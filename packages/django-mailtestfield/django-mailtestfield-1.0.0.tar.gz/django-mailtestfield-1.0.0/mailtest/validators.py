import hashlib
import json
import urllib2

from django.core.cache import cache
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

# default settings
MAILTEST_USE_HTTPS = getattr(settings, 'MAILTEST_USE_HTTPS', True)
MAILTEST_REJECT_DISPOSABLE = getattr(settings, 'MAILTEST_REJECT_DISPOSABLE', True)
MAILTEST_REJECT_ROBOT = getattr(settings, 'MAILTEST_REJECT_ROBOT', True)
MAILTEST_CACHE_AGE = getattr(settings, 'MAILTEST_CACHE_AGE', (60 * 60 * 24))

# default messages
MAILTEST_MSG_INVALID = getattr(settings, 'MAILTEST_MSG_INVALID', 'This email address is invalid')
MAILTEST_MSG_DISPOSABLE = getattr(settings, 'MAILTEST_MSG_DISPOSABLE', 'Disposable email addresses are not allowed')
MAILTEST_MSG_ROBOT = getattr(settings, 'MAILTEST_MSG_ROBOT', 'This email address is blocked')

def MailTestValidator(value):
    # get the domain part of the url
    try:
        domain = value.split('@')[1]
    except:
        # invalid email format so bail, the default validator will suffice
        return

    # generate cache key (hash to prevent control character or length issues)
    cache_key = 'mailtestvalid_%s' % hashlib.sha1(domain).hexdigest()

    # attempt to retrieve from cache
    status = cache.get(cache_key)
    if status is None:
        # not in cache, attempt to get the result from the MailTest API
        try:
            if MAILTEST_USE_HTTPS:
                url = 'https://api.mailtest.in/v1/%s' % domain
            else:
                url = 'http://api.mailtest.in/v1/%s' % domain
            status = json.load(urllib2.urlopen(url, timeout=10))['status']
        except:
            # problem connecting to the API so bail gracefully
            return

        # store result in cache
        cache.set(cache_key, status, MAILTEST_CACHE_AGE)

    # invalid domain
    if status == 'INVALID':
        raise ValidationError(_(MAILTEST_MSG_INVALID))

    # check for disposable email address
    if MAILTEST_REJECT_DISPOSABLE and status == 'DISPOSABLE':
        raise ValidationError(_(MAILTEST_MSG_DISPOSABLE))

    # check for monetized bounce service
    if MAILTEST_REJECT_ROBOT and status == 'ROBOT':
        raise ValidationError(_(MAILTEST_MSG_ROBOT))
