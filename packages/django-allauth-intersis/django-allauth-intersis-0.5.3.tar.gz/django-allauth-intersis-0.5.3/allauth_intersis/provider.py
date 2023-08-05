from django.core.exceptions import ObjectDoesNotExist
from django.contrib.sites.models import Site
from django.conf import settings

from allauth.socialaccount import providers
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider
from allauth.socialaccount.models import SocialApp


class InterSISAccount(ProviderAccount):
    def to_str(self):
        return self.account.extra_data.get('name',
                                           super(InterSISAccount, self).to_str())


class InterSISProvider(OAuth2Provider):
    id = 'intersis'
    name = 'InterSIS'
    package = 'allauth_intersis'
    account_class = InterSISAccount

    def get_app(self, request):
        """
        Retrieve the social app credentials from the database, if they exist; register with the authorization
        server if they do not.

        The InterSIS spec includes automated registration of client applications. Future versions of this package
        will allow resource owners to specify the location of their InterSIS compliant server; if the client
        has not yet registered with that server (except ObjectDoesNotExist) then it will attempt to do so at
        /v.1/auth/clients.
        """
        try:
            return SocialApp.objects.get_current(self.id)
        except ObjectDoesNotExist:
            import urllib.parse
            import urllib.request
            import json

            url = settings.BASE_INTERSIS_SERVER_URL + '/v.1/auth/clients/'
            data = urllib.parse.urlencode({
                'name': settings.INTERSIS_CLIENT_NAME,
                'redirect_uris': settings.BASE_INTERSIS_CLIENT_URL + '/intersis/login/callback/',
                })

            data = data.encode('utf-8')  # data should be bytes
            req = urllib.request.Request(url, data)
            response = json.loads(urllib.request.urlopen(req).readall().decode('utf-8'))

            this_app = SocialApp.objects.create(
                provider=self.id,
                name=self.id,
                client_id=response["client_id"],
                secret=response["client_secret"],
            )

            this_app.sites.add(Site.objects.get_current())

            return this_app


    def get_default_scope(self):
        return ['read']

    def extract_uid(self, data):
        return str(data['id'])

    def extract_common_fields(self, data):
        # Hackish way of splitting the fullname.
        # Assumes no middlenames.
        # name = data.get('name', '')
        # first_name, last_name = name, ''
        # if name and ' ' in name:
        #     first_name, last_name = name.split(' ', 1)
        return dict(email="stand_in@example.com",
                    last_name="stand_in",
                    first_name="stand_in")

providers.registry.register(InterSISProvider)
