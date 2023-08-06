Butter CMS for Django
=========================

https://www.buttercms.com

**Why Butter?**

Butter makes setting up a company blog on Django insanely easy. It's built for Django developers to save us from hosting, DB setup, themeing, maintaining yet another Wordpress install. It's designed to be quickly integrated to an existing Django project.

Butter provides a marketing friendly blogging UI, hosted on buttercms.com, and exposes content created via an API.

This package provides a thin wrapper that interacts with the Butter API and a quick start blog application.


Installation
------------
.. code-block:: bash

    $ pip install buttercms-django

Add buttercms entry to INSTALLED_APPS in settings.py:

.. code-block:: python

    INSTALLED_APPS = (
        ...
        'buttercms',
    )

Add your new blog path to urls.py:

.. code-block:: python

    urlpatterns = patterns('',
        ...
        url(r'^blog/', include(butter.urls)),
    )

Nice job. You've now got a fully functioning blog, running natively in your Django project. (Yay, no PHP scripts.)

Next Steps
-------------
Visit localhost:8000/blog to check out the blog.

We've provided a default theme but we expect you'll want skin it with your branding so we've made this as simple as extending your base template.

TODO Template instructions.

