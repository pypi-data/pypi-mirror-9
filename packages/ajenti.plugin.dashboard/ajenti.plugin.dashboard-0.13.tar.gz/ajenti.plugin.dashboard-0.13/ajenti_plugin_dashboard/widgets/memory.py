import psutil

from aj.api import *
from aj.plugins.dashboard.api import Widget


@component(Widget)
class MemoryWidget(Widget):
    id = 'memory'
    name = 'Memory usage'
    template = '/dashboard:resources/partial/widgets/memory.html'

    def __init__(self, context):
        Widget.__init__(self, context)

    def get_value(self, config):
        v = psutil.virtual_memory()
        return {
            'used': v.total - v.available,
            'free': v.available,
            'total': v.total
        }
