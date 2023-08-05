"""
Tests - Deuce Client  - Version
"""

from unittest import TestCase

import deuceclient


class VersionTest(TestCase):

    def test_version(self):

        deuce_client_version = deuceclient.version()

        version_data = deuce_client_version.split('.')

        self.assertEqual(int(version_data[0]),
                         deuceclient.__DEUCECLIENT_VERSION__['major'])

        self.assertEqual(int(version_data[1]),
                         deuceclient.__DEUCECLIENT_VERSION__['minor'])

        self.assertEqual(len(version_data),
                         len(deuceclient.__DEUCECLIENT_VERSION__))
