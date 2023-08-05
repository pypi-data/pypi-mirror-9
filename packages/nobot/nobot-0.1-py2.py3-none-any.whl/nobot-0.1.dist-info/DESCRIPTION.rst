Nobot
=====

**Django reCAPTCHA form field/widget integration app.**


.. image:: https://travis-ci.org/EnTeQuAk/nobot.svg?branch=master
    :target: https://travis-ci.org/EnTeQuAk/nobot

.. image:: https://badge.fury.io/py/nobot.png
    :target: http://badge.fury.io/py/nobot

.. image:: https://pypip.in/d/nobot/badge.png
        :target: https://pypi.python.org/pypi/nobot


Installation
------------

#. Install or add ``nobot`` to your Python path.

#. Add ``nobot`` to your ``INSTALLED_APPS`` setting.

#. Add a ``NOBOT_RECAPTCHA_PUBLIC_KEY`` setting to the project's ``settings.py`` file. This is your public API key as provided by reCAPTCHA, i.e.::

    NOBOT_RECAPTCHA_PUBLIC_KEY = '76wtgdfsjhsydt7r5FFGFhgsdfytd656sad75fgh'

   This can be seperately specified at runtime by passing a ``public_key`` parameter when constructing the ``ReCaptchaField``, see field usage below.

#. Add a ``NOBOT_RECAPTCHA_PRIVATE_KEY`` setting to the project's ``settings.py`` file. This is your private API key as provided by reCAPTCHA, i.e.::

    NOBOT_RECAPTCHA_PRIVATE_KEY = '98dfg6df7g56df6gdfgdfg65JHJH656565GFGFGs'

   This can be seperately specified at runtime by passing a ``private_key`` parameter when constructing the ``ReCaptchaField``, see field usage below.


Usage
-----

Field
~~~~~

The quickest way to add reCAPTHCA to a form is to use the included ``ReCaptchaField`` field type. A ``ReCaptcha`` widget will be rendered with the field validating itself without any further action required from you. For example::

    from django import forms
    from nobot.fields import ReCaptchaField

    class FormWithCaptcha(forms.Form):
        captcha = ReCaptchaField()

The reCAPTCHA widget supports several `Javascript options variables <https://code.google.com/apis/recaptcha/docs/customization.html>`_ customizing the behaviour of the widget, such as ``theme`` and ``lang``. You can forward these options to the widget by passing an ``attr`` parameter containing a dictionary of options to ``ReCaptchaField``, i.e.::

    captcha = ReCaptchaField(attrs={'theme' : 'clean'})

The captcha client takes the key/value pairs and writes out the RecaptchaOptions value in JavaScript.


Credits
-------

Originally developed under the name `django-recaptcha <https://github.com/praekelt/django-recaptcha/>`_ by Praekelt Foundation. Forked for better testability and extensibility.
Authors
=======

``nobot`` was previously developed under the name `django-recaptcha` and under the
Copyright of Praekelt Foundation. The following copyright notice holds true for
releases before the renaming: "Copyright (c) by Praekelt Foundation

Package Maintainer
------------------
* Christopher Grebs

Praekelt Foundation
-------------------
* Shaun Sephton
* Peter Pistorius
* Hedley Roos

bTaylor Design
--------------
* `Brandon Taylor <http://btaylordesign.com/>`_

Other
-----
* Brooks Travis
* `Denis Mishchishin <https://github.com/denz>`_
* `Joshua Peper <https://github.com/zout>`_
* `Rodrigo Primo <https://github.com/rodrigoprimo>`_
* `snnwolf <https://github.com/snnwolf>`_
* `Adriano Orioli <https://github.com/Aorioli>`_
* `cdvv7788 <https://github.com/cdvv7788>`_
Changelog
=========

0.1
---

* Initial release after refactoring and renaming to `nobot`.


Original Changelog of django-recaptcha
======================================

1.0.3 (2015-01-13)
------------------

#. Added nocaptcha recaptcha support

1.0.2 (2014-09-16)
------------------

#. Fixed Russian translations
#. Added Spanish translations

1.0.1 (2014-09-11)
------------------

#. Added Django 1.7 suport
#. Added Russian translations
#. Added multi dependancy support
#. Cleanup

1.0 (2014-04-23)
----------------

#. Added Python 3 support
#. Added French, Dutch and Brazilian Portuguese translations

0.0.9 (2014-02-14)
------------------
#. Bugfix: release master and not develop. This should fix the confusion due to master having been the default branch on Github.

0.0.8 (2014-02-13)
------------------
#. Bugfix: remove reference to options.html.

0.0.7 (2014-02-12)
------------------
#. Make it possible to load the widget via ajax.

0.0.6 (2013-01-31)
------------------
#. Added an extra parameter `lang` to bypass Google's language bug. See http://code.google.com/p/recaptcha/issues/detail?id=133#c3
#. widget.html no longer includes options.html. Options are added directly to widget.html

0.0.5 (2013-01-17)
------------------
#. Removed django-registration dependency
#. Changed testing mechanism to environmental variable `RECAPTCHA_TESTING`

0.0.4
-----
#. Handle missing REMOTE_ADDR request meta key. Thanks Joe Jasinski.
#. Added checks for settings.DEBUG to facilitate tests. Thanks Victor Neo.
#. Fix for correct iframe URL in case of no javascript. Thanks gerdemb.

0.0.3 (2011-09-20)
------------------
#. Don't force registration version thanks kshileev.
#. Render widget using template, thanks denz.

0.0.2 (2011-08-10)
------------------
#. Use remote IP when validating.
#. Added SSL support, thanks Brooks Travis.
#. Added support for Javascript reCAPTCHA widget options, thanks Brandon Taylor.
#. Allow for key and ssl specification at runtime, thanks Evgeny Fadeev.

0.0.1 (2010-06-17)
------------------
#. Initial release.


