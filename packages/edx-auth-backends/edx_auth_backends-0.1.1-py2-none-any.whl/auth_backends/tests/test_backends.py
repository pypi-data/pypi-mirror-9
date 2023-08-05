from django.conf import settings
from social.tests.backends.oauth import OAuth2Test
from social.tests.backends.open_id import OpenIdConnectTestMixin


class EdXOpenIdConnectTests(OpenIdConnectTestMixin, OAuth2Test):
    backend_path = 'auth_backends.backends.EdXOpenIdConnect'
    issuer = getattr(settings, 'SOCIAL_AUTH_EDX_OIDC_URL_ROOT', None)
    expected_username = 'test_user'

    def get_id_token(self, *args, **kwargs):
        data = super(EdXOpenIdConnectTests, self).get_id_token(*args, **kwargs)

        # Set the field used to derive the username of the logged user.
        data['preferred_username'] = self.expected_username

        return data

    def test_login(self):
        user = self.do_login()
        self.assertIsNotNone(user)
