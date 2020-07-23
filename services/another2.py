# -*- coding: utf-8 -*-
from nameko.rpc import rpc
from nameko.events import event_handler, BROADCAST, SINGLETON, SERVICE_POOL
import time
from dependencies import LoggingDependency


class Another2Service:
    name = "another2"  # 自定义服务名称
    log = LoggingDependency()

    @rpc  # 入口点标记
    def hello(self, name):
        # sleep(5)
        return "Hello, {}!".format(name)

    @event_handler("greeting_service", "event_type")
    def abort(self, n):
        print("Hello, {}!".format(n), self.name)
        return "Hello, {}!".format(n)


class Another3Service:
    name = "another3"  # 自定义服务名称
    log = LoggingDependency()

    @rpc  # 入口点标记
    def hello(self, name):
        # sleep(5)
        return "Hello, {}!".format(name)

    # @event_handler("greeting_service", "event_type", handler_type=SINGLETON, reliable_delivery=False)
    @event_handler("greeting_service", "event_type")
    def abort(self, n):
        print("Hello, {}!".format(n), self.name)
        return "Hello, {}!".format(n)
