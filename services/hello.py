from nameko.rpc import rpc
from nameko.events import EventDispatcher
import time
from dependencies import LoggingDependency


class GreetingService:
    name = "greeting_service"  # 自定义服务名称
    log = LoggingDependency()

    dispatch = EventDispatcher()

    @rpc  # 入口点标记
    def hello(self, name):
        # sleep(5)
        return "Hello, {}!".format(name)

    @rpc
    def abort(self):
        raise Exception()

    @rpc
    def hello_nb(self, name):
        self.dispatch("event_type", name)
        return "Hello, {}!".format(name)
