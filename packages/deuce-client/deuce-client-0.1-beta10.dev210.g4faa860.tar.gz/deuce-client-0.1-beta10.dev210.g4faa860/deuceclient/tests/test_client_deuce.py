"""
Tests - Deuce Client - Client - Deuce
"""
import json

import httpretty

import deuceclient.api as api
import deuceclient.api.vault as api_vault
from deuceclient.tests import *


class DeuceClientTests(ClientTestBase):

    def setUp(self):
        super(DeuceClientTests, self).setUp()

    def tearDown(self):
        super(DeuceClientTests, self).tearDown()

    """
    Keeping temporarily for merge purposes
    To be Removed
    """
