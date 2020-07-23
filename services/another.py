# -*- coding: utf-8 -*-
from nameko.rpc import rpc
from nameko.events import event_handler
import time
from dependencies import LoggingDependency


class AnotherService:
    name = "another"  # 自定义服务名称
    log = LoggingDependency()

    @rpc  # 入口点标记
    def hello(self, name):
        # sleep(5)
        return "Hello, {}!".format(name)

    @event_handler("greeting_service", "event_type")
    def abort(self, n):
        print("Hello, {}!".format(n), self.name)
        return "Hello, {}!".format(n)


class Ano:
    name = 'not rpc'

    def hello(self):
        pass
