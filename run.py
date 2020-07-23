# -*- coding: utf-8 -*-
import eventlet
import inspect
import six
from nameko.exceptions import CommandError
from nameko.extensions import ENTRYPOINT_EXTENSIONS_ATTR
from werkzeug.utils import find_modules, import_string

eventlet.monkey_patch()  # noqa (code before rest of imports)

import errno
import logging.config
import signal
from nameko.runners import ServiceRunner


def is_type(obj):
    return isinstance(obj, six.class_types)


def is_entrypoint(method):
    return hasattr(method, ENTRYPOINT_EXTENSIONS_ATTR)


config = {
    'AMQP_URI': 'pyamqp://guest:guest@172.30.1.224',
    'rpc_exchange': 'nameko-rpc',
    'max_workers': 20,
    'parent_calls_tracked': 20,
    'LOGGING': {
        'version': 1,
        # 'disable_existing_loggers': False,
        'formatters': {
            'normal': {
                'format': '%(name)s %(asctime)s %(levelname)s %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            },
            'raw': {
                'format': '%(message)s',
            },
        },
        'handlers': {
            'console': {
                'formatter': 'normal',
                'class': 'logging.StreamHandler',
                'stream': 'ext://sys.stdout'
            },
        },
        "loggers": {
            "nameko.messaging": {
                "level": "DEBUG",
                "handlers": ["console"],
                "propagate": False
            }
        },
        'root': {
            'level': 'INFO',
            'handlers': ['console', ]
        }
    }
}

if "LOGGING" in config:
    logging.config.dictConfig(config['LOGGING'])
else:
    logging.basicConfig(level=logging.INFO, format='%(message)s')

# create a runner for ServiceA and ServiceB
runner = ServiceRunner(config=config)


# from services import GreetingService, AnotherService

# runner.add_service(GreetingService)
# runner.add_service(AnotherService)
def register_services(r, package):
    found_services = []
    for module_name in find_modules(package):
        module = import_string(module_name)
        print(module, module_name)
        for _, potential_service in inspect.getmembers(module, is_type):
            if inspect.getmembers(potential_service, is_entrypoint):
                found_services.append(potential_service)
                r.add_service(potential_service)
    if not found_services:
        raise CommandError(
            "Failed to find anything that looks like a service in package "
            "{!r}".format(package)
        )


register_services(runner, 'services')


def shutdown(signum, frame):
    # signal handlers are run by the MAINLOOP and cannot use eventlet
    # primitives, so we have to call `stop` in a greenlet
    eventlet.spawn_n(runner.stop)


signal.signal(signal.SIGTERM, shutdown)
logger = logging.getLogger(__name__)
# start both services
runner.start()
runnlet = eventlet.spawn(runner.wait)
while True:
    try:
        runnlet.wait()
    except OSError as exc:
        if exc.errno == errno.EINTR:
            # this is the OSError(4) caused by the signalhandler.
            # ignore and go back to waiting on the runner
            continue
        raise
    except KeyboardInterrupt:
        print()  # looks nicer with the ^C e.g. bash prints in the terminal
        try:
            runner.stop()
        except KeyboardInterrupt:
            print()  # as above
            runner.kill()
    else:
        # runner.wait completed
        break
# # stop both services
# # runner.stop()
