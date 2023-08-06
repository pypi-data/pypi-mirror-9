import os
import plugins

from django.conf     import settings
from django.apps     import AppConfig
from django.db.utils import OperationalError

from plugins.models import PluginConfiguration

import types

plugin_list = {}

class PluginsConfig(AppConfig):
    name         = 'plugins'
    verbose_name = "Django Plugins"

    def ready(self):
        try:
            if not settings.PLUGINS_DIR:
                raise Exception('django-plugins: PLUGINS_DIR required in settings.py')

            # Configure plugins
            plugin_names = [os.path.splitext(d)[0] for d in os.listdir(settings.PLUGINS_DIR) if os.path.splitext(d)[1] == '.py']

            # for plugin_dir in plugin_dirs:
            #     plugin_obj, created = PluginConfiguration.objects.get_or_create(name=plugin_dir)

            # Remove from the database the plugins no longer in PLUGIN_DIR
            for plugin_obj in PluginConfiguration.objects.all():
                if plugin_obj.name not in plugin_names:
                    plugin_obj.delete()

            for plugin_name in plugin_names:
                filename = os.path.join(settings.PLUGINS_DIR, plugin_name + '.py')

                # Dinamically load the plugin
                with open(filename) as fp:
                    code = compile(fp.read(), filename, "exec")

                plugin_code = types.ModuleType("<plugins>")
                exec code in plugin_code.__dict__

                # Check plugin validity
                if not hasattr(plugin_code, 'plugin_type'):
                    raise Exception('django-plugins: plugin "%s" does not have a plugin_type' % plugin_name)

                if not hasattr(plugin_code, 'run'):
                    raise Exception('django-plugins: plugin "%s" does not have a run function' % plugin_name)

                plugins.plugin_list[plugin_name] = plugin_code

                # Save or update the plugin in the database
                plugin_obj, created = PluginConfiguration.objects.update_or_create(name=plugin_name, defaults= {
                    'verbose_name': plugin_code.verbose_name if hasattr(plugin_code, 'verbose_name') else None,
                    'plugin_type' : plugin_code.plugin_type
                })
        except OperationalError:
            pass
        except Exception as ex:
            raise ex


