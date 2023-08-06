# Copyright (c) 2015 Hewlett-Packard Development Company, L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import logging
import time
import uuid

import gear

from gearstore import client
from gearstore.store import sqla


class Stocker(object):
    '''A combination gearman worker and client that stores all received jobs in
       a database and then submits any jobs stored in the database to the
       intended destination queue.'''
    def __init__(self, client_id=None, worker_id=None, dsn=None):
        self.dsn = dsn
        self._store = sqla.Store(self.dsn)
        self.worker = gear.Worker(client_id or worker_id)
        client_id_client = '%s_shipper' % (client_id or worker_id)
        self.client = gear.Client(client_id_client)
        self._log = logging.getLogger('gearstore.stocker')

    def addServer(self, *args, **kwargs):
        self.worker.addServer(*args, **kwargs)
        self.client.addServer(*args, **kwargs)

    def waitForServer(self):
        self.worker.waitForServer()
        self.client.waitForServer()

    def registerStoreFunction(self):
        self.worker.registerFunction(client.DEFAULT_STORE_FUNC)

    def stock(self):
        job = self.worker.getJob()
        payload = json.loads(job.arguments)
        unique = job.unique or bytes(uuid.uuid4())
        payload['unique'] = unique
        try:
            self._store.save(payload)
            job.sendWorkComplete(data=unique)
            self._log.info('stocked %s' % str(job))
        except Exception as e:
            self._log.exception(e)
            job.sendWorkException(bytes(str(e).encode('utf-8')))

    def ship(self):
        try:
            for job in self._store.consume():
                gjob = gear.Job(job['funcname'], job['arg'], job['unique'])
                self.client.submitJob(gjob)
                # We now need to wait for the completion of that job before we
                # reenter the consume generator which causes the record to be
                # deleted.
                while not gjob.complete:
                    time.sleep(0.1)  # XXX: We need gear.Client to help
                if gjob.failure:
                    if gjob.exception:
                        raise RuntimeError('Job failed due to exception (%s)'
                                           ' and will be retried.'
                                           % gjob.exception)
                    else:
                        raise RuntimeError('Job failed and will be retried.')
                self._log.info('shipped %s' % str(job))
        except (gear.GearmanError, RuntimeError) as e:
            self._log.exception(e)
            # We would have broken out of consume, so no changes would be made
            # to the db, and another instance of consume will pick it up and
            # retry. So just let this ship() call exit, and the next polling
            # interval will retry.
