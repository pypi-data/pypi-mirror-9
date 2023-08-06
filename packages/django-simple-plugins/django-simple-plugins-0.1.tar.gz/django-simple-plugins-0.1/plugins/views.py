import json

from django.shortcuts import render
from django.http import HttpResponse
from django.core.urlresolvers import reverse

from plugins.models import PluginConfiguration

def update_plugins_order(request):
    for plugin in json.loads(request.POST['data']):
        plugin_obj = PluginConfiguration.objects.get(pk=plugin['id'])
        plugin_obj.order = plugin['order']
        plugin_obj.save()

    return HttpResponse(json.dumps({}), content_type="application/json")

def js_config(request):
    return HttpResponse('window.update_plugins_order = "%s"' % reverse('plugins_update_plugins_order'), content_type="text/javascript")
