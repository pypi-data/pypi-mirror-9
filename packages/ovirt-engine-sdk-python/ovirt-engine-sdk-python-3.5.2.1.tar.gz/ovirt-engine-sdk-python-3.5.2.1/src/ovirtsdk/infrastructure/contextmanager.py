#
# Copyright (c) 2010 Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#           http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from ovirtsdk.utils.ordereddict import OrderedDict
from ovirtsdk.infrastructure.cache import Cache
import threading


class ContextManager(OrderedDict):
    """ The oVirt context manager """

    def __init__(self):
        OrderedDict.__init__(self)
        self.__lock = threading.RLock()

    def __getitem__(self, key):
        with self.__lock:
            if key not in self.data.keys():
                OrderedDict.__setitem__(self, key, Cache())
        return OrderedDict.__getitem__(self, key)

    def drop(self, key):
        """
        Removes specified context

        @param key: the context id
        """
        item = self.__getitem__(key)
        item.clear(force=True)
        self.pop(key)
