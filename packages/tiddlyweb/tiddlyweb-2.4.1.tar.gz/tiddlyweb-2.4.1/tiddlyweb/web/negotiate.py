"""
WSGI Middleware to do a limited version of content negotiation
and put the type in ``tiddlyweb.type``. On ``GET`` and ``HEAD``
requests the ``Accept`` header is examined. On ``POST`` and ``PUT``,
``Content-Type``. If extensions are provided on a URI used in a ``GET``
request if the extension matches something in ``extension_types`` in
:py:mod:`config <tiddlyweb.config>`, the type indicated by the
extension wins over the Accept header.
"""

import logging
import mimeparse


LOGGER = logging.getLogger(__name__)


class Negotiate(object):
    """
    Perform a form of content negotiation to provide information
    to the WSGI environment that will later be used to choose
    serializers.
    """

    def __init__(self, application):
        self.application = application

    def __call__(self, environ, start_response):
        figure_type(environ)
        return self.application(environ, start_response)


def figure_type(environ):
    """
    Determine either the ``Content-Type`` (for ``POST`` and ``PUT``)
    or ``Accept`` header (for ``GET``) and put that information
    in ``tiddlyweb.type`` in the WSGI environment.
    """
    if environ['REQUEST_METHOD'].upper() == 'GET':
        _figure_type_for_get(environ)
    else:
        _figure_type_for_other(environ)


def _figure_type_for_other(environ):
    """
    Determine the type for PUT and POST
    requests, based on the content-type
    header.
    """
    content_type = environ.get('CONTENT_TYPE', None)
    if content_type:
        LOGGER.debug('negotiating for content-type %s', content_type)
        content_type = content_type.split(';')[0]
        environ['tiddlyweb.type'] = content_type


def _figure_type_for_get(environ):
    """
    Determine the type for a GET request, based on the ``Accept``
    header and URI path filename extensions. If there is an extension
    and the extension matches something in ``extension_types`` in
    :py:mod:`config <tiddlyweb.config>`, the type indicated by the
    extension wins over ``Accept``. This allows humans to easily
    declare a desired representation from a browser.
    """
    accept_header = environ.get('HTTP_ACCEPT')
    path_info = environ.get('PATH_INFO')

    extension_types = environ['tiddlyweb.config']['extension_types']

    our_types = []

    if path_info:
        last_segment = path_info.rsplit('/', 1)[-1]
        extension = last_segment.rsplit('.', 1)
        if len(extension) == 2:
            ext = extension[-1]
            environ['tiddlyweb.extension'] = ext
            try:
                our_type = extension_types[ext]
                our_types.append(our_type)
            except KeyError:
                pass

    if accept_header:
        default_type = environ['tiddlyweb.config']['default_serializer']
        matchable_types = list(
                environ['tiddlyweb.config']['serializers'].keys())
        matchable_types.append(default_type)
        try:
            our_types.append(mimeparse.best_match(
                matchable_types, accept_header))
        except ValueError:
            our_types.append(default_type)

    LOGGER.debug('negotiating for accept and extensions %s', our_types)

    environ['tiddlyweb.type'] = our_types

    return
