﻿=====
Restart
=====

Restart is a simple Django app to allow administrators to restart the 
application by touching the wsgi file.

Quick start
-----------

1. Add "restart" to your INSTALLED_APPS settings.  For example::

    INSTALLED_APPS = (
        ...
        'restart',
        'admin_shortcuts',          # An optional package, not required
        'djangocms_admin_style',    # An optional package, not required
        'django.contrib.admin',
    )


2. Add 'restart.Loader' to your TEMPLATE_LOADERS in your settings file::

    TEMPLATE_LOADERS = (
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
        'restart.Loader',
        # 'django.template.loaders.eggs.Loader',
    )

3. Setup the name of your wsgi file in your settings, for example::
    
    WSGI_NAME = "django.wsgi"


4. This app also uses the SITE_ROOT variable.  If this is not defined it will attempt to guess the site-root, however it is recommended that this is defined. It should be the folder which contains your wsgi file.


5. Run `python manage.py syncdb` to create the restart model.


6. Run `python manage.py collectstatic` to collect the required static files.


7. When accessing the admin, you should now see a small arrow on the bottom right of your window at all times.  Clicking on this will show the server uptime based on the wsgi file, and allow restarting via touch.


Django Suit
---------------------
If using Django-suit, create a new (or edit your existing) admin/base.html file in your templates with the following code::

    {% extends "suit:admin/base.html" %}

    {% block extrahead %}{% include 'admin/inc/extrahead.html' %}{% endblock %}
    
Django Admin tools
---------------------
If using Django admin tools, create a new (or edit your existing) admin/base.html file in your templates with the following code::

    {% extends "admin_tools.theming:admin/base.html" %}

    {% block extrahead %}{% include 'admin/inc/extrahead.html' %}{% endblock %}


Custom base template
---------------------
If you have a custom admin/base.html file or you want to install manually, you can skip step 2 above, and replace the line::
    
    {% block extrahead %}{% endblock %}

with::

    {% block extrahead %}{% include 'admin/inc/extrahead.html' %}{% endblock %}


Tested with
---------------------
- Django 1.6
- Django CMS 3.0rc1
- Django base admin styles
- Django CMS Admin styles (optional)
- Django CMS Admin styles (optional)
- Django Admin shortcuts (optional)
- Reversion (tested with 1.8.0, optional)

Requires
---------------------
This app should work with verisons of Django below 1.6, it has been tested down to 1.3.  No other packages should be required.


Todo
---------------------
- Ensure works with grapelli, django-suit and other admin alternative templates.
- Tests

Other
---------------------
The template loader code is based on: http://djangosnippets.org/snippets/1376/
