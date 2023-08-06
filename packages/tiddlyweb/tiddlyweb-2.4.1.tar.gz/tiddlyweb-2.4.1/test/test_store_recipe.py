"""
Exploratory testing for storing recipes.

"""

import os

import sys

import py.test

import tiddlyweb.stores.text

from tiddlyweb.model.recipe import Recipe
from tiddlyweb.store import NoRecipeError

from .fixtures import reset_textstore, _teststore

expected_stored_filename = os.path.join('store', 'recipes', 'testrecipe')

recipe_list_string = [
        [u'bagone', u'select=title:TiddlerOne'],
        [u'bagtwo', u'select=title:TiddlerTwo'],
        [u'bagthree', u'select=tag:tagone;select=tag:tagthree']
]

expected_stored_content = """desc: I enjoy being stored
policy: {"read": [], "create": [], "manage": [], "accept": [], "write": [], "owner": null, "delete": []}

/bags/bagone/tiddlers?select=title:TiddlerOne
/bags/bagtwo/tiddlers?select=title:TiddlerTwo
/bags/bagthree/tiddlers?select=tag:tagone;select=tag:tagthree"""


def setup_module(module):
    """
    Need to clean up the store here.
    """
    reset_textstore()
    module.store = _teststore()


def test_recipe_put():
    """
    put a recipe to disk and make sure it is there.
    """

    recipe = Recipe('testrecipe')
    recipe.desc = 'I enjoy being stored'
    recipe.set_recipe(recipe_list_string)
    store.put(recipe)

    if type(store.storage) != tiddlyweb.stores.text.Store:
        py.test.skip('skipping this test for non-text store')

    assert os.path.exists(expected_stored_filename)

    with open(expected_stored_filename) as f:
        content = f.read()

    if sys.version_info[0] < 3:
        assert content == expected_stored_content


def test_recipe_get():
    """
    get a recipe from disk and confirm it has proper form.
    """

    stored_recipe = Recipe('testrecipe')
    stored_recipe = store.get(stored_recipe)

    assert stored_recipe.get_recipe() == recipe_list_string


def test_recipe_delete():
    recipe = Recipe('deleteme')
    recipe.desc = 'delete me please'
    store.put(recipe)

    stored_recipe = Recipe('deleteme')
    stored_recipe = store.get(stored_recipe)
    assert stored_recipe.desc == 'delete me please'

    deleted_recipe = Recipe('deleteme')
    store.delete(deleted_recipe)

    py.test.raises(NoRecipeError, 'store.get(deleted_recipe)')
    py.test.raises(NoRecipeError, 'store.delete(deleted_recipe)')


def test_recipe_no_recipe():
    """
    make a sure a recipe that is stored without a recipe is retrievable
    """
    recipe = Recipe('testrecipe2')
    recipe.desc = 'I enjoy being stored'
    store.put(recipe)

    stored_recipe = Recipe('testrecipe2')
    stored_recipe = store.get(stored_recipe)

    assert stored_recipe.desc == recipe.desc


def test_list():
    recipe = Recipe('testrecipe3')
    store.put(recipe)
    recipes = list(store.list_recipes())

    assert len(recipes) == 3
    assert u'testrecipe' in [recipe.name for recipe in recipes]
    assert u'testrecipe2' in [recipe.name for recipe in recipes]
    assert u'testrecipe3' in [recipe.name for recipe in recipes]


def test_recipe_weird_bag():
    recipe = Recipe('weirdbags')
    recipe.set_recipe([
        ('foo/bar', ''),
        ('zam/boom', ''),
    ])
    store.put(recipe)

    new_recipe = Recipe('weirdbags')
    new_recipe = store.get(new_recipe)
    bags = [bag for bag, filter in new_recipe.get_recipe()]
    assert bags == ['foo/bar', 'zam/boom']


def test_recipe_bad_name():
    recipe = Recipe('../badname')
    py.test.raises(NoRecipeError, 'store.put(recipe)')
    py.test.raises(NoRecipeError, 'store.get(recipe)')
