
Browserify filter for webassets
--------------------

Filter for for compiling assets using Browserify[1] and webassets[2].

Basic usage
`````

.. code:: python

    from webassets.filter import register_filter
    from webassets_browserify import Browserify

    register_filter(Browserify)


Usage with Django
`````

This requires django-assets[3].

.. code:: python

    from django_assets import Bundle, register
    from webassets.filter import register_filter
    from webassets_browserify import Browserify

    register_filter(Browserify)

    js = Bundle('js/main.js', filters='browserify', output='bundle.js',
                depends='js/**/*.js')
    register('js_all', js)


Links
`````

[1] http://browserify.org
[2] http://webassets.readthedocs.org
[3] http://django-assets.readthedocs.org



