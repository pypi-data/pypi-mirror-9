"""
Cover tiddlyweb.web.util.make_cookie.

It creates the string used to put in a Set-Cookie
header.
"""

import sys

from tiddlyweb.util import sha
from tiddlyweb.web.util import make_cookie


def test_cookie_name_value():
    string = make_cookie('test1', 'alpha1')

    assert string == 'test1=alpha1; httponly'


def test_unicode_cookie_value():
    string = make_cookie('tiddlyweb', u'\u3454')
    assert string == 'tiddlyweb=%E3%91%94; httponly'


def test_cookie_path():
    string = make_cookie('test2', 'alpha2', path='/path/to/location')

    assert string == 'test2=alpha2; Path=/path/to/location; httponly'

    string = make_cookie('test2', 'alpha2', path='/path/to/location',
            httponly=False)

    assert string == 'test2=alpha2; Path=/path/to/location'


def test_cookie_expire():
    string = make_cookie('test3', 'alpha3', expires=50)

    assert string == 'test3=alpha3; Max-Age=50; httponly'


def test_cookie_mac():
    string = make_cookie('test4', 'alpha4', mac_key='secret')

    secret_string = sha('%s%s' % ('alpha4', 'secret')).hexdigest()

    if sys.version_info[0] == 2:  # Cookie changed
        assert string == 'test4="alpha4:%s"; httponly' % secret_string
    else:
        assert string == 'test4=alpha4:%s; httponly' % secret_string


def test_cookie_domain():
    string = make_cookie('test5', 'alpha5', domain=".tiddlyspace.com")

    assert string == 'test5=alpha5; Domain=.tiddlyspace.com; httponly'
