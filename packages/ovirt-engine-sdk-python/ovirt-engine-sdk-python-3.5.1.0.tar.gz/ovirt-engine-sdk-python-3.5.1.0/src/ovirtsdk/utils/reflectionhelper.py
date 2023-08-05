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

import inspect
import thread

class ReflectionHelper():
    cache = {}
    __plock = thread.allocate_lock()
    '''Provides reflection capabilities'''
    @staticmethod
    def getClasses(module, byName=False):
        '''
        Retrieves module members
        
        @param module: the name of the module for lookup
        '''
        known_wrapper_types = {}
        for name, obj in inspect.getmembers(module, inspect.isclass):
            known_wrapper_types[name.lower()] = name if byName is True \
                                                     else obj

        return known_wrapper_types

    @staticmethod
    def getClassNames(module):
        '''
        Retrieves module member's names key:val pairs
        
        @param module: the name of the module for lookup
        '''
        return ReflectionHelper.getClasses(module, True)

    @staticmethod
    def isModuleMember(module, typ, invalidate=False):
        '''
        Checks if specific type exist in given module
        
        @param module: the name of the module for lookup
        @param typ: the type to check
        @param invalidate: force cache invalidation
        '''
        with ReflectionHelper.__plock:
            if invalidate or (module not in ReflectionHelper.cache.keys() or \
               (len(inspect.getmembers(module, inspect.isclass)) > len(ReflectionHelper.cache[module]))):
                ReflectionHelper.cache[module] = ReflectionHelper.getClasses(module)
            if ReflectionHelper.cache[module].has_key(typ.__name__.lower()) and \
               ReflectionHelper.cache[module][typ.__name__.lower()] == typ:
                return True
            return False
