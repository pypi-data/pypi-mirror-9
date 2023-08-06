"""
WSGI Middleware apps that haven't gotten around to being extracted to
their own modules.
"""

import logging
import time

from httpexceptor import HTTP403, HTTP302

from tiddlyweb.model.policy import UserRequiredError, ForbiddenError
from tiddlyweb.store import Store
from tiddlyweb.web.util import server_base_url

from tiddlyweb.fixups import quote

try:
    unicode = unicode
except NameError:
    unicode = str


class Header(object):
    """
    If ``REQUEST_METHOD`` is HEAD, change it internally to ``GET`` and
    consume the generated output so the response has no body.
    """

    def __init__(self, application):
        self.application = application

    def __call__(self, environ, start_response):
        if environ['REQUEST_METHOD'] == 'HEAD':
            environ['REQUEST_METHOD'] = 'GET'
            self.application(environ, start_response)
            return []
        else:
            return self.application(environ, start_response)


class SimpleLog(object):
    """
    WSGI Middleware to write a very simple log to ``stdout``.

    Borrowed from Paste Translogger
    """

    format = ('%(REMOTE_ADDR)s - %(REMOTE_USER)s [%(time)s] '
            '"%(REQUEST_METHOD)s %(REQUEST_URI)s %(HTTP_VERSION)s" '
            '%(status)s %(bytes)s "%(HTTP_REFERER)s" "%(HTTP_USER_AGENT)s"')

    def __init__(self, application):
        self.application = application

    def __call__(self, environ, start_response):
        logger = logging.getLogger('tiddlyweb')
        if logger.isEnabledFor(logging.INFO):
            return self._log_app(environ, start_response)
        else:
            return self.application(environ, start_response)

    def _log_app(self, environ, start_response):
        req_uri = quote(environ.get('SCRIPT_NAME', '')
                + environ.get('PATH_INFO', ''))
        if environ.get('QUERY_STRING'):
            req_uri += '?' + environ['QUERY_STRING']

        def replacement_start_response(status, headers, exc_info=None):
            """
            We need to gaze at the content-length, if set, to
            write log info.
            """
            size = None
            for name, value in headers:
                if name.lower() == 'content-length':
                    size = value
            self.write_log(environ, req_uri, status, size)
            return start_response(status, headers, exc_info)

        return self.application(environ, replacement_start_response)

    def write_log(self, environ, req_uri, status, size):
        """
        Write the log info out in a formatted form to ``logging.info``.

        This is rather more complex than desirable because there is
        a mix of ``str`` and ``unicode`` in the gathered data and it
        needs to be made acceptable for output.
        """
        environ['REMOTE_USER'] = None
        try:
            environ['REMOTE_USER'] = environ['tiddlyweb.usersign']['name']
        except KeyError:
            pass
        if size is None:
            size = '-'
        log_format = {
                'REMOTE_ADDR': environ.get('REMOTE_ADDR') or '-',
                'REMOTE_USER': environ.get('REMOTE_USER') or '-',
                'REQUEST_METHOD': environ['REQUEST_METHOD'],
                'REQUEST_URI': req_uri,
                'HTTP_VERSION': environ.get('SERVER_PROTOCOL'),
                'time': time.strftime('%d/%b/%Y:%H:%M:%S ', time.localtime()),
                'status': status.split(None, 1)[0],
                'bytes': size,
                'HTTP_REFERER': environ.get('HTTP_REFERER', '-'),
                'HTTP_USER_AGENT': environ.get('HTTP_USER_AGENT', '-'),
        }
        message = self.format % log_format
        logging.info(message)


class StoreSet(object):
    """
    WSGI Middleware that sets our choice of :py:class:`Store
    <tiddlyweb.store.Store>` in the ``environ``. That is, initialize
    the store for each request.
    """

    def __init__(self, application):
        self.application = application

    def __call__(self, environ, start_response):
        database = Store(environ['tiddlyweb.config']['server_store'][0],
                environ['tiddlyweb.config']['server_store'][1],
                environ)
        environ['tiddlyweb.store'] = database
        return self.application(environ, start_response)


class TransformProtect(object):
    """
    WSGI Middleware to add a ``Cache-Control: no-transform``` header
    so that mobile companies that transcode content over their 3G (etc)
    networks don't, as it will break various JavaScript things,
    including TiddlyWiki.
    """

    def __init__(self, application):
        self.application = application

    def __call__(self, environ, start_response):

        def replacement_start_response(status, headers, exc_info=None):
            if '200' in status or '304' in status:
                headers.append(('Cache-Control', 'no-transform'))
            return start_response(status, headers, exc_info)

        return self.application(environ, replacement_start_response)


class EncodeUTF8(object):
    """
    WSGI Middleware to ensure that the unicode content sent out the
    pipe is encoded to UTF-8. Within the application string-based content
    is *unicode* (i.e. not encoded).
    """

    def __init__(self, application):
        self.application = application

    def __call__(self, environ, start_response):
        return (_encoder(output) for output in
                self.application(environ, start_response))


def _encoder(string):
    """
    Take a potentially unicode string and encode it
    as UTF-8.
    """
    # if we are currently unicode, encode to utf-8
    if type(string) == unicode:
        string = string.encode('utf-8')
    return string


class PermissionsExceptor(object):
    """
    Trap :py:class:`permissions exceptions
    <tiddlyweb.model.policy.PermissionsError>` and turn them into HTTP
    exceptions so the errors are propagated to clients.
    """

    def __init__(self, application):
        self.application = application

    def __call__(self, environ, start_response):
        try:
            output = self.application(environ, start_response)
            return output
        except ForbiddenError as exc:
            raise HTTP403(exc)
        except UserRequiredError as exc:
            # We only send to the challenger on a GET
            # request. Otherwise we're in for major confusion
            # on dealing with redirects and the like in
            # scripts and javascript, where follow
            # behavior is inconsistent.
            if environ['REQUEST_METHOD'] == 'GET':
                url = _challenge_url(environ)
                raise HTTP302(url)
            raise HTTP403(exc)


def _challenge_url(environ):
    """
    Generate the URL of the challenge system
    so that GET requests are redirected to the
    right place.
    """
    script_name = environ.get('SCRIPT_NAME', '')
    query_string = environ.get('QUERY_STRING', None)
    redirect = script_name
    if query_string:
        redirect += '?%s' % query_string
    redirect = quote(redirect, safe='')
    return '%s/challenge?tiddlyweb_redirect=%s' % (
            server_base_url(environ), redirect)
