`|Build Status| <https://travis-ci.org/mbraak/django-mptt-admin>`_
`|Version| <https://pypi.python.org/pypi/django-mptt-admin/>`_
`|Development
Status| <https://pypi.python.org/pypi/django-mptt-admin/>`_

`|Coverage
Status| <https://coveralls.io/r/mbraak/django-mptt-admin?branch=master>`_
`|Downloads| <https://pypi.python.org/pypi/django-mptt-admin/>`_
`|Format| <https://pypi.python.org/pypi/django-mptt-admin/>`_
`|Requirements
Status| <https://requires.io/github/mbraak/django-mptt-admin/requirements/?branch=master>`_

`|License| <https://pypi.python.org/pypi/django-mptt-admin/>`_
`|Supported Python
versions| <https://pypi.python.org/pypi/django-mptt-admin/>`_
`|Supported Python
implementations| <https://pypi.python.org/pypi/django-mptt-admin/>`_

Django Mptt Admin
=================

*Django-mptt-admin* provides a nice Django Admin interface for
`django-mptt models <http://django-mptt.github.io/django-mptt/>`_. The
source is available on
`https://github.com/mbraak/django-mptt-admin <https://github.com/mbraak/django-mptt-admin>`_.
It uses the `jqTree <http://mbraak.github.io/jqTree/>`_ library.

.. figure:: https://raw.github.com/mbraak/django-mptt-admin/master/screenshot.png
   :align: center
   :alt: Screenshot

   Screenshot
Requirements
------------

The package is tested with Django (1.4 - 1.7), and django-mptt (0.6.0,
0.6.1). Also with Python 2.6, 2.7, 3.3 and 3.4.

Installation
------------

Install the package:

::

    $ pip install django_mptt_admin

Add **django\_mptt\_admin** to your installed apps in **settings.py**.

::

      INSTALLED_APPS = (
          ..
          'django_mptt_admin',
      )

Use the DjangoMpttAdmin class in admin.py:

::

        from django.contrib import admin
        from django_mptt_admin.admin import DjangoMpttAdmin
        from models import Country

        class CountryAdmin(DjangoMpttAdmin):
            pass

        admin.site.register(Country, CountryAdmin)

Options
-------

**tree\_auto\_open**

Auto-open node. Default value is 1.

Values: \* **True**: autopen all nodes \* **False**: do not autoopen \*
**integer**: autopen until this level

**tree\_load\_on\_demand**

Load on demand (True / False / level). Default is True.

-  **True**: load nodes on demand
-  **False**: do not load nodes on demand
-  **int**: load nodes on demand until this level

**autoescape**

Autoescape (True / False). Default is True.

Autoescape titles in tree.

**filter\_tree\_queryset**

Override the **filter\_tree\_queryset** method to filter the queyset for
the tree.

::

    class CountryAdmin(DjangoMpttAdmin):
      def filter_tree_queryset(self, queryset):
        return queryset.filter(name='abc')

Changelog
---------

\*\*0.2.0 (january 12 2015) \*\*

-  Issue 23: fixed save-state for load-on-demand
-  Issue 35: fixed auto-open for load-on-demand
-  Issue 40: use jqtree 1.0.0
-  Issue 45: added i18n support and Hebrew translation (thanks to Udi
   Oron)
-  Issue 47: added filter\_tree\_queryset method

**0.1.10** (september 24 2014)

-  Issue 31: added autoescape option
-  Issue 34: use the default change list in popup mode (thanks to
   hstanev)
-  Issue 36: the option tree\_load\_on\_demand = False does not work

**0.1.9** (july 12 2014)

-  Issue 25: update jqtree to 0.21.0
-  Issue 28: fixing problems related to working with model's pk-field,
   named other than "id" (thanks to Igor Gai)
-  Issue 29: fix path to spinner.gif (thanks to Igor Gai)

**0.1.8** (februari 2 2014)

-  Issue 17: handle error when moving node
-  Issue 18: do not use inline javascript
-  Issue 19: support Django 1.7 alpha

**0.1.7** (january 3 2014)

-  Issue 16: moving a node fails if the node id is a uuid

**0.1.6** (october 10 2013)

-  Issue 8: removing node from the tree causes the tree view to crash

**0.1.5** (august 27 2013)

-  Issue 6: save the tree state
-  Issue 7: do not handle the right mouse click

**0.1.4** (august 8 2013)

-  Issue 5: Support for uuid ids

**0.1.3** (may 2 2013)

*This version drops support for Django 1.3.7*

-  Issue 2: Posting a screenshot in the readme would be really useful
   (thanks to Andy Baker)
-  Issue 3: Use static templatetag for CDN-compatible file paths (thanks
   to Alex Holmes)
-  Added `Coveralls <https://coveralls.io/r/mbraak/django-mptt-admin>`_
   support

**0.1.2** (march 12 2013)

-  Issue 1: Grid view doesn't link correctly to object change pages
   (thanks to Kris Fields)

**0.1.1** (februari 25 2013)

-  Added experimental Python 3 support

**0.1** (februari 7 2013)

-  Initial version

.. |Build
Status| image:: https://travis-ci.org/mbraak/django-mptt-admin.svg?branch=master
.. |Version| image:: https://pypip.in/version/django-mptt-admin/badge.svg
.. |Development
Status| image:: https://pypip.in/status/django-mptt-admin/badge.svg
.. |Coverage
Status| image:: https://img.shields.io/coveralls/mbraak/django-mptt-admin.svg
.. |Downloads| image:: https://pypip.in/download/django-mptt-admin/badge.svg
.. |Format| image:: https://pypip.in/format/django-mptt-admin/badge.svg
.. |Requirements
Status| image:: https://requires.io/github/mbraak/django-mptt-admin/requirements.png?branch=master
.. |License| image:: https://pypip.in/license/django-mptt-admin/badge.svg
.. |Supported Python
versions| image:: https://pypip.in/py_versions/django-mptt-admin/badge.svg
.. |Supported Python
implementations| image:: https://pypip.in/implementation/django-mptt-admin/badge.svg
