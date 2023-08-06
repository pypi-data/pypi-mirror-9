import logging
import yagi.commandline
from yagi.consumer import Consumer
import yagi.event_worker

LOG = logging.getLogger(__name__)

consumers = []


def create_consumer(queue_name, app=None, config=None):
    consumer = Consumer(queue_name, app, config)
    consumers.append(consumer)


def setup_consumers():
    qs = [q.strip() for q in yagi.config.get('consumers', 'queues').split(',')]
    for q in qs:
        create_consumer(q)


def start_consumers():
    if yagi.config.get('event_worker', 'daemonize') == 'True':
        import daemon
        context = daemon.DaemonContext()
        LOG.info('Starting Event Worker daemon')
        context.pidfile = yagi.config.get('event_worker', 'pidfile')
        context.open()
    yagi.event_worker.start(consumers)
