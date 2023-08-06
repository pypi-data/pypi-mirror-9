import logging
log = logging.getLogger(__name__)

from keystoneclient import session as kc_session
from keystoneclient.auth.identity import v3 as kc_v3
from keystoneclient.v3 import client as kc_client

from keystoneclient.openstack.common.apiclient import exceptions as kc_exceptions

from .settings import from_settings

def request_keystone(request):
    return Keystone(request)

def _kc_session_with_token(wrap):
    def _check_if_token(self):
        if not self._session and 'keystone_token' in self.request.session:
            self._get_unscoped_session(token=self.request.session['keystone_token'])

        if self._authed:
            return wrap(self)
        else:
            log.debug('Unable to get keystone session. Returning None')
            return None
    return _check_if_token

class Keystone(object):
    _authed = False
    _session = None

    def __init__(self, request):
        self.request = request
        self.settings = from_settings(request.registry.settings)
        self.settings = { k: v for (k, v) in self.settings.items() if v }

    def _get_unscoped_session(self, token=None, username=None, password=None):
        try:
            auth_password = kc_v3.PasswordMethod(
                    user_domain_name=self.settings['user_domain_name'],
                    username=username,
                    password=password
                    )

            auth_token = kc_v3.TokenMethod(
                    token=token
                    )

            auth_methods = []

            if token is not None:
                auth_methods.append(auth_token)

            if username is not None and password is not None:
                auth_methods.append(auth_password)

            auth = kc_v3.Auth(auth_url=self.settings['auth_url'], auth_methods=auth_methods)

            sess = kc_session.Session(auth=auth)

            log.debug('Fetching unscoped token')
            unscoped_token = sess.get_token()
            log.debug('Fetched unscoped token: {}'.format(unscoped_token))

            if unscoped_token:
                self._authed = True
                self._session = sess
                self.request.session['keystone_token'] = unscoped_token
            else:
                if 'keystone_token' in self.request.session:
                    del self.request.session['keystone_token']
        except (kc_exceptions.Unauthorized, kc_exceptions.AuthorizationFailure) as e:
            return

    def get_scoped_session(self, project_id):
        try:
            auth_token = kc_v3.TokenMethod(token=self.unscoped_token)

            auth = kc_v3.Auth(auth_url=self.settings['auth_url'], auth_methods=[auth_token], project_id=project_id)

            sess = kc_session.Session(auth=auth)

            log.debug('Fetching scoped token')
            scoped_token = sess.get_token()
            log.debug('Fetched scoped token for "{}": {}'.format(scoped_token, project_id))

            return sess
        except (kc_exceptions.Unauthorized, kc_exceptions.AuthorizationFailure) as e:
            raise ValueError('Invalid or unauthorized unscoped token')

    @_kc_session_with_token
    def get_projects(self):
        ks = kc_client.Client(session=self._session)
        projects = [project.to_dict() for project in ks.projects.list(user=self.user_id)]

        return projects

    def authenticate(self, username, password):
        self._get_unscoped_session(username=username, password=password)

        if not self._authed:
            return False

        return True

    @_kc_session_with_token
    def revoke_all(self):
        if 'keystone_token' in self.request.session:
            del self.request.session['keystone_token']

    @property
    @_kc_session_with_token
    def username(self):
        return self._session.auth.auth_ref['user']['name']

    @property
    @_kc_session_with_token
    def user_id(self):
        return self._session.auth.auth_ref['user']['id']

    @property
    @_kc_session_with_token
    def unscoped_token(self):
        return self._session.get_token()
