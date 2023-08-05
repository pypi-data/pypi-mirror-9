from __future__ import absolute_import, print_function
import os
import sys
import json
import errno
import socket
import signal
import logging
import logging.config
import threading
import traceback
import multiprocessing
from time import sleep

from setproctitle import setproctitle

from kuyruk import importer, signals
from kuyruk.task import get_queue_name
from kuyruk.exceptions import Reject, Discard, ConnectionError

logger = logging.getLogger(__name__)


class Worker(object):
    """Consumes tasks from a queue and runs them.

    :param app: An instance of :class:`~kuyruk.Kuyruk`
    :param args: Command line arguments

    """
    def __init__(self, app, args):
        self.kuyruk = app

        if not args.queue:
            raise ValueError("empty queue name")
        self.queue = get_queue_name(args.queue, local=args.local)

        self.shutdown_pending = threading.Event()
        self._pause = False
        self._started = None
        self.consuming = False
        self._current_message = None
        self.current_task = None
        self.current_args = None
        self.current_kwargs = None
        self._heartbeat_exc_info = None
        if self.config.WORKER_MAX_LOAD is None:
            self.config.WORKER_MAX_LOAD = multiprocessing.cpu_count()

        signals.worker_init.send(self.kuyruk, worker=self)

    @property
    def config(self):
        return self.kuyruk.config

    def run(self):
        """Runs the worker and consumes messages from RabbitMQ.
        Returns only after `shutdown()` is called.

        """
        setproctitle("kuyruk: worker on %s" % self.queue)

        self._setup_logging()

        signal.signal(signal.SIGINT, self._handle_sigint)
        signal.signal(signal.SIGTERM, self._handle_sigterm)
        signal.signal(signal.SIGHUP, self._handle_sighup)
        signal.signal(signal.SIGUSR1, self._handle_sigusr1)
        signal.signal(signal.SIGUSR2, self._handle_sigusr2)

        self._started = os.times()[4]

        for f in (self._watch_load, self._shutdown_timer):
            t = threading.Thread(target=f)
            t.daemon = True
            t.start()

        signals.worker_start.send(self.kuyruk, worker=self)
        self._consume_messages()
        signals.worker_shutdown.send(self.kuyruk, worker=self)

        logger.debug("End run worker")

    def _setup_logging(self):
        if self.config.WORKER_LOGGING_CONFIG:
            logging.config.fileConfig(self.config.WORKER_LOGGING_CONFIG)
        else:
            logging.getLogger('rabbitpy').level = logging.WARNING
            level = getattr(logging, self.config.WORKER_LOGGING_LEVEL.upper())
            fmt = "%(levelname).1s " \
                  "%(name)s.%(funcName)s:%(lineno)d - %(message)s"
            logging.basicConfig(level=level, format=fmt)

    def _consume_messages(self):
        with self.kuyruk.channel() as ch:
            ch.queue_declare(
                queue=self.queue, durable=True, auto_delete=False)

            # Set prefetch count to 1. If we don't set this, RabbitMQ keeps
            # sending messages while we are already working on a message.
            ch.basic_qos(0, 1, False)

            consumer_tag = '%s@%s' % (os.getpid(), socket.gethostname())
            while not self.shutdown_pending.is_set():
                # Consume or pause
                if self._pause and self.consuming:
                    ch.basic_cancel(consumer_tag)
                    logger.info('Consumer cancelled')
                    self.consuming = False
                elif not self._pause and not self.consuming:
                    ch.basic_consume(queue=self.queue,
                                     consumer_tag=consumer_tag,
                                     callback=self._process_message)
                    logger.info('Consumer started')
                    self.consuming = True

                if self._heartbeat_exc_info:
                    break

                try:
                    ch.connection.drain_events(timeout=0.1)
                    ch.connection.heartbeat_tick()
                except socket.error as e:
                    if isinstance(e, socket.timeout):
                        pass
                    elif e.errno == errno.EINTR:
                        pass  # happens when the process receives a signal
                    else:
                        raise
        logger.debug("End run worker")

    def _process_message(self, message):
        """Processes the message received from the queue."""
        try:
            description = json.loads(message.body)
        except Exception:
            message.channel.basic_reject(message.delivery_tag, requeue=False)
            logger.error("Cannot decode message. Dropping.")
        else:
            logger.info("Processing task: %r", description)
            self._process_description(message, description)

    def _process_description(self, message, description):
        try:
            task = importer.import_object(description['module'],
                                          description['function'])
            args, kwargs = description['args'], description['kwargs']
        except Exception:
            logger.error('Cannot import task')
            exc_info = sys.exc_info()
            signals.worker_failure.send(self.kuyruk, description=description,
                                        exc_info=exc_info, worker=self)
            message.channel.basic_reject(message.delivery_tag, requeue=False)
        else:
            self._process_task(message, description, task, args, kwargs)

    def _process_task(self, message, description, task, args, kwargs):
        try:
            self._current_message = message
            self.current_task = task
            self.current_args = args
            self.current_kwargs = kwargs
            stop_heartbeat = threading.Event()
            heartbeat_thread = threading.Thread(
                target=self._heartbeat_tick,
                args=(message.channel.connection, stop_heartbeat))
            heartbeat_thread.start()
            try:
                task.apply(*args, **kwargs)
            finally:
                self._current_message = None
                self.current_task = None
                self.current_args = None
                self.current_kwargs = None
                stop_heartbeat.set()
                heartbeat_thread.join()
        except Reject:
            logger.warning('Task is rejected')
            sleep(1)  # Prevent cpu burning
            message.channel.basic_reject(message.delivery_tag, requeue=True)
        except Discard:
            logger.warning('Task is discarded')
            message.channel.basic_reject(message.delivery_tag, requeue=False)
        except ConnectionError:
            pass
        except Exception:
            logger.error('Task raised an exception')
            exc_info = sys.exc_info()
            logger.error(''.join(traceback.format_exception(*exc_info)))
            signals.worker_failure.send(self.kuyruk, description=description,
                                        task=task, args=args, kwargs=kwargs,
                                        exc_info=exc_info, worker=self)
            message.channel.basic_reject(message.delivery_tag, requeue=False)
        else:
            logger.info('Task is successful')
            message.channel.basic_ack(message.delivery_tag)
        finally:
            logger.debug("Task is processed")

    def _watch_load(self):
        """Pause consuming messages if lood goes above the allowed limit."""
        while not self.shutdown_pending.is_set():
            load = os.getloadavg()[0]
            if load > self.config.WORKER_MAX_LOAD:
                if self._pause is False:
                    logger.warning(
                        'Load is above the treshold (%.2f/%s), '
                        'pausing consumer', load, self.config.WORKER_MAX_LOAD)
                    self._pause = True
            else:
                if self._pause is True:
                    logger.warning(
                        'Load is below the treshold (%.2f/%s), '
                        'resuming consumer', load, self.config.WORKER_MAX_LOAD)
                    self._pause = False
            sleep(1)

    @property
    def uptime(self):
        if self._started is not None:
            return os.times()[4] - self._started

    def _shutdown_timer(self):
        """Counts down from MAX_WORKER_RUN_TIME. When it reaches zero sutdown
        gracefully.

        """
        if not self.config.WORKER_MAX_RUN_TIME:
            return

        while not self.shutdown_pending.is_set():
            remaining = self.config.WORKER_MAX_RUN_TIME - self.uptime
            if remaining > 0:
                sleep(remaining)
            else:
                logger.warning('Run time reached zero')
                self.shutdown()
                break

    def shutdown(self):
        """Exits after the current task is finished."""
        logger.warning("Shutdown requested")
        self.shutdown_pending.set()

    def _handle_sigint(self, signum, frame):
        """Shutdown after processing current task."""
        logger.warning("Catched SIGINT")
        self.shutdown()

    def _handle_sigterm(self, signum, frame):
        """Shutdown after processing current task."""
        logger.warning("Catched SIGTERM")
        self.shutdown()

    def _handle_sighup(self, signum, frame):
        logger.warning("Catched SIGHUP")
        raise ConnectionError(self._heartbeat_exc_info)

    def _handle_sigusr1(self, signum, frame):
        """Print stacktrace."""
        print('=' * 70)
        print(''.join(traceback.format_stack()))
        print('-' * 70)

    def _handle_sigusr2(self, signum, frame):
        """Drop current task."""
        logger.warning("Catched SIGQUIT")
        if self._current_message:
            logger.warning("Dropping current task...")
            raise Discard

    def drop_task(self):
        os.kill(os.getpid(), signal.SIGUSR2)

    def _heartbeat_tick(self, connection, stop_event):
        while not stop_event.is_set():
            try:
                connection.drain_events(timeout=0.1)
                connection.heartbeat_tick()
            except socket.timeout:
                pass
            except Exception as e:
                logger.error(e)
                self._heartbeat_exc_info = sys.exc_info()
                os.kill(os.getpid(), signal.SIGHUP)
                break
