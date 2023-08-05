"""
Tests - Deuce Client - Client - Deuce - Init
"""
import json

import httpretty
import requests

import deuceclient.client.deuce
from deuceclient.tests import *


class ClientDeuceInitTests(ClientTestBase):

    def setUp(self):
        super(ClientDeuceInitTests, self).setUp()

        self.client = deuceclient.client.deuce.DeuceClient(self.authenticator,
                                                           self.apihost,
                                                           sslenabled=True)

    def tearDown(self):
        super(ClientDeuceInitTests, self).tearDown()

    def test_init_ssl_correct_uri(self):
        self.assertIn('X-Deuce-User-Agent', self.client.headers)
        self.assertIn('User-Agent', self.client.headers)
        self.assertEqual(self.expected_agent,
                         self.client.headers['X-Deuce-User-Agent'])
        self.assertEqual(self.expected_agent,
                         self.client.headers['User-Agent'])
        self.assertEqual(self.client.headers['X-Deuce-User-Agent'],
                         self.client.headers['User-Agent'])

        self.assertEqual(self.expected_uri,
                         self.client.uri)
        self.assertEqual(self.authenticator.AuthTenantId,
                         self.client.project_id)

    def test_log_request(self):
        self.client._DeuceClient__log_request_data()

        self.client._DeuceClient__log_request_data(fn=None)

        self.client._DeuceClient__log_request_data(fn=None,
                                                   headers=None)

        self.client._DeuceClient__log_request_data(fn='howdy',
                                                   headers=None)

        self.client._DeuceClient__log_request_data(fn='doody',
                                                   headers={'X-Car': 'humvee'})

        self.client._DeuceClient__log_request_data(headers={
                                                   'X-Rug': 'bearskin'})

    @httpretty.activate
    def test_log_response(self):
        resp_uri = 'http://log.response/'
        resp_data = {'field': 'value'}

        httpretty.register_uri(httpretty.GET,
                               resp_uri,
                               content_type="application/json",
                               body=json.dumps(resp_data),
                               status=200)
        response = requests.get(resp_uri)

        self.client._DeuceClient__log_response_data(response)
        self.client._DeuceClient__log_response_data(response,
                                                    jsondata=True)
        self.client._DeuceClient__log_response_data(response,
                                                    fn='transformers')
        self.client._DeuceClient__log_response_data(response,
                                                    jsondata=True,
                                                    fn='strawberry')
        self.client._DeuceClient__log_response_data(response,
                                                    jsondata=False,
                                                    fn='shortcake')

    @httpretty.activate
    def test_log_response_zero_length_content(self):
        resp_uri = 'http://log.response/'

        httpretty.register_uri(httpretty.GET,
                               resp_uri,
                               content_type="application/json",
                               body='',
                               status=200)
        response = requests.get(resp_uri)
        self.client._DeuceClient__log_response_data(response,
                                                    jsondata=False,
                                                    fn='bears')
