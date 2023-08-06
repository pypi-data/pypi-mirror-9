Changes
=======

0.2.3 (2015-03-08)
++++++++++++++++++

- Fix `#14 <https://github.com/vinta/django-email-confirm-la/issues/14>`_ Admin raises an `AttributeError` when `content_object` doesn't exist


0.2.2 (2014-11-13)
++++++++++++++++++

- New admin action: Re-send confirmation email
- New setting: ``EMAIL_CONFIRM_LA_EMAIL_BACKEND``
- Change ``EMAIL_CONFIRM_LA_DOMAIN`` default value to ``''``, fail fast
- Fix circular import


0.2.1 (2014-11-09)
++++++++++++++++++

- Django 1.6 compatibility: ``transaction.atomic``
- Django 1.4 compatibility: ``update_fields``


0.2.0 (2014-11-08)
++++++++++++++++++

- Django 1.7 compatibility: ``migrations``


0.1.0 (2014-10-31)
++++++++++++++++++

- Initial release
