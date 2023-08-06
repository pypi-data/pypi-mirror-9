from pyramid.exceptions import ConfigurationError
from pyramid.interfaces import ISessionFactory

from .settings import parse_settings

def includeme(config):
    """ Set up standard configurator registrations.  Use via:

    .. code-block:: python

       config = Configurator()
       config.include('pyramid_keystone')

    """

    # We use an action so that the user can include us, and then add the
    # required variables, upon commit we will pick up those changes.
    def register():
        registry = config.registry
        settings = parse_settings(registry.settings)

        registry.settings.update(settings)

    def ensure():
        if config.registry.queryUtility(ISessionFactory) is None:
            raise ConfigurationError('pyramid_keystone requires a registered'
                    ' session factory. (use the set_session_factory method)')

    config.action('keystone-configure', register)
    # We need to make sure that this is executed after the default Pyramid
    # actions, because otherwise our Session Factory may not exist yet
    config.action(None, ensure, order=10)

    # Allow the user to use our auth policy (recommended)
    config.add_directive('keystone_auth_policy', '.authentication.add_auth_policy')

    # Add the keystone property to the request
    config.add_request_method('.keystone.request_keystone', name='keystone',
            property=True, reify=True)

