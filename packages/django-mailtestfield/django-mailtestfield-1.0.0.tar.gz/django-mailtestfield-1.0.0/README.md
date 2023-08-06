# django-mailtestfield
Drop-in replacement for Django's forms.EmailField. Uses http://mailtest.in to validate email addresses against a number of factors. Caches results and fails silently should anything go wrong.

## MailTest

http://mailtest.in is a free email domain validation API. Reject email addresses from invalid domains (i.e. the domain is unregistered or has no MX records). Optionally reject disposable email addresses and monetized bounce services.

## Installation

You can install django-mailtestfield with pip by typing:

    pip install django-mailtestfield

Or with easy_install by typing:

    easy_install django-mailtestfield

Or manually by downloading a tarball and typing:

    python setup.py install

## Usage

Simply import the form field and use it:

    from django import forms
    from mailtest.field import EmailField

    class MyForm(forms.Form):
        email = EmailField()

## Settings

django-mailtestfield has a few settings with sensible defaults:

`MAILTEST_USE_HTTPS` Boolean, default `True`: Connect to MailTest.in via HTTPS.<br />
`MAILTEST_REJECT_DISPOSABLE` Boolean, default `True`: Reject disposable email addresses.<br />
`MAILTEST_REJECT_ROBOT` Boolean, default `True`: Reject monetized bounce addresses.<br />
`MAILTEST_CACHE_AGE` Integer, default `86400` (24 hours): Length of time to cache results.

The message strings can also be modifed in the settings.

`MAILTEST_MSG_INVALID` default `"This email address is invalid"`<br />
`MAILTEST_MSG_DISPOSABLE` default `"Disposable email addresses are not allowed"`<br />
`MAILTEST_MSG_ROBOT` default `"This email address is blocked"`
