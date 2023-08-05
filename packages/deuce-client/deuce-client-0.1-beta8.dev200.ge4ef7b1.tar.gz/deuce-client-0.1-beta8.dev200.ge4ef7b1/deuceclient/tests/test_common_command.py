"""
Tests - Deuce Client - Common - Command
"""
import mock
from unittest import TestCase

import deuceclient
import deuceclient.common.command


class CommandTest(TestCase):

    def test_init_nonssl_incorrect_uri(self):
        deuceclient_version = 'deuce_version'
        apihost = 'myapi'
        uripath = 'someuri'
        expected_agent = 'Deuce-Client/{0:}'.format(deuceclient_version)
        expected_uri = "http://" + apihost + '/' + uripath

        with mock.patch('deuceclient.version') as mock_deuceversion:
            mock_deuceversion.return_value = deuceclient_version

            command = deuceclient.common.command.Command(apihost,
                                                         uripath,
                                                         False)
            self.assertIn('X-Deuce-User-Agent', command.headers)
            self.assertIn('User-Agent', command.headers)
            self.assertEqual(expected_agent,
                             command.headers['X-Deuce-User-Agent'])
            self.assertEqual(expected_agent,
                             command.headers['User-Agent'])
            self.assertEqual(command.headers['X-Deuce-User-Agent'],
                             command.headers['User-Agent'])

            self.assertEqual(expected_uri,
                             command.uri)

    def test_init_nonssl_correct_uri(self):
        deuceclient_version = 'deuce_version'
        apihost = 'myapi'
        uripath = '/someuri'
        expected_agent = 'Deuce-Client/{0:}'.format(deuceclient_version)
        expected_uri = "http://" + apihost + uripath

        with mock.patch('deuceclient.version') as mock_deuceversion:
            mock_deuceversion.return_value = deuceclient_version

            command = deuceclient.common.command.Command(apihost,
                                                         uripath,
                                                         False)
            self.assertIn('X-Deuce-User-Agent', command.headers)
            self.assertIn('User-Agent', command.headers)
            self.assertEqual(expected_agent,
                             command.headers['X-Deuce-User-Agent'])
            self.assertEqual(expected_agent,
                             command.headers['User-Agent'])
            self.assertEqual(command.headers['X-Deuce-User-Agent'],
                             command.headers['User-Agent'])

            self.assertEqual(expected_uri,
                             command.uri)

    def test_init_ssl_incorrect_uri(self):
        deuceclient_version = 'deuce_version'
        apihost = 'myapi'
        uripath = 'someuri'
        expected_agent = 'Deuce-Client/{0:}'.format(deuceclient_version)
        expected_uri = "https://" + apihost + '/' + uripath

        with mock.patch('deuceclient.version') as mock_deuceversion:
            mock_deuceversion.return_value = deuceclient_version

            command = deuceclient.common.command.Command(apihost,
                                                         uripath,
                                                         True)
            self.assertIn('X-Deuce-User-Agent', command.headers)
            self.assertIn('User-Agent', command.headers)
            self.assertEqual(expected_agent,
                             command.headers['X-Deuce-User-Agent'])
            self.assertEqual(expected_agent,
                             command.headers['User-Agent'])
            self.assertEqual(command.headers['X-Deuce-User-Agent'],
                             command.headers['User-Agent'])

            self.assertEqual(expected_uri,
                             command.uri)

    def test_init_ssl_correct_uri(self):
        deuceclient_version = 'deuce_version'
        apihost = 'myapi'
        uripath = '/someuri'
        expected_agent = 'Deuce-Client/{0:}'.format(deuceclient_version)
        expected_uri = "https://" + apihost + uripath

        with mock.patch('deuceclient.version') as mock_deuceversion:
            mock_deuceversion.return_value = deuceclient_version

            command = deuceclient.common.command.Command(apihost,
                                                         uripath,
                                                         True)
            self.assertIn('X-Deuce-User-Agent', command.headers)
            self.assertIn('User-Agent', command.headers)
            self.assertEqual(expected_agent,
                             command.headers['X-Deuce-User-Agent'])
            self.assertEqual(expected_agent,
                             command.headers['User-Agent'])
            self.assertEqual(command.headers['X-Deuce-User-Agent'],
                             command.headers['User-Agent'])

            self.assertEqual(expected_uri,
                             command.uri)

    def test_basics(self):
        deuceclient_version = deuceclient.version()
        apihost = 'myapi'
        uripath = '/someuri'
        expected_agent = 'Deuce-Client/{0:}'.format(deuceclient_version)
        expected_uri = "https://" + apihost + uripath

        with mock.patch('deuceclient.version') as mock_deuceversion:
            mock_deuceversion.return_value = deuceclient_version

            command = deuceclient.common.command.Command(apihost,
                                                         uripath,
                                                         True)
            self.assertIn('X-Deuce-User-Agent', command.headers)
            self.assertIn('User-Agent', command.headers)
            self.assertEqual(expected_agent,
                             command.headers['X-Deuce-User-Agent'])
            self.assertEqual(expected_agent,
                             command.headers['User-Agent'])
            self.assertEqual(command.headers['X-Deuce-User-Agent'],
                             command.headers['User-Agent'])

            self.assertEqual(expected_uri,
                             command.uri)

            self.assertEqual(expected_uri, command.Uri)
            self.assertEqual(command.headers, command.Headers)
            self.assertEqual(apihost, command.ApiHost)
            self.assertIsNone(command.body)
            self.assertIsNone(command.Body)
            self.assertEqual(command.body, command.Body)
