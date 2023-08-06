
"""
Test that GETting recipes.
"""


from base64 import b64encode

from tiddlyweb.fixups import unquote

import simplejson

from .fixtures import (muchdata, reset_textstore, _teststore, initialize_app,
        get_http)
from tiddlyweb.model.recipe import Recipe
from tiddlyweb.model.user import User

authorization = b64encode('cdent:cowpig'.encode('utf-8')).decode('utf-8')
http = get_http()


def setup_module(module):
    from tiddlyweb.filters.select import ATTRIBUTE_SELECTOR
    from tiddlyweb.filters import FilterError

    def hell_raiser(entity, attribute, value):
        raise FilterError('no good man')

    ATTRIBUTE_SELECTOR['error'] = hell_raiser

    initialize_app()
    reset_textstore()
    module.store = _teststore()
    muchdata(module.store)

    user = User('cdent')
    user.set_password('cowpig')
    module.store.put(user)


def test_get_recipe_txt():
    """
    Return a wiki for a recipe we can access.
    """
    response, content = http.requestU(
            'http://our_test_domain:8001/recipes/long.txt',
            method='GET')

    assert response['status'] == '200'
    assert '/bags/bag8/tiddlers?select=title:tiddler8' in content
    assert 'etag' in response
    etag = response['etag']

    response, content = http.requestU(
            'http://our_test_domain:8001/recipes/long.txt',
            method='GET', headers={'if-none-match': etag})
    assert response['status'] == '304'

    response, content = http.requestU(
            'http://our_test_domain:8001/recipes/long.txt',
            method='GET', headers={'if-none-match': etag + 'foo'})
    assert response['status'] == '200'


def test_get_recipe_not():
    """
    Return a 404 when content type not regonized.
    """
    response, content = http.requestU(
            'http://our_test_domain:8001/recipes/long.xml',
            method='GET')

    assert response['status'] == '404'


def test_get_recipe_dot_name():
    """
    Effectively return an entity with a dot in the name.
    """
    recipe = Recipe('long.gif')
    recipe.desc = u'hello'
    store.put(recipe)

    response, content = http.requestU(
            'http://our_test_domain:8001/recipes/long.gif',
            method='GET')

    assert response['status'] == '200'

    store.delete(recipe)


def test_get_recipe_not_with_accept():
    """
    Return a default content type when the extension and
    content type conflict.
    """
    response, content = http.requestU(
            'http://our_test_domain:8001/recipes/long.html',
            method='GET', headers={'Accept': 'text/plain'})

    assert response['status'] == '200'


def test_get_missing_recipe():
    """
    Return 404 for a recipe that is not there.
    """
    response, content = http.requestU(
            'http://our_test_domain:8001/recipes/not_there',
            method='GET')

    assert response['status'] == '404'


def test_get_recipe_tiddler_list():
    response, content = http.requestU(
            'http://our_test_domain:8001/recipes/long/tiddlers',
            method='GET')

    assert response['status'] == '200'
    assert content.count('<li>') == 10


def test_get_recipe_tiddler_list_disposition():
    response, content = http.requestU(
            'http://our_test_domain:8001/recipes/long/tiddlers?download=long.html',
            method='GET')

    assert response['status'] == '200'
    assert response['content-disposition'] == 'attachment; filename="long.html"'


def test_get_recipe_tiddler_list_filtered_one():
    response, content = http.requestU(
            'http://our_test_domain:8001/recipes/long/tiddlers.txt?select=title:tiddler8',
            method='GET')

    assert response['status'] == '200'
    assert response['last-modified'] == 'Fri, 23 May 2008 03:03:00 GMT'
    assert content == 'tiddler8\n'


def test_get_recipe_tiddler_list_filtered_empty():
    response, content = http.requestU(
            'http://our_test_domain:8001/recipes/long/tiddlers.txt?select=title:tiddlerfoo',
            method='GET')

    assert response['status'] == '200'


def test_get_recipe_tiddler_list_bogus_filter():
    response, content = http.requestU(
            'http://our_test_domain:8001/recipes/long/tiddlers.txt?sort=monkey',
            method='GET')
    assert response['status'] == '400'
    assert 'malformed filter' in content


def test_get_recipes_default():
    response, content = http.requestU(
            'http://our_test_domain:8001/recipes',
            method='GET')

    assert response['status'] == '200'
    assert response['content-type'] == 'text/html; charset=UTF-8'
    assert content.count('<li>') == 1
    assert content.count('recipes/long') == 1


