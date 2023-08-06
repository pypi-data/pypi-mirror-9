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

import gear

DEFAULT_STORE_FUNC = 'gearstore_store_job'


class Client(gear.Client):
    '''Convenience class to allow submitting gearstored jobs with the
       same API as gear'''

    def submitJob(self, job, background=None,
                  precedence=gear.PRECEDENCE_NORMAL,
                  timeout=30):
        arguments = json.dumps({'funcname': job.name, 'arg': job.arguments})
        job.name = DEFAULT_STORE_FUNC
        job.arguments = arguments
        return super(Client, self).submitJob(job, background,
                                             precedence, timeout)
