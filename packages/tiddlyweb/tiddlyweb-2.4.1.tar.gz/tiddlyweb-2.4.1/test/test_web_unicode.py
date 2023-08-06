"""
Test a full suite of unicode interactions.
"""


from tiddlyweb.fixups import unquote
import simplejson
import httplib2

from .fixtures import (reset_textstore, _teststore, initialize_app,
        get_http)
from tiddlyweb.model.recipe import Recipe
from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.model.bag import Bag
from tiddlyweb.model.user import User


encoded_name = 'aaa%25%E3%81%86%E3%81%8F%E3%81%99'
name = unquote(encoded_name)
http = get_http()


def setup_module(module):
    initialize_app()
    reset_textstore()
    module.store = _teststore()
    user = User(name)
    user.set_password(name)
    module.store.put(user)
    module.cookie = None


def test_unicode_cookie():
    global cookie
    nested_response = None
    try:
        response, content = http.requestU(
                'http://our_test_domain:8001/challenge/cookie_form',
                method='POST',
                body='user=%s&password=%s' % (encoded_name, encoded_name),
                redirections=0,
                headers={'Content-type': 'application/x-www-form-urlencoded'}
                )
    except httplib2.RedirectLimit as e:
        nested_response = e

    assert nested_response.response['status'] == '303', content
    cookie = nested_response.response['set-cookie']
    assert encoded_name in cookie


def test_put_unicode_bag():
    encoded_bag_name = encoded_name
    bag_name = name

    bag_policy = dict(delete=[bag_name])
    bag_json = simplejson.dumps({'policy': bag_policy})
    response, content = http.requestU(
            'http://our_test_domain:8001/bags/%s' % encoded_bag_name,
            method='PUT',
            body=bag_json,
            headers={'Content-Type': 'application/json',
                'Cookie': cookie})
    assert response['status'] == '204'

    bag = Bag(bag_name)
    bag = store.get(bag)
    assert bag.policy.delete == bag_policy['delete']
    assert bag.policy.owner == name
    assert bag.name == bag_name


def test_put_unicode_tiddler():
    encoded_tiddler_name = encoded_name
    tiddler_name = name
    encoded_bag_name = encoded_name
    bag_name = name

    tiddler_text = u'hello %s' % name
    tiddler_json = simplejson.dumps(dict(modifier=name,
        text=tiddler_text, tags=[name]))
    response, content = http.requestU(
            'http://our_test_domain:8001/bags/%s/tiddlers/%s'
            % (encoded_bag_name, encoded_tiddler_name),
            method='PUT',
            body=tiddler_json,
            headers={'Content-Type': 'application/json'})

    assert response['status'] == '204'

    tiddler = Tiddler(tiddler_name, bag=bag_name)
    tiddler = store.get(tiddler)
    assert tiddler.title == tiddler_name
    assert tiddler.text == tiddler_text
    assert tiddler.tags == [name]


def test_put_unicode_recipe():
    encoded_recipe_name = encoded_name
    recipe_name = name
    bag_name = name

    recipe_list = [[bag_name, '[tag[%s]]' % name]]
    json_recipe_list = simplejson.dumps(dict(recipe=recipe_list))
    response, content = http.requestU(
            'http://our_test_domain:8001/recipes/%s' % encoded_recipe_name,
            method='PUT',
            body=json_recipe_list,
            headers={'Content-Type': 'application/json'})
    assert response['status'] == '204'

    recipe = Recipe(recipe_name)
    recipe = store.get(recipe)
    assert recipe.get_recipe() == recipe_list
    assert recipe.name == recipe_name


def test_get_tiddlers_from_recipe():
    get_tiddlers_from_thing('recipes')


def test_get_tiddlers_from_bag():
    get_tiddlers_from_thing('bags')


def test_filter_tiddlers():
    response, content = http.requestU(
            'http://our_test_domain:8001/bags/%s/tiddlers.json?select=tag:%s'
            % (encoded_name, encoded_name),
            method='GET')
    assert response['status'] == '200'
    info = simplejson.loads(content)
    assert info[0]['tags'] == [name]
    assert info[0]['title'] == name
    assert info[0]['bag'] == name
    assert len(info) == 1


def test_double_uri_encoded_title():
    """
    This test works against wsgi-intercept but fails when
    used with web server like CherryPy, nginx or Apache.

    This is because PATH_INFO is being decoded before being given
    to the environment. This is not a good thing, it means that things
    like %2F get turned into / in URIs.

    See: https://github.com/tiddlyweb/tiddlyweb/issues/86
         https://mail.python.org/pipermail/web-sig/2008-January/thread.html#3122
    """
    store.put(Bag('double'))

    response, content = http.requestU(
            'http://our_test_domain:8001/bags/double/tiddlers/test%2520one',
            method='PUT',
            headers={'Content-Type': 'application/json'},
            body='{"text": "hi"}')

    assert response['status'] == '204'

    tiddler = store.get(Tiddler('test%20one', 'double'))
    assert tiddler.title == 'test%20one'


def get_tiddlers_from_thing(container):
    response, content = http.requestU(
            'http://our_test_domain:8001/%s/%s/tiddlers.json' % (
                container, encoded_name),
            method='GET')
    assert response['status'] == '200'
    tiddler_info = simplejson.loads(content)
    assert tiddler_info[0]['title'] == name
    assert tiddler_info[0]['tags'] == [name]

    response, content = http.requestU(
            'http://our_test_domain:8001/%s/%s/tiddlers/%s.json'
            % (container, encoded_name, encoded_name),
            method='GET')
    assert response['status'] == '200'
    tiddler_info = simplejson.loads(content)
    assert tiddler_info['title'] == name
    assert tiddler_info['tags'] == [name]
    assert tiddler_info['text'] == 'hello %s' % name
