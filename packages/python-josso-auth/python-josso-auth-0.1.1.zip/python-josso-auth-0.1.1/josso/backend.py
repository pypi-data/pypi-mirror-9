import os
import six
from social.backends.base import BaseAuth
from suds.client import Client

WSDL_DIR = os.path.join(os.path.dirname(__file__), 'wsdl')


class JOSSOAuth(BaseAuth):
    """
    Base JOSSO authentication backend for python-social-auth. Override and set BASE_URL to implement specific
    JOSSO providers
    """

    ID_KEY = 'email'

    name = ''
    base_url = ''

    def get_wsdl_url(self, name):
        return 'file:{0}'.format(os.path.join(WSDL_DIR, name))

    def get_base_url(self):
        if not self.base_url.endswith('/'):
            self.base_url += '/'
        return self.base_url

    def auth_url(self):
        return '{0}signon/login.do?{1}'.format(
            self.get_base_url(), six.moves.urllib.parse.urlencode({'josso_back_to': self.redirect_uri})
        )

    def auth_complete(self, *args, **kwargs):
        ident_provider_client = Client(
            url=self.get_wsdl_url('SSOIdentityProvider.xml'),
            location='{0}services/SSOIdentityProvider?wsdl'.format(self.get_base_url())
        )
        ident_manager_client = Client(
            url=self.get_wsdl_url('SSOIdentityManager.xml'),
            location='{0}services/SSOIdentityManager?wsdl'.format(self.get_base_url())
        )

        josso_session_id = str(ident_provider_client.service.resolveAuthenticationAssertion(
            self.data.get('josso_assertion_id')
        ))
        josso_user_info = ident_manager_client.service.findUserInSession(josso_session_id)

        data = {
            'username': josso_user_info.name,
            'session_id': josso_session_id
        }
        data.update({str(p.name): str(p.value) for p in josso_user_info.properties})
        response = kwargs.get('response') or {}
        response.update(data)
        kwargs.update({'response': response, 'backend': self})
        return self.strategy.authenticate(*args, **kwargs)

    def get_user_details(self, response):
        return {
            'username': response['username'].split('@', 1)[0],
            'email': response.get('email', ''),
            'fullname': response.get('displayName')
        }

    def extra_data(self, user, uid, response, details=None):
        data = super(JOSSOAuth, self).extra_data(user, uid, response, details)
        data['session_id'] = response.get('session_id')
        return data