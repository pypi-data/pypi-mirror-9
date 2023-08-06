import os
import simplejson as json

from django.conf import settings as django_settings
from django.core.management.base import BaseCommand, CommandError

from tendenci.core.site_settings.models import Setting


class Command(BaseCommand):
    """
    Update site settings in the database to not be client editable.
    This was initially build to hide theme settings when switching themes.
    """
    help = 'Hide settings (client_editable = false) in the site_settings_setting table'

    def handle(self, scope_category, **options):
        try:
            verbosity = int(options['verbosity'])
        except:
            verbosity = 1

        if scope_category:
            settings = Setting.objects.filter(scope_category=scope_category)

            required_keys = [
                'scope',
                'scope_category',
                'name'
            ]
            for setting in settings:
                try:
                    current_setting = Setting.objects.get(
                        name=setting.name,
                        scope=setting.scope,
                        scope_category=setting.scope_category
                    )
                except:
                    current_setting = None
                print current_setting
                # update the setting
                if (current_setting):
                    current_setting.client_editable = False
                    current_setting.save()
                    print '%s (%s)  - hidden.' % (
                        setting.name,
                        setting.scope_category
                    )
