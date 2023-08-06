Django Simple Plugins
=====================

Django Simple Plugins is an app for Django that provides a simple yet
flexible system to add a plugin layer to your project. Works with Django
1.7

Installation
~~~~~~~~~~~~

Install Django plugins with pip:

.. code:: sh

    pip install django-simple-plugins

Add 'plugins' to the list of installed apps in your ``settings.py``
file:

.. code:: python

    ...
    'plugins',
    ...

Add a ``PLUGINS_DIR`` setting to your ``settings.py`` with the directory
where you are going to store your plugins. For instance:

.. code:: python

    ...
    PLUGINS_DIR = os.path.join(BASE_DIR, 'my_plugins')
    ...

Add the plugins urls to your ``urls.py`` file:

.. code:: python

    ...
    urlpatterns = patterns('',
        url(r'^admin/', include(admin.site.urls)),
        url(r'^plugins/', include('plugins.urls')),
    )
    ...

Execute ``./manage.py migrate``

Writing your first plugins
~~~~~~~~~~~~~~~~~~~~~~~~~~

As a very simple example, imagine that we want to delegate the "greet
user" functionality to a plugin system. You want something a bit fancier
than this:

.. code:: python

    def greet(request):
        greeting = 'Hello ' + request.user.username
        return HttpResponse(greeting)

For example, based on who the user is, you want a greeting like "Hello
mighty Superman" or "Hello mighty, super Batman".

.. code:: python

    import plugins

    def greet(request):
        adjectives = plugins.execute_plugins(type='GREETING', context={
            'username': request.user.username
        }, initial_input=[])
        greeting = 'Hello %s %s' % (', '.join(adjectives), request.user.username)
        return HttpResponse(greeting)

We want to define a series of plugins of type "GREETING" that return a
list of adjective based on a context that provides the username.

Let's write the first plugin. In the directory defined by
``PLUGINS_DIR`` add the file ``greeter_plugin_1.py`` with this content:

.. code:: python

    plugin_type = 'GREETING'
    verbose_name = 'Greeting plugin 1 - Mighty'

    def run(options, context, input):
        if context['username'] in options['mighty_users']:
            input += 'mighty'

        return input

Each plugin *must* define a ``plugin_type`` and a ``run()`` function.
They *can* define a ``verbose_name`` Each run function is pass the
options passed by the configuration (see below), an optional context and
an input. Since the plugins are executed in a chained fashion, the first
plugin to be executed is passed the ``initial_input`` (in our case
``[]``) or ``None``. The subsequent plugins are passed the return value
of the previous plugins.

Let's write the others:

.. code:: python

    # greeter_plugin_2.py
    plugin_type = 'GREETING'
    verbose_name = 'Greeting plugin 2 - Super'

    def run(options, context, input):
        if context['username'] in options['super_users']:
            input += 'super'

        return input

.. code:: python

    # greeter_plugin_3.py
    plugin_type = 'GREETING'

    def run(options, context, input):
        if context['username'] in options['stinky_users']:
            input += 'stinky'

        return input

.. code:: python

    # goodbye_plugin_1.py
    plugin_type = 'GOODBYE'

    def run(options, context, input):
        pass

Visiting the admin page, we have a list of our plugins conveniently
grouped by plugin type.

.. figure:: http://i.imgur.com/fVG7WZe.png
   :alt: Screenshot 1

   Screenshot 1
Three things to notice. We don't want to insult our users, so we can
disable the third plugin and it will be skipped. If you don't provide a
``verbose_name``, the file name will be used (see ``greeter_plugin_3``).
Finally, the plugins are *sortable*. You can drag them to arrange the
order of execution. For example, If you'd like to have "super, mighly
Batman" instead of "mighty, super batman", just drag the Super plugin
before the other:

.. figure:: http://i.imgur.com/9lcG8Eb.png
   :alt: Screenshot 2

   Screenshot 2
We only have one last thing to do. As you might have noticed, we read
some parameter from the ``options`` dictionary. In the admin interface
you can specify a JSON string that will be passed as a dictionary to the
plugin. For instance:

.. figure:: http://i.imgur.com/8Z8x9YT.png
   :alt: Screenshot 2

   Screenshot 2

