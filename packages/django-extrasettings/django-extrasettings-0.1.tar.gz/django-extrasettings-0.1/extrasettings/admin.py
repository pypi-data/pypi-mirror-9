from django.contrib           import admin

from extrasettings.models import Extrasetting

class ExtrasettingAdmin(admin.ModelAdmin):
    fields        = ('settings', 'schema')

    class Media:
        css = {
            'all': ('extrasettings/css/bootstrap-3.css',)
        }
        js  = ('extrasettings/js/jQuery.js', 'extrasettings/js/jsoneditor.min.js', 'extrasettings/js/settings-edit.js')

admin.site.register(Extrasetting, ExtrasettingAdmin)

