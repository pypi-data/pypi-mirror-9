====================
Mezzanine BS Banners
====================

**Making it easier to manage DMARC reports**

Designed to quickly and easily import DMARC reports.

Quick start
-----------

1. Install the app

2. Add "dmarc" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = (
        ...
        'dmarc',
    )

3. Run 'python manage.py migrate' to create the database models.

Usage
=====
python manage.py importdmarcreport

Dependencies
============

* `Django`_ 1.7

Support
=======

To report a security issue, please send an email privately to
`ahicks@p-o.co.uk`_. This gives us a chance to fix the issue and
create an official release prior to the issue being made
public.

For general questions or comments, please contact  `ahicks@p-o.co.uk`_.

`Project website`_

Communications are expected to conform to the `Django Code of Conduct`_.

.. GENERAL LINKS

.. _`Django`: http://djangoproject.com/
.. _`Django Code of Conduct`: https://www.djangoproject.com/conduct/
.. _`Python`: http://python.org/
.. _`Persistent Objects Ltd`: http://p-o.co.uk/
.. _`Project website`: http://p-o.co.uk/tech-articles/django-dmarc/


.. PEOPLE WITH QUOTES

.. _`Alan Hicks`: https://plus.google.com/103014117568943351106
.. _`ahicks@p-o.co.uk`: mailto:ahicks@p-o.co.uk?subject=django-dmarc+Security+Issue
