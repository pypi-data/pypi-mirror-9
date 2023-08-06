Browserify filter for webassets
-------------------------------

Filter for for compiling assets using `Browserify <http://browserify.org>`_ and
`webassets <http://webassets.readthedocs.org>`_.

Basic usage
```````````

.. code:: python

    from webassets.filter import register_filter
    from webassets_browserify import Browserify

    register_filter(Browserify)


Usage with Django
`````````````````

This requires `django-assets <http://django-assets.readthedocs.org>`_.

.. code:: python

    from django_assets import Bundle, register
    from webassets.filter import register_filter
    from webassets_browserify import Browserify

    register_filter(Browserify)

    js = Bundle('js/main.js', filters='browserify', output='bundle.js',
                depends='js/**/*.js')
    register('js_all', js)



