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

import sys
import os

from models import *


class ClustersApi(object):

    def __init__(self, apiClient):
      self.apiClient = apiClient

    

    def create(self, environment, deployment, clusterTemplate, **kwargs):
        """Create a new cluster

        Args:
            environment, str: environmentName (required)

            deployment, str: deploymentName (required)

            X-Request-Id, str: requestId (optional)

            clusterTemplate, ClusterTemplate: clusterTemplate (required)

            

        Returns: 
        """

        allParams = ['environment', 'deployment', 'X-Request-Id', 'clusterTemplate']

        params = locals()
        for (key, val) in params['kwargs'].iteritems():
            if key not in allParams:
                raise TypeError("Got an unexpected keyword argument '%s' to method create" % key)
            params[key] = val
        del params['kwargs']

        resourcePath = '/api/v2/environments/{environment}/deployments/{deployment}/clusters'
        resourcePath = resourcePath.replace('{format}', 'json')
        method = 'POST'

        queryParams = {}
        headerParams = {}

        if ('X-Request-Id' in params):
            headerParams['X-Request-Id'] = params['X-Request-Id']
        if ('environment' in params):
            replacement = str(self.apiClient.toPathValue(params['environment']))
            resourcePath = resourcePath.replace('{' + 'environment' + '}',
                                                replacement)
        if ('deployment' in params):
            replacement = str(self.apiClient.toPathValue(params['deployment']))
            resourcePath = resourcePath.replace('{' + 'deployment' + '}',
                                                replacement)
        postData = clusterTemplate

        response = self.apiClient.callAPI(resourcePath, method, queryParams,
                                          postData, headerParams)

        

        

    def delete(self, environment, deployment, cluster, **kwargs):
        """Delete a cluster by name

        Args:
            environment, str: environmentName (required)

            deployment, str: deploymentName (required)

            cluster, str: clusterName (required)

            X-Request-Id, str: requestId (optional)

            

        Returns: 
        """

        allParams = ['environment', 'deployment', 'cluster', 'X-Request-Id']

        params = locals()
        for (key, val) in params['kwargs'].iteritems():
            if key not in allParams:
                raise TypeError("Got an unexpected keyword argument '%s' to method delete" % key)
            params[key] = val
        del params['kwargs']

        resourcePath = '/api/v2/environments/{environment}/deployments/{deployment}/clusters/{cluster}'
        resourcePath = resourcePath.replace('{format}', 'json')
        method = 'DELETE'

        queryParams = {}
        headerParams = {}

        if ('X-Request-Id' in params):
            headerParams['X-Request-Id'] = params['X-Request-Id']
        if ('environment' in params):
            replacement = str(self.apiClient.toPathValue(params['environment']))
            resourcePath = resourcePath.replace('{' + 'environment' + '}',
                                                replacement)
        if ('deployment' in params):
            replacement = str(self.apiClient.toPathValue(params['deployment']))
            resourcePath = resourcePath.replace('{' + 'deployment' + '}',
                                                replacement)
        if ('cluster' in params):
            replacement = str(self.apiClient.toPathValue(params['cluster']))
            resourcePath = resourcePath.replace('{' + 'cluster' + '}',
                                                replacement)
        postData = None

        response = self.apiClient.callAPI(resourcePath, method, queryParams,
                                          postData, headerParams)

        

        

    def get(self, environment, deployment, cluster, **kwargs):
        """Get a cluster by name

        Args:
            environment, str: environmentName (required)

            deployment, str: deploymentName (required)

            cluster, str: clusterName (required)

            

        Returns: Cluster
        """

        allParams = ['environment', 'deployment', 'cluster']

        params = locals()
        for (key, val) in params['kwargs'].iteritems():
            if key not in allParams:
                raise TypeError("Got an unexpected keyword argument '%s' to method get" % key)
            params[key] = val
        del params['kwargs']

        resourcePath = '/api/v2/environments/{environment}/deployments/{deployment}/clusters/{cluster}'
        resourcePath = resourcePath.replace('{format}', 'json')
        method = 'GET'

        queryParams = {}
        headerParams = {}

        if ('environment' in params):
            replacement = str(self.apiClient.toPathValue(params['environment']))
            resourcePath = resourcePath.replace('{' + 'environment' + '}',
                                                replacement)
        if ('deployment' in params):
            replacement = str(self.apiClient.toPathValue(params['deployment']))
            resourcePath = resourcePath.replace('{' + 'deployment' + '}',
                                                replacement)
        if ('cluster' in params):
            replacement = str(self.apiClient.toPathValue(params['cluster']))
            resourcePath = resourcePath.replace('{' + 'cluster' + '}',
                                                replacement)
        postData = None

        response = self.apiClient.callAPI(resourcePath, method, queryParams,
                                          postData, headerParams)

        if not response:
            return None

        responseObject = self.apiClient.deserialize(response, 'Cluster')
        return responseObject
        

        

    def getStatus(self, environment, deployment, cluster, **kwargs):
        """Get a cluster status by name

        Args:
            environment, str: environmentName (required)

            deployment, str: deploymentName (required)

            cluster, str: clusterName (required)

            

        Returns: Status
        """

        allParams = ['environment', 'deployment', 'cluster']

        params = locals()
        for (key, val) in params['kwargs'].iteritems():
            if key not in allParams:
                raise TypeError("Got an unexpected keyword argument '%s' to method getStatus" % key)
            params[key] = val
        del params['kwargs']

        resourcePath = '/api/v2/environments/{environment}/deployments/{deployment}/clusters/{cluster}/status'
        resourcePath = resourcePath.replace('{format}', 'json')
        method = 'GET'

        queryParams = {}
        headerParams = {}

        if ('environment' in params):
            replacement = str(self.apiClient.toPathValue(params['environment']))
            resourcePath = resourcePath.replace('{' + 'environment' + '}',
                                                replacement)
        if ('deployment' in params):
            replacement = str(self.apiClient.toPathValue(params['deployment']))
            resourcePath = resourcePath.replace('{' + 'deployment' + '}',
                                                replacement)
        if ('cluster' in params):
            replacement = str(self.apiClient.toPathValue(params['cluster']))
            resourcePath = resourcePath.replace('{' + 'cluster' + '}',
                                                replacement)
        postData = None

        response = self.apiClient.callAPI(resourcePath, method, queryParams,
                                          postData, headerParams)

        if not response:
            return None

        responseObject = self.apiClient.deserialize(response, 'Status')
        return responseObject
        

        

    def getTemplateRedacted(self, environment, deployment, cluster, **kwargs):
        """Get a cluster template by name

        Args:
            environment, str: environmentName (required)

            deployment, str: deploymentName (required)

            cluster, str: clusterName (required)

            

        Returns: ClusterTemplate
        """

        allParams = ['environment', 'deployment', 'cluster']

        params = locals()
        for (key, val) in params['kwargs'].iteritems():
            if key not in allParams:
                raise TypeError("Got an unexpected keyword argument '%s' to method getTemplateRedacted" % key)
            params[key] = val
        del params['kwargs']

        resourcePath = '/api/v2/environments/{environment}/deployments/{deployment}/clusters/{cluster}/template'
        resourcePath = resourcePath.replace('{format}', 'json')
        method = 'GET'

        queryParams = {}
        headerParams = {}

        if ('environment' in params):
            replacement = str(self.apiClient.toPathValue(params['environment']))
            resourcePath = resourcePath.replace('{' + 'environment' + '}',
                                                replacement)
        if ('deployment' in params):
            replacement = str(self.apiClient.toPathValue(params['deployment']))
            resourcePath = resourcePath.replace('{' + 'deployment' + '}',
                                                replacement)
        if ('cluster' in params):
            replacement = str(self.apiClient.toPathValue(params['cluster']))
            resourcePath = resourcePath.replace('{' + 'cluster' + '}',
                                                replacement)
        postData = None

        response = self.apiClient.callAPI(resourcePath, method, queryParams,
                                          postData, headerParams)

        if not response:
            return None

        responseObject = self.apiClient.deserialize(response, 'ClusterTemplate')
        return responseObject
        

        

    def list(self, environment, deployment, **kwargs):
        """List all clusters

        Args:
            environment, str: environmentName (required)

            deployment, str: deploymentName (required)

            

        Returns: list[str]
        """

        allParams = ['environment', 'deployment']

        params = locals()
        for (key, val) in params['kwargs'].iteritems():
            if key not in allParams:
                raise TypeError("Got an unexpected keyword argument '%s' to method list" % key)
            params[key] = val
        del params['kwargs']

        resourcePath = '/api/v2/environments/{environment}/deployments/{deployment}/clusters'
        resourcePath = resourcePath.replace('{format}', 'json')
        method = 'GET'

        queryParams = {}
        headerParams = {}

        if ('environment' in params):
            replacement = str(self.apiClient.toPathValue(params['environment']))
            resourcePath = resourcePath.replace('{' + 'environment' + '}',
                                                replacement)
        if ('deployment' in params):
            replacement = str(self.apiClient.toPathValue(params['deployment']))
            resourcePath = resourcePath.replace('{' + 'deployment' + '}',
                                                replacement)
        postData = None

        response = self.apiClient.callAPI(resourcePath, method, queryParams,
                                          postData, headerParams)

        if not response:
            return None

        responseObject = self.apiClient.deserialize(response, 'list[str]')
        return responseObject
        

        

    def update(self, environment, deployment, cluster, desired, **kwargs):
        """Update an existing cluster

        Args:
            environment, str: environmentName (required)

            deployment, str: deploymentName (required)

            cluster, str: clusterName (required)

            X-Request-Id, str: requestId (optional)

            desired, ClusterTemplate: desired (required)

            

        Returns: 
        """

        allParams = ['environment', 'deployment', 'cluster', 'X-Request-Id', 'desired']

        params = locals()
        for (key, val) in params['kwargs'].iteritems():
            if key not in allParams:
                raise TypeError("Got an unexpected keyword argument '%s' to method update" % key)
            params[key] = val
        del params['kwargs']

        resourcePath = '/api/v2/environments/{environment}/deployments/{deployment}/clusters/{cluster}'
        resourcePath = resourcePath.replace('{format}', 'json')
        method = 'PUT'

        queryParams = {}
        headerParams = {}

        if ('X-Request-Id' in params):
            headerParams['X-Request-Id'] = params['X-Request-Id']
        if ('environment' in params):
            replacement = str(self.apiClient.toPathValue(params['environment']))
            resourcePath = resourcePath.replace('{' + 'environment' + '}',
                                                replacement)
        if ('deployment' in params):
            replacement = str(self.apiClient.toPathValue(params['deployment']))
            resourcePath = resourcePath.replace('{' + 'deployment' + '}',
                                                replacement)
        if ('cluster' in params):
            replacement = str(self.apiClient.toPathValue(params['cluster']))
            resourcePath = resourcePath.replace('{' + 'cluster' + '}',
                                                replacement)
        postData = desired

        response = self.apiClient.callAPI(resourcePath, method, queryParams,
                                          postData, headerParams)

        

        

    




