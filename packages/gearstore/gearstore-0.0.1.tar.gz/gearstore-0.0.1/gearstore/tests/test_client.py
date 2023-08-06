# -*- coding: utf-8 -*-

# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""
test_gearstore
----------------------------------

Tests for `gearstore.client` module.
"""

import json

import gear

from gearstore import client
from gearstore.tests import base


class TestGearstoreClient(base.TestCase):
    def setUp(self):
        super(TestGearstoreClient, self).setUp()
        self.server = gear.Server(0)

    def test_client(self):
        c = client.Client(client_id='test_client_client')
        c.addServer('127.0.0.1', port=self.server.port)
        w = gear.Worker(client_id='test_client_worker')
        w.addServer('127.0.0.1', port=self.server.port)
        c.waitForServer()
        w.waitForServer()
        j = gear.Job('test_forwarding', 'payload for forwarding')
        c.submitJob(j, background=False)
        # Now we're going to pretend to be a gearstore worker
        w.registerFunction(client.DEFAULT_STORE_FUNC)
        j = w.getJob()
        self.assertEqual(j.name, client.DEFAULT_STORE_FUNC)
        raw = j.arguments
        payload = json.loads(raw)
        self.assertIn('funcname', payload)
        self.assertIn('arg', payload)
        self.assertEqual('test_forwarding', payload['funcname'])
        self.assertEqual('payload for forwarding', payload['arg'])
