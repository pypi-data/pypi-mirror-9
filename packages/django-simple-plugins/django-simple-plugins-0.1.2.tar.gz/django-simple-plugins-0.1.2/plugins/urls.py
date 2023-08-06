from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^jsconfig/',             'plugins.views.js_config',            name='plugins_js_config'),
    url(r'^update_plugins_order/', 'plugins.views.update_plugins_order', name='plugins_update_plugins_order'),
)
