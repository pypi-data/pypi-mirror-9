Django Markdown Content Manager
===============================

DMCM is a Django 1.8 app which implements a content management
system where every item is a page and all the content is written
in Markdown.


Quick start
-----------

1. Add "dmcm" to your ``INSTALLED_APPS`` settings.

2. The DMCM pages are orgaised in a tree structure. A default root page
   called "Root" will be created. Add ``SITE_ROOT_SLUG`` to ``settings``::

     SITE_ROOT_SLUG = 'home'  # Homepage

3. Include the feedreader URLconf in your project urls.py like this::

     url(r'^dmcm/', include('dmcm.urls', namespace='dmcm')),

4. Run ``python manage.py syncdb`` to create the dmcm models.

5. Run ``python manage.py collectstatic`` to copy static files to your
   project's static root.

6. Visit ``/dmcm/`` on your site to see a default home page in DMCM.

   Visit ``/dmcm/dmcm/edit/`` to see a list of all DMCM pages and to add more.

   Editing in DMCM requires that Django login be enabled.

Dependencies
------------

-  `Django 1.8 <https://pypi.python.org/pypi/Django/1.8>`__
-  `django-braces 1.4.0 <https://pypi.python.org/pypi/django-braces/1.4.0>`__
-  `factory_boy 2.5.1 <https://pypi.python.org/pypi/factory_boy/2.5.1>`__
-  `Markdown 2.6.1 <https://pypi.python.org/pypi/Markdown/2.6.1>`__

