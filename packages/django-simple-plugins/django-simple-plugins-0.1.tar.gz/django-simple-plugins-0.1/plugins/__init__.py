import json
from plugins.models import PluginConfiguration

default_app_config = 'plugins.apps.PluginsConfig'

plugin_list = {}

def execute_plugins(type, context={}, initial_input=None):
    plugins_to_execute = PluginConfiguration.objects.filter(plugin_type=type, enabled=True).order_by('order')

    output = initial_input

    for plugin in plugins_to_execute:
        output = plugin_list[plugin.name].run(json.loads(plugin.options), context, output)

    return output
