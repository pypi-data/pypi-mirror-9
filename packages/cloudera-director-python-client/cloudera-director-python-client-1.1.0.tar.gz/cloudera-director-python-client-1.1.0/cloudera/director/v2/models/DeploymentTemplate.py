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

class DeploymentTemplate:

    def __init__(self, **kwargs):
        self.swaggerTypes = {
            'configs': 'dict[str,dict[str,str]]',
            'enableEnterpriseTrial': 'bool',
            'externalDatabaseTemplates': 'dict[str,ExternalDatabaseTemplate]',
            'externalDatabases': 'dict[str,ExternalDatabase]',
            'hostname': 'str',
            'managerVirtualInstance': 'VirtualInstance',
            'name': 'str',
            'password': 'str',
            'port': 'int',
            'repository': 'str',
            'repositoryKeyUrl': 'str',
            'username': 'str'

        }


        #Optional configurations for Cloudera Manager and its management services
        self.configs = kwargs.get('configs',{}) # dict[str,dict[str,str]]
        #Whether to enable Cloudera Enterprise Trial
        self.enableEnterpriseTrial = kwargs.get('enableEnterpriseTrial',None) # bool
        #External database template definitions
        self.externalDatabaseTemplates = kwargs.get('externalDatabaseTemplates',{}) # dict[str,ExternalDatabaseTemplate]
        #External database definitions
        self.externalDatabases = kwargs.get('externalDatabases',{}) # dict[str,ExternalDatabase]
        #Hostname for existing Cloudera Manager installation
        self.hostname = kwargs.get('hostname',None) # str
        #Instance definition for a Cloudera Manager instance created from scratch
        self.managerVirtualInstance = kwargs.get('managerVirtualInstance',None) # VirtualInstance
        #Deployment name
        self.name = kwargs.get('name',None) # str
        #Web UI and API password [redacted on read]
        self.password = kwargs.get('password',None) # str
        #Port for existing Cloudera Manager installation
        self.port = kwargs.get('port',0) # int
        #Custom Cloudera Manager repository URL
        self.repository = kwargs.get('repository',None) # str
        #Custom Cloudera Manager public GPG key
        self.repositoryKeyUrl = kwargs.get('repositoryKeyUrl',None) # str
        #Web UI and API username
        self.username = kwargs.get('username',None) # str
        
