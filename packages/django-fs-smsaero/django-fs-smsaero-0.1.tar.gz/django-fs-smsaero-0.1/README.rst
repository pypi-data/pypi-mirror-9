Installation
============

1. Install ``django-fs-smsaero`` using ``pip``::

    $ pip install django-fs-smsaero

2. Add ``'smsaero'`` to your ``INSTALLED_APPS`` setting::

    INSTALLED_APPS = (
        ...
        'smsaero',
        ...
    )

3. Run ``syncdb`` or ``migrate``::

    $ ./manage.py syncdb

    or

    $ ./manage.py migrate


Usage
=====

Just import ``send_sms`` function and use it::

    from smsaero.api import send_sms

    send_sms('+79135461856', 'Some text.')


Credits
=======

`Fogstream <http://fogstream.ru>`_
