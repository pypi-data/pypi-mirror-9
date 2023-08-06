"""
Classes representing collections of :py:class:`bags
<tiddlyweb.model.bag.Bag>`, :py:class:`recipes
<tiddlyweb.model.recipe.Recipe>` and :py:class:`tiddlers
<tiddlyweb.model.tiddler.Tiddler>`.

Because the main reason for having a collection is to send it out over
the web, the collections keep track of their last-modified time and
generate a hash suitable for use as an ETag.
"""

import logging

from tiddlyweb.store import StoreError
from tiddlyweb.util import sha

from tiddlyweb.model.tiddler import Tiddler


LOGGER = logging.getLogger(__name__)


class Collection(object):
    """
    Base class for all collections.

    Can be used directly for general collections if required.

    A collection acts as generator, yielding one of its contents when
    iterated.
    """

    def __init__(self, title=''):
        self._digest = sha()
        self.modified = '0'
        self.title = title
        self.link = ''
        self._container = []

    def __contains__(self, item):
        return item in self._container

    def add(self, thing):
        """
        Add an item to the container, updating the digest and
        modified information.
        """
        self._update_digest(thing)
        self._container.append(thing)
        try:
            modified_string = str(thing.modified)
            modified_string = modified_string.ljust(14, '0')
            if modified_string > self.modified:
                self.modified = modified_string
        except AttributeError:
            pass

    def _update_digest(self, thing):
        """
        Update the digest with this thing.
        """
        self._digest.update(thing.encode('utf-8'))

    def hexdigest(self):
        """
        Return the current hex representation of the hash digest of this
        collection.
        """
        return self._digest.hexdigest()

    def __iter__(self):
        """
        Generate the items in this container.
        """
        for thing in self._container:
            yield thing


class Container(Collection):
    """
    A collection of things which have a ``name`` attribute.

    In TiddlyWeb this is for lists of :py:class:`bags
    <tiddlyweb.model.bag.Bag>` and :py:class:`recipes
    <tiddlyweb.model.recipe.Recipe>`.
    """

    def _update_digest(self, thing):
        """
        Update the digest with this thing's ``name``.
        """
        self._digest.update(thing.name.encode('utf-8'))


class Tiddlers(Collection):
    """
    A Collection specifically for :py:class:`tiddlers
    <tiddlyweb.model.tiddler.Tiddler>`.

    This differs from the base class in two ways:

    The calculation of the digest is more detailed in order to create
    stong ``ETags`` for the collection.

    When iterated, if ``store`` is set on the Collection, then a yielded
    tiddler will be loaded from the store to fill in all its attributes.
    When a tiddler is added to the collection, if it is already filled,
    a non-full copy is made and put into the collection. This is done
    to save memory and because often the data is not needed.

    If ``collections.use_memory`` is ``True`` in ``config`` then the
    full tiddler is kept in the collection. On servers with adequate
    memory this can be more efficient.
    """

    def __init__(self, title='', store=None, bag=None, recipe=None):
        Collection.__init__(self, title)
        self.is_revisions = False
        self.is_search = False
        self.bag = bag
        self.recipe = recipe
        self.store = store

    def __iter__(self):
        """
        Generate the items in this container. Since these are
        :py:class:`tiddlers <tiddlyweb.model.tiddler.Tiddler>`,
        load them if they are not loaded. If a tiddler has been removed since
        this request was started, skip it.
        """
        for tiddler in self._container:
            if not tiddler.store and self.store:
                try:
                    tiddler = self.store.get(tiddler)
                except StoreError as exc:
                    LOGGER.debug('missed tiddler in collection: %s, %s',
                            tiddler, exc)
                    continue
            yield tiddler

    def add(self, tiddler):
        """
        Add a reference to the :py:class:`tiddler
        <tiddlyweb.model.tiddler.Tiddler>` to the container, updating the
        digest and modified information. If the tiddler has recently been
        deleted, resulting in a :py:class:`StoreError
        <tiddlyweb.store.StoreError>`, don't add it.
        """
        if not tiddler.store and self.store:
            try:
                tiddler = self.store.get(tiddler)
            except StoreError as exc:
                LOGGER.debug(
                        'tried to add missing tiddler to collection: %s, %s',
                        tiddler, exc)
                return
            if not self.store.environ['tiddlyweb.config'].get(
                    'collections.use_memory', False):
                reference = Tiddler(tiddler.title, tiddler.bag)
                if tiddler.revision:
                    reference.revision = tiddler.revision
                if tiddler.recipe:
                    reference.recipe = tiddler.recipe
                self._container.append(reference)
            else:
                self._container.append(tiddler)
        else:
            self._container.append(tiddler)
        self._update_digest(tiddler)
        modified_string = str(tiddler.modified)
        modified_string = modified_string.ljust(14, '0')
        if modified_string > self.modified:
            self.modified = modified_string

    def _update_digest(self, tiddler):
        """
        Update the digest with information from this tiddler.
        """
        try:
            self._digest.update(tiddler.bag.encode('utf-8'))
        except AttributeError:
            pass
        self._digest.update(tiddler.title.encode('utf-8'))
        self._digest.update(str(tiddler.revision).encode('utf-8'))
