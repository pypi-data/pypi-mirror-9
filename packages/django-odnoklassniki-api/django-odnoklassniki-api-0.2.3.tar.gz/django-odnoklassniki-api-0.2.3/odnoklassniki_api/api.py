# -*- coding: utf-8 -*-
from django.conf import settings
from oauth_tokens.api import ApiAbstractBase, Singleton
from odnoklassniki import api, OdnoklassnikiError
from simplejson.decoder import JSONDecodeError

__all__ = ['api_call', 'OdnoklassnikiError']

APPLICATION_PUBLIC = getattr(settings, 'OAUTH_TOKENS_ODNOKLASSNIKI_CLIENT_PUBLIC', '')
APPLICATION_SECRET = getattr(settings, 'OAUTH_TOKENS_ODNOKLASSNIKI_CLIENT_SECRET', '')


class OdnoklassnikiApi(ApiAbstractBase):

    __metaclass__ = Singleton

    provider = 'odnoklassniki'
    error_class = OdnoklassnikiError
    error_class_repeat = tuple(list(ApiAbstractBase.error_class_repeat) + [JSONDecodeError])

    def get_consistent_token(self):
        return getattr(settings, 'ODNOKLASSNIKI_API_ACCESS_TOKEN', None)

    def get_api(self, token):
        return api.Odnoklassniki(application_key=APPLICATION_PUBLIC, application_secret=APPLICATION_SECRET, token=token)

    def get_api_response(self, *args, **kwargs):
        return self.api._get(self.method, *args, **kwargs)

    def handle_error_code(self, e, *args, **kwargs):
        if e.code is None and e.message == 'HTTP error':
            return self.sleep_repeat_call(*args, **kwargs)
        else:
            return super(OdnoklassnikiApi, self).handle_error_code(e, *args, **kwargs)

    def handle_error_code_2(self, e, *args, **kwargs):
        # SERVICE : Service is temporary unavailable., logged by ID :
        return self.sleep_repeat_call(*args, **kwargs)

    def handle_error_code_8(self, e, *args, **kwargs):
        # FLOOD_BLOCKED : Call blocked due to flood protection
        return self.sleep_repeat_call(*args, **kwargs)

    def handle_error_code_102(self, e, *args, **kwargs):
        # PARAM_SESSION_EXPIRED : Session expired
        self.refresh_tokens()
        return self.repeat_call(*args, **kwargs)


def api_call(*args, **kwargs):
    api = OdnoklassnikiApi()
    return api.call(*args, **kwargs)
