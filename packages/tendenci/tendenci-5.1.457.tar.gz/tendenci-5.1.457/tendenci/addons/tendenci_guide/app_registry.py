from tendenci.core.registry import site
from tendenci.core.registry.base import LogRegistry, lazy_reverse
from tendenci.addons.tendenci_guide.models import Guide

class GuideRegistry(LogRegistry):
    event_logs = {
        'tendenci_guide':{
            'edit':('1002000', 'A20900'), # base
            'add':('1002100', '119933'), # add
            'edit':('1002200', 'EEDD55'), # edit
            'delete':('1002300', 'AA2222'), # delete
            'search':('1002400', 'CC55EE'), # search
            'detail':('1002500', '55AACC'), # detail
        }
    }

site.register(Guide, GuideRegistry)