def test_get_recipes_txt():
    response, content = http.requestU(
            'http://our_test_domain:8001/recipes.txt',
            method='GET')

    assert response['status'] == '200'
    assert response['content-type'] == 'text/plain; charset=UTF-8'
    assert len(content.rstrip().split('\n')) == 1


def test_get_recipes_json():
    response, content = http.requestU(
            'http://our_test_domain:8001/recipes.json',
            method='GET')

    assert response['status'] == '200'
    assert response['content-type'] == 'application/json'
    info = simplejson.loads(content)
    assert type(info) == list
    assert len(info) == 1
    assert info[0] == 'long'


def test_get_recipes_unsupported_neg_format():
    response, content = http.requestU(
            'http://our_test_domain:8001/recipes.gif',
            method='GET')

    assert response['status'] == '415'


def test_get_recipes_unsupported_neg_format_with_accept():
    response, content = http.requestU(
            'http://our_test_domain:8001/recipes.gif',
            method='GET', headers={'Accept': 'text/html'})

    assert response['status'] == '415'


def test_put_recipe():
    """
    Get a recipe as json then put it back with a different name.
    """
    response, content = http.requestU(
            'http://our_test_domain:8001/recipes/long.json',
            method='GET')

    json = content
    assert response['status'] == '200'

    response, content = http.requestU(
            'http://our_test_domain:8001/recipes/other',
            method='PUT', headers={'Content-Type': 'application/json'},
            body=json)

    assert response['status'] == '204'
    assert response['location'] == 'http://our_test_domain:8001/recipes/other'


def test_put_recipe_bad_json():
    """
    Get a recipe as json then put it back with a different name.
    """
    response, content = http.requestU(
            'http://our_test_domain:8001/recipes/long.json',
            method='GET')

    assert response['status'] == '200'
    json = content[0:-1]

    response, content = http.requestU(
            'http://our_test_domain:8001/recipes/other',
            method='PUT', headers={'Content-Type': 'application/json'},
            body=json)

    assert response['status'] == '400'
    assert 'unable to put recipe: unable to make json' in content


def test_put_bad_recipe():
    """
    Get a recipe as json then put it back with a different name.
    """
    response, content = http.requestU(
            'http://our_test_domain:8001/recipes/other',
            method='PUT', headers={'Content-Type': 'application/json'},
            body='{ "recipe": null }')

    assert response['status'] == '400'
    assert 'malformed input' in content


def test_put_recipe_change_description():
    """
    Get a recipe as json then put it back with a different name.
    """
    response, content = http.requestU(
            'http://our_test_domain:8001/recipes/long.json',
            method='GET')

    assert response['status'] == '200'

    info = simplejson.loads(content)
    info['desc'] = 'new description'
    json = simplejson.dumps(info)

    response, content = http.requestU(
            'http://our_test_domain:8001/recipes/other',
            method='PUT', headers={'Content-Type': 'application/json'},
            body=json)

    assert response['status'] == '204'
    assert response['location'] == 'http://our_test_domain:8001/recipes/other'

    response, content = http.requestU(response['location'],
            headers={'Accept': 'application/json'},
            method='GET')

    assert response['status'] == '200'

    info = simplejson.loads(content)
    assert info['desc'] == 'new description'


def test_put_recipe_415():
    """
    Get a recipe as text then fail to put it back as wiki.
    """
    response, content = http.requestU(
            'http://our_test_domain:8001/recipes/long.txt',
            method='GET')

    text = content
    assert response['status'] == '200'

    response, content = http.requestU(
            'http://our_test_domain:8001/recipes/other',
            method='PUT', headers={'Content-type': 'text/x-tiddlywiki'},
            body=text)

    assert response['status'] == '415'


def test_delete_recipe():
    """
    DELETE the other recipe
    """
    response, content = http.requestU(
            'http://our_test_domain:8001/recipes/other',
            method='DELETE')
    assert response['status'] == '204'

    response, content = http.requestU(
            'http://our_test_domain:8001/recipes/other',
            method='GET')
    assert response['status'] == '404'

    # what happens when we delete the same recipe again?
    response, content = http.requestU(
            'http://our_test_domain:8001/recipes/other',
            method='DELETE')
    assert response['status'] == '404'


def test_get_recipe_wiki_bag_constraints():
    """
    Make sure that when the constraints on a bag don't let read
    that a recipe with that bag throws an error.
    """
    response, content = http.requestU(
            'http://our_test_domain:8001/recipes/long/tiddlers',
            method='GET')
    assert response['status'] == '200'

    _put_bag_policy('bag28', dict(policy=dict(read=['NONE'])))
    response, content = http.requestU(
            'http://our_test_domain:8001/recipes/long/tiddlers',
            method='GET')
    assert response['status'] == '403'
    assert 'may not read' in content


