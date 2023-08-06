from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from tendenci.core.registry import site
from tendenci.core.registry.base import CoreRegistry, lazy_reverse
from tendenci.core.newsletters.models import Newsletter


class NewsletterRegistry(CoreRegistry):
    version = '1.0'
    author = _('Schipul - The Web Marketing Company')
    author_email = 'programmers@schipul.com'
    description = _('Create newsletter')

    event_logs = {
        'newsletter':{
            'add': ('136000','DD3300'),
            'edit': ('136100', 'DD3311'),
            'detail': ('136200', 'DD3322'),
            'send': ('136300', 'DD3333'),
            'resend': ('136400', 'DD3344')
        }
    }
    url = {
        'add': lazy_reverse('newsletter.orig.generator'),
        'search': lazy_reverse('newsletter.list'),
    }

site.register(Newsletter, NewsletterRegistry)
