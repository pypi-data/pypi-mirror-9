from django.conf.urls         import patterns
from django.contrib           import admin
from django.http              import HttpResponse
from django.core.urlresolvers import reverse_lazy

from plugins.models import PluginConfiguration

class PluginConfigurationAdmin(admin.ModelAdmin):
    fields        = ('options', 'enabled')
    list_display  = ('__unicode__', 'plugin_type', 'order', 'enabled')
    list_editable = ('enabled',)

    class Media:
        css = {
            'all': ('plugins/css/codemirror.css',)
        }
        js  = ('plugins/js/jQuery.js', 'plugins/js/jQuery-ui.js', 'plugins/js/codemirror.js', reverse_lazy('plugins_js_config'), 'plugins/js/plugins_list.js')

admin.site.register(PluginConfiguration, PluginConfigurationAdmin)