def test_roundtrip_unicode_recipe():
    encoded_recipe_name = '%E3%81%86%E3%81%8F%E3%81%99'
    recipe_name = unquote(encoded_recipe_name)
    recipe_list = [[recipe_name, '']]
    body = simplejson.dumps(dict(desc='', recipe=recipe_list))
    response, content = http.requestU(
            'http://our_test_domain:8001/recipes/%s' % encoded_recipe_name,
            method='PUT', body=body.encode('utf-8'),
            headers={'Content-Type': 'application/json'})
    assert response['status'] == '204'

    recipe = Recipe(recipe_name)
    recipe = store.get(recipe)
    assert recipe.get_recipe() == recipe_list

    response, content = http.requestU(
            'http://our_test_domain:8001/recipes/%s.json'
                % encoded_recipe_name,
            method='GET')
    assert response['status'] == '200'
    assert simplejson.loads(content)['recipe'] == recipe_list


def test_recipe_policy():
    recipe_dict = {
            'desc': 'hello',
            'policy': {'manage': ['cdent'], 'read': []},
            'recipe': [['bag0', '']],
            }
    recipe_json = simplejson.dumps(recipe_dict)

    response, content = http.requestU(
            'http://our_test_domain:8001/recipes/boom', method='PUT',
            headers={'Content-Type': 'application/json'}, body=recipe_json)
    assert response['status'] == '204'

    response, content = http.requestU(
            'http://our_test_domain:8001/recipes/boom', method='GET')
    assert response['status'] == '200'

    recipe_dict = {
            'desc': 'hello',
            'policy': {'manage': ['cdent'], 'read': ['NONE']},
            'recipe': [['bag0', '']],
            }
    recipe_json = simplejson.dumps(recipe_dict)

    response, content = http.requestU(
            'http://our_test_domain:8001/recipes/boom', method='PUT',
            headers={'Content-Type': 'application/json',
                'Authorization': 'Basic %s' % authorization},
            body=recipe_json)
    assert response['status'] == '204'

    response, content = http.requestU(
            'http://our_test_domain:8001/recipes/boom', method='GET')
    assert response['status'] == '403'

    recipe_dict = {
            'desc': 'hello',
            'policy': {'manage': ['NONE'], 'read': ['NONE']},
            'recipe': [['bag0', '']],
            }
    recipe_json = simplejson.dumps(recipe_dict)
    response, content = http.requestU(
            'http://our_test_domain:8001/recipes/boom', method='PUT',
            headers={'Content-Type': 'application/json',
                'Authorization': 'Basic %s' % authorization},
            body=recipe_json)
    assert response['status'] == '204'

    recipe_dict = {
            'desc': 'hello',
            'policy': {'manage': ['cdent'], 'read': ['NONE']},
            'recipe': [['bag0', '']],
            }
    recipe_json = simplejson.dumps(recipe_dict)
    response, content = http.requestU(
            'http://our_test_domain:8001/recipes/boom', method='PUT',
            headers={'Content-Type': 'application/json',
                'Authorization': 'Basic %s' % authorization},
            body=recipe_json)
    assert response['status'] == '403'


def test_recipe_bad_filter_400():
    recipe = Recipe('badfilter')
    recipe.desc = u'hello'
    recipe.set_recipe([('bag8', 'select=error:5')])
    store.put(recipe)

    response, content = http.requestU(
            'http://our_test_domain:8001/recipes/badfilter/tiddlers')
    assert response['status'] == '400', content


def test_put_recipe_vnd():
    """
    Get a recipe as json then put it back with a different name
    using vnd.tiddlyweb.
    """
    response, content = http.requestU(
            'http://our_test_domain:8001/recipes/long.json',
            method='GET')

    json = content
    assert response['status'] == '200'

    response, content = http.requestU(
            'http://our_test_domain:8001/recipes/other',
            method='PUT', headers={'Content-Type':
                'application/vnd.tiddlyweb+json'},
            body=json)

    assert response['status'] == '204'
    assert response['location'] == 'http://our_test_domain:8001/recipes/other'


def _put_bag_policy(bag_name, policy_dict):
    """
    XXX: This is duplicated from test_web_tiddler. Clean up!
    """
    json = simplejson.dumps(policy_dict)

    response, content = http.requestU(
            'http://our_test_domain:8001/bags/%s' % bag_name,
            method='PUT', headers={'Content-Type': 'application/json'},
            body=json)
    assert response['status'] == '204'
