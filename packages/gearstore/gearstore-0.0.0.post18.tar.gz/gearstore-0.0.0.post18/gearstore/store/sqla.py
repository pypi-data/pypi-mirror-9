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
import sqlalchemy as sa
from sqlalchemy import exc as sa_exc
from sqlalchemy import orm
from sqlalchemy.orm import exc

from gearstore.store import sqla_models as models

_session = None


class Store(object):
    def __init__(self, details):
        self._engine = sa.create_engine(details)
        self._sessionmaker = orm.sessionmaker(bind=self._engine)
        self.session = orm.scoped_session(self._sessionmaker)

    def initialize_schema(self):
        models.Base.metadata.create_all(self._engine)

    def save(self, job):
        # Storing as binary for more efficient usage in MySQL particularly
        for k in ('unique', 'funcname', 'arg'):
            if job.get(k) is not None and (isinstance(job.get(k), str) or
                                           isinstance(job.get(k), unicode)):
                job[k] = job[k].encode('utf-8')
        j = models.Job(id=job.get('unique'), funcname=job.get('funcname'),
                       arg=job.get('arg'))
        sess = self.session()
        try:
            sess.add(j)
            # XXX: allow commit in batches some day
            sess.commit()
        except sa_exc.IntegrityError:
            sess.rollback()
            # We don't actually care, because it means we already have this
            # unique job ID
            pass

    def consume(self, batchlimit=1000):
        sess = self.session()
        for rec in range(0, batchlimit):
            try:
                j = sess.query(models.Job).limit(1).one()
            except exc.NoResultFound:
                return
            yield {'unique': j.id, 'funcname': j.funcname, 'arg': j.arg}
            sess.delete(j)
            # XXX: allow committing deletes in batches some day
            sess.commit()
