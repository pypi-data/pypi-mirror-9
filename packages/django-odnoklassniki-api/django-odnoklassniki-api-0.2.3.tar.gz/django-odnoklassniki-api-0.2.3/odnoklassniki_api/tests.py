# -*- coding: utf-8 -*-
from django.test import TestCase
import mock

from .api import api_call, OdnoklassnikiApi

GROUP_ID = 53038939046008


class OdnoklassnikiApiTest(TestCase):

    def test_api_instance_singleton(self):

        self.assertEqual(id(OdnoklassnikiApi()), id(OdnoklassnikiApi()))

    def test_get_url_info(self):

        response = api_call('url.getInfo', url='http://www.odnoklassniki.ru/apiok')
        self.assertEqual(response, {u'objectId': GROUP_ID, u'type': u'GROUP'})

    @mock.patch('odnoklassniki.api.Odnoklassniki._request', side_effect=lambda *args, **kwargs: (200, {u'error_data': None, u'error_code': 102, u'error_msg': u'PARAM_SESSION_EXPIRED : Session expired'}))
    @mock.patch('odnoklassniki_api.api.OdnoklassnikiApi.handle_error_code_102')
    def test_error_102(self, request, handle_error):

        response = api_call('url.getInfo', url='http://www.odnoklassniki.ru/apiok')
        self.assertTrue(handle_error.called)
