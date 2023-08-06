import logging
log = logging.getLogger(__name__)

import string
import hashlib

from os import urandom

from zope.interface import implementer

from pyramid.interfaces import (
    IAuthenticationPolicy,
    IDebugLogger,
    )

from pyramid.security import (
    Authenticated,
    Everyone,
    )

def _clean_principal(princid):
    """ Utility function that cleans up the passed in principal

    This can easily also be extended for example to make sure that certain
    usernames are automatically off-limits.
    """
    if princid in (Authenticated, Everyone):
        princid = None
    return princid


def add_auth_policy(config):
    config.set_authentication_policy(AuthPolicy())

@implementer(IAuthenticationPolicy)
class AuthPolicy(object):
    def _log(self, msg, methodname, request):
        logger = request.registry.queryUtility(IDebugLogger)
        if logger:
            cls = self.__class__
            classname = cls.__module__ + '.' + cls.__name__
            methodname = classname + '.' + methodname
            logger.debug(methodname + ': ' + msg)

    def __init__(self, debug=False):
        self.debug = debug

    def unauthenticated_userid(self, request):
        """ No support for the unauthenticated userid """
        return None

    def authenticated_userid(self, request):
        """ Return the authenticated userid or ``None``."""

        return request.keystone.user_id
 
    def effective_principals(self, request):
        """ A list of effective principals derived from request.

        This will return a list of principals including, at least,
        :data:`pyramid.security.Everyone`. If there is no authenticated
        userid, this will be the only principal:

        .. code-block:: python

            return [Everyone]

        """
        debug = self.debug
        effective_principals = [Everyone]
        userid = self.authenticated_userid(request)

        if userid is None:
            debug and self._log(
                'authenticated_userid returned %r; returning %r' % (
                    userid, effective_principals),
                'effective_principals',
                request
                )
            return effective_principals

        roles = []

        # Get the roles here ...

        effective_principals.append(Authenticated)
        effective_principals.append(userid)
        effective_principals.extend(roles)

        debug and self._log(
            'returning effective principals: %r' % (
                effective_principals,),
            'effective_principals',
            request
             )
        return effective_principals


    def remember(self, request, principal, tokens=None, **kw):
        return []

    def forget(self, request):
        request.keystone.revoke_all()
        return []


