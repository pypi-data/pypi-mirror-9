Installation
============

1. Install ``django-fs-smsc`` using ``pip``::

    $ pip install django-fs-smsc

2. Add ``'smsc'`` to your ``INSTALLED_APPS`` setting::

    INSTALLED_APPS = (
        ...
        'smsc',
        ...
    )

3. Add ``'smsc.urls'`` to your url-patterns::

    urlpatterns = patterns('',
        ...
        url(r'^smsc/', include('smsc.urls')),
        ...
    )

4. Run ``syncdb`` or ``migrate``::

    $ ./manage.py syncdb

    or

    $ ./manage.py migrate


Usage
=====

Just import ``send_sms`` function and use it::

    from smsc.api import send_sms

    send_sms('+79135461856', 'Some text.')


Credits
=======

`Fogstream <http://fogstream.ru>`_
