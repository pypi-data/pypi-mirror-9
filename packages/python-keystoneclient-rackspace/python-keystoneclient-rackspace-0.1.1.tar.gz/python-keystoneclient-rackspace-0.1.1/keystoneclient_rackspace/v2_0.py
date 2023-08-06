from keystoneclient.auth.identity import v2
from oslo_config import cfg


class RackspaceAuth(v2.Auth):
    """A plugin for authenticating with a username and API key.

    A username or user_id must be provided.

    :param string auth_url: Identity service endpoint for authorization.
    :param string username: Username for authentication.
    :param string api_key: API key for authentication.
    :param string tenant_id: Optional tenant_id.

    :raises TypeError: if a api_key or username is not provided.
    """

    def __init__(self, auth_url, username=None, api_key=None, tenant_id=None,
                 **kwargs):
        super(RackspaceAuth, self).__init__(auth_url, **kwargs)

        if username is None:
            msg = 'You need to specify a username'
            raise TypeError(msg)
        if api_key is None:
            msg = 'You need to specify an API key'
            raise TypeError(msg)

        self.username = username
        self.api_key = api_key
        self.tenant_id = tenant_id

    def get_auth_data(self, headers=None):
        auth = {'RAX-KSKEY:apiKeyCredentials': {
                        'username': self.username,
                        'apiKey': self.api_key
                    }
                }
        if self.tenant_id:
            auth['tenantId'] = self.tenant_id
        return auth

    @classmethod
    def get_options(cls):
        options = super(RackspaceAuth, cls).get_options()

        options.extend([
            cfg.StrOpt('user-name',
                       dest='username',
                       deprecated_name='username',
                       help='Username to login with'),
            cfg.StrOpt('apikey',
                       dest='api_key',
                       secret=True,
                       help='API key to use'),
            cfg.StrOpt('tenant-id',
                       dest='tenant_id',
                       help='Tenant ID to login with'),
        ])
        return options
