import json
from django.db              import models
from django.core.validators import RegexValidator

import extrasettings

class Extrasetting(models.Model):
    name = models.CharField(max_length=50, validators = [
        RegexValidator('^[a-zA-Z_][a-zA-Z0-9_]*$',
            message = 'Extra setting names can only contain letters, numbers (not as first chat) and underscores',
            code    = 'invalid_name'
        ),
    ])
    settings = models.TextField(default="{}")
    schema   = models.TextField(default="{}")

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        setattr(extrasettings, self.name, json.loads(self.settings))
        super(Extrasetting, self).save(*args, **kwargs)

# Create your models here.
