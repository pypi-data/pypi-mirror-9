import os
import re
import json
import extrasettings

from django.conf     import settings
from django.apps     import AppConfig
from django.db.utils import OperationalError

from extrasettings.models import Extrasetting

class ExtrasettingsConfig(AppConfig):
    name         = 'extrasettings'
    verbose_name = "Django Extrasettings"

    def ready(self):
        try:
            if not settings.EXTRASETTINGS_DIR:
                raise Exception('django-extrasettings: EXTRASETTINGS_DIR required in settings.py')

            # Configure settings
            settings_names = [os.path.splitext(d)[0] for d in os.listdir(settings.EXTRASETTINGS_DIR) if os.path.splitext(d)[1] == '.json']

            # Remove from the database the plugins no longer in PLUGIN_DIR
            for settings_obj in Extrasetting.objects.all():
                if settings_obj.name not in settings_names:
                    settings_obj.delete()

            for setting_name in settings_names:
                if not re.match('^[a-zA-Z_][a-zA-Z0-9_]*$', setting_name):
                    raise Exception('django-extrasettings: %s.json is not a valid filename. Use only letters, underscores and numbers (no numbers as first char)' % setting_name)

                filename = os.path.join(settings.EXTRASETTINGS_DIR, setting_name + '.json')

                try:
                    schema = json.load(open(filename))
                except ValueError:
                    raise Exception('django-extrasettings: %s.json is not a valid JSON file' % setting_name)

                settings_obj, created = Extrasetting.objects.update_or_create(name=setting_name, defaults= {
                    'schema': json.dumps(schema)
                })

                setattr(extrasettings, setting_name, json.loads(settings_obj.settings))

        except OperationalError:
            pass
        except Exception as ex:
            raise ex

