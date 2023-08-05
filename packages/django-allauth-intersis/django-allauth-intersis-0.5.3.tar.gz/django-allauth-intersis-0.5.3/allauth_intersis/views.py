import requests

from django.conf import settings

from allauth.socialaccount import providers
from allauth.socialaccount.providers.oauth2.views import (OAuth2Adapter,
                                                          OAuth2LoginView,
                                                          OAuth2CallbackView)

from .provider import InterSISProvider

class InterSISOAuth2Adapter(OAuth2Adapter):
    provider_id = InterSISProvider.id
    access_token_url = settings.BASE_INTERSIS_SERVER_URL + '/o/token/'
    authorize_url = settings.BASE_INTERSIS_SERVER_URL + '/o/authorize/'
    profile_url = settings.BASE_INTERSIS_SERVER_URL + '/v.1/auth/user'
    supports_state = False
    redirect_uri_protocol = 'https'

    def complete_login(self, request, app, token, **kwargs):
        response = requests.get(self.profile_url,
                            params={'access_token': token})
        extra_data = response.json()
        if 'Profile' in extra_data:
            extra_data = {
                'user_id': extra_data['Profile']['CustomerId'],
                'name': extra_data['Profile']['Name'],
                'email': extra_data['Profile']['PrimaryEmail']
            }
        return self.get_provider().sociallogin_from_response(request, extra_data)


oauth2_login = OAuth2LoginView.adapter_view(InterSISOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(InterSISOAuth2Adapter)
