# Copyright 2014 MongoDB, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging

logger = logging.getLogger('giza.content.steps.inheritance')

from giza.core.inheritance import InheritableContentError, DataContentBase, DataCache
from giza.content.steps.models import StepData

class StepError(Exception): pass

class StepFile(DataContentBase):
    content_class = StepData

    @property
    def steps(self):
        if not hasattr(self, '_ordered_content'):
            self._ordered_content = []

        if len(self._ordered_content) == 0:
            ret = []

            for step in self.content.values():
                step.resolve(self.data)
                ret.append((step.number, step))

            def sorter(x, y):
                return cmp(x[0], y[0])

            ret.sort(cmp=lambda x,y: cmp(x[0], y[0]))
            self._ordered_content = [ r for idx, r in ret ]

        return self._ordered_content

    def add(self, doc):
        content = super(StepFile, self).add(doc)

        if not hasattr(self, '_step_counter'):
            self._step_counter = 1
        else:
            self._step_counter += 1

        obj = self.content[content.ref]

        if 'number' not in obj:
            obj.number = self._step_counter

        return obj

class StepDataCache(DataCache):
    content_class = StepFile
