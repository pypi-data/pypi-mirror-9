#!/usr/bin/env python

# Licensed to Cloudera, Inc. under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  Cloudera, Inc. licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Note: This file is auto generated. Do not edit manually.

class ExternalDatabaseServerTemplate:

    def __init__(self, **kwargs):
        self.swaggerTypes = {
            'config': 'dict[str,str]',
            'hostname': 'str',
            'name': 'str',
            'password': 'str',
            'port': 'int',
            'tags': 'dict[str,str]',
            'type': 'str',
            'username': 'str'

        }


        self.config = kwargs.get('config',{}) # dict[str,str]
        #Hostname for existing external database server
        self.hostname = kwargs.get('hostname',None) # str
        #External database server name
        self.name = kwargs.get('name',None) # str
        #Database password for administrative access [redacted on read]
        self.password = kwargs.get('password',None) # str
        #Port for an existing external database server
        self.port = kwargs.get('port',0) # int
        self.tags = kwargs.get('tags',{}) # dict[str,str]
        #External database server type
        self.type = kwargs.get('type',None) # str
        #Database username for administrative access
        self.username = kwargs.get('username',None) # str
        
