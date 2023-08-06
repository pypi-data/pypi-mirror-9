from nose.tools import eq_

from tidings.models import WatchFilter, EmailUser
from tidings.tests import watch, watch_filter, TestCase


# TODO: write a test to ensure that event types don't collide
# case-insensitive-ly
# E.g. No duplicates in this list: [et.lower() for et in EVENT_TYPES]


class WatchTests(TestCase):
    """Tests for Watch model"""

    def test_unsubscribe_url(self):
        """Make sure unsubscribe_url() returns something URL-ish."""
        w = watch()
        url = w.unsubscribe_url()
        assert url.startswith('http')
        assert url.endswith('?s=%s' % w.secret)


class WatchFilterTests(TestCase):
    """Tests for WatchFilter"""

    def test_value_range(self):
        """Assert 0 and 2**32-1 both fit in the value field.

        That's the range of our hash function.

        """
        MAX_INT = 2 ** 32 - 1
        watch_filter(name='maxint', value=MAX_INT).save()
        eq_(MAX_INT, WatchFilter.objects.get(name='maxint').value)


class EmailUserTests(TestCase):
    """Tests for EmailUser class"""

    def test_blank_username(self):
        """Assert EmailUsers' username is ''.

        This isn't covered by the tests in django.contrib.auth, and we need to
        hear about it if it changes, as some implementations of _mails() depend
        on it.

        """
        eq_('', EmailUser().username)
