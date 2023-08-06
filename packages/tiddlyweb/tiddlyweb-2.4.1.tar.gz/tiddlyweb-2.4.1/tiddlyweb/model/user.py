"""
A class representing a simple user entity.

A User object is not required during TiddlyWeb requests,
:py:class:`credentials extractors
<tiddlyweb.web.extractors.ExtractorInterface>` and :py:class:`policies
<tiddlyweb.model.policy.Policy>` may work with arbitrary data for
authentication and authorization. However if a locally stored user
is required the :py:class:`User` may be used.
"""

from tiddlyweb.util import sha

from tiddlyweb.fixups import unicode


class User(object):
    """
    A simple representation of a user. A user is a username, an optional
    password, an optional list of roles, and an optional note.
    """

    def __init__(self, usersign, note=None):
        self.usersign = unicode(usersign)
        self.note = note
        if self.note:
            self.note = unicode(self.note)
        self._password = None
        self.roles = set()

    def add_role(self, role):
        """
        Add the named ``role`` (a string) to this user.
        """
        self.roles.add(unicode(role))

    def del_role(self, role):
        """
        Remove the named ``role`` (a string) from this user.
        If it is not there, do nothing.
        """
        self.roles.discard(role)

    def list_roles(self):
        """
        List (as a list of strings) the roles that this
        user has.
        """
        return list(self.roles)

    def set_password(self, password):
        """
        Set the password for this user.
        """
        password = password.strip()
        # The null password or empty password string never auths
        if not password:
            return
        self._password = sha(password.strip()).hexdigest()

    def check_password(self, candidate_password):
        """
        Check the password for this user. Return ``True`` if correct.
        """
        if not self._password:
            return False
        crypted_thing = sha(candidate_password.strip()).hexdigest()
        return crypted_thing == self._password

    def __repr__(self):
        return self.usersign + ' ' + object.__repr__(self)
