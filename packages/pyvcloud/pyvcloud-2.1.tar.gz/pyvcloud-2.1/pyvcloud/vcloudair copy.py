# VMware vCloud Python SDK
# Copyright (c) 2014 VMware, Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# coding: utf-8

import base64
import requests
import StringIO
import json
# from pyvcloud.schema.vcim import serviceType, vchsType
from pyvcloud.schema.vcd.v1_5.schemas.vcloud import sessionType, organizationType, organizationListType
# from pyvcloud.vclouddirector import VCD
# from pyvcloud.schema.vcim.serviceType import ServiceType

class VCA(object):

    def __init__(self, service_type='ondemand', version='5.7'):
        self.host = None
        self.username = None
        self.token = None
        self.token_vcd = None
        self.service_type = service_type
        self.version = version
        self.session = None
        self.org = None
        self.api_url = None
        self.instance = None
        self.plans = None
        
    def re_login(self, api_url, token_vcd, version, verify=True):
        headers = {}
        headers["x-vcloud-authorization"] = token_vcd
        headers["Accept"] = "application/*+xml;version=" + version
        response = requests.get(api_url, headers=headers, verify=verify)
        if response.status_code == requests.codes.ok:
            self.session = sessionType.parseString(response.content, True)
            return True
        else:
            return False                

    def login(self, host, username, password, token=None, token_vcd=None, service_type='ondemand', version='5.7', verify=True):
        """
        Request to login to vCloud Air
        
        :param host: URL of the vCloud service, for example: vca.vmware.com.
        :param username: The user name.
        :param password: The password.
        :param token: The token from a previous successful login, None if this is a new login request.                        
        :return: True if the user was successfully logged in, False otherwise.
        """

        if not (host.startswith('https://') or host.startswith('http://')):
            host = 'https://' + host
            
        if service_type == 'subscription':
            if token_vcd:
                headers = {}
                headers["x-vchs-authorization"] = token_vcd
                headers["Accept"] = "application/xml;version=" + version
                response = requests.get(host + "/api/vchs/services", headers=headers, verify=verify)
                if response.status_code == requests.codes.ok:
                    self.host = host
                    self.token_vcd = token_vcd
                    self.service_type = service_type
                    self.version = version
                    return True
                else:
                    return False
            else:
                url = host + "/api/vchs/sessions"
                encode = "Basic " + base64.standard_b64encode(username + ":" + password)
                headers = {}
                headers["Authorization"] = encode.rstrip()
                headers["Accept"] = "application/xml;version=" + version
                response = requests.post(url, headers=headers, verify=verify)
                if response.status_code == requests.codes.created:
                    self.host = host
                    self.username = username
                    self.token_vcd = response.headers["x-vchs-authorization"]
                    self.service_type = service_type
                    self.version = version                
                    return True
                else:
                    return False
        elif service_type == 'ondemand':
            if token:                
                headers = {}
                headers["Authorization"] = "Bearer %s" % token
                headers["Accept"] = "application/json;version=%s;class=com.vmware.vchs.sc.restapi.model.planlisttype" % version
                response = requests.get(host + "/api/sc/plans", headers=headers, verify=verify)
                if response.history[-1]:
                    response = requests.get(response.history[-1].headers['location'], headers=headers)                    
                if response.status_code == requests.codes.ok:
                    self.host = host
                    self.token = token
                    self.service_type = service_type
                    self.version = version    
                    self.plans = json.loads(response.content)['plans']
                    return True
                else:
                    return False
            else:
                url = host + "/api/iam/login"
                encode = "Basic " + base64.standard_b64encode(username + ":" + password)
                headers = {}
                headers["Authorization"] = encode.rstrip()
                headers["Accept"] = "application/json;version=%s" % version
                response = requests.post(url, headers=headers, verify=verify)
                if response.status_code == requests.codes.created:
                    self.host = host
                    self.username = username
                    self.token = response.headers["vchs-authorization"]
                    self.service_type = service_type
                    self.version = version              
                    return True
                else:
                    return False
        #todo: test with system administrator role, org_name?
        elif service_type == 'vcd':
            if token_vcd:
                url = host + "/api/session"     
                headers = {}
                headers["x-vcloud-authorization"] = token_vcd
                headers["Accept"] = "application/*+xml;version=" + version
                response = requests.get(url, headers=headers, verify=verify)
                if response.status_code == requests.codes.ok:
                    self.host = host
                    self.token_vcd = token_vcd
                    self.session = sessionType.parseString(response.content, True)
                    self.service_type = service_type
                    self.version = version    
                    self.org_name = username[username.rfind('@')+1:]                    
                    return True
                else:
                    return False
            else:
                url = host + "/api/sessions"                     
                encode = "Basic " + base64.standard_b64encode(username + ":" + password)
                headers = {}
                headers["Authorization"] = encode.rstrip()
                headers["Accept"] = "application/*+xml;version=" + version
                response = requests.post(url, headers=headers, verify=verify)
                if response.status_code == requests.codes.ok:
                    self.host = host
                    self.username = username
                    self.token_vcd = response.headers["x-vcloud-authorization"]
                    self.service_type = service_type
                    self.version = version    
                    self.session = sessionType.parseString(response.content, True)
                    self.org_name = username[username.rfind('@')+1:]
                    return True
                else:
                    return False
        else:
            False
            
    def logout(self, verify=True):
        """
        Request to logout from  vCloud Air.
        
        :return:
        """        
        if self.service_type == 'subscription':
            url = self.host + "/api/vchs/session"
            headers = {}
            headers["x-vchs-authorization"] = self.token
            return requests.delete(url, headers=self._get_vchsHeaders(), verify=verify)
        elif self.service_type == 'ondemand':
            pass
        elif self.service_type == 'vcd':
            pass
        self.token = None
        self.token_vcd = None
            
    def get_orgs(self, verify=True):
        if self.session:
            org_list = filter(lambda org_ref: (org_ref.type_ == 'application/vnd.vmware.vcloud.orgList+xml'), self.session.Link)
            if org_list:
                response = requests.get(org_list[0].href, headers=self._get_vchsHeaders(), verify=verify)
                if response.status_code == requests.codes.ok:
                    orgs = organizationListType.parseString(response.content, True)
                    return orgs

    def get_org(self, name, verify=True):
        orgs = self.get_orgs()
        org_list = orgs.get_Org() if orgs else []
        org = filter(lambda org: org.get_name() == name, org_list)
        if org and org[0]:
            response = requests.get(org[0].href, headers=self._get_vchsHeaders(), verify=verify)
            if response.status_code == requests.codes.ok:
                org_details = organizationType.parseString(response.content, True)
                return org_details

    def _get_vchsHeaders(self):
        headers = {}        
        headers["Accept"] = "application/*+xml;version=" + self.version        
        if self.service_type == 'subscription':
            headers["x-vchs-authorization"] = self.token_vcd
        elif self.service_type == 'ondemand':
            headers["x-vcloud-authorization"] = self.token_vcd
        elif self.service_type == 'vcd':
            headers["x-vcloud-authorization"] = self.token_vcd
        return headers

    def get_instances(self, verify=True):
        if self.service_type == 'ondemand':            
            headers = {}
            headers["Authorization"] = "Bearer %s" % self.token
            headers["Accept"] = "application/json;version=%s" % self.version
            response = requests.get(self.host + "/api/sc/instances", headers=headers, verify=verify)
            if response.history[-1]:
                response = requests.get(response.history[-1].headers['location'], headers=headers, verify=verify)
            if response.status_code == requests.codes.ok:
                return json.loads(response.content)['instances']          

    #this currently works for ondemand only 
    def login_to_instance(self, password, instance, verify=True):
        instances = self.get_instances(verify=verify)
        item = filter(lambda item: item['id'] == instance, instances)
        if item and item[0]:
            # print item[0]
            attrib = json.loads(item[0]['instanceAttributes'])
            encode = "Basic " + base64.standard_b64encode(self.username + "@" + attrib['orgName'] + ":" + password)
            headers = {}
            headers["Authorization"] = encode.rstrip()
            headers["Accept"] = "application/*+xml;version=" + self.version
            response = requests.post(attrib['sessionUri'], headers=headers, verify=verify)
            # print response.content
            if response.status_code == requests.codes.ok:
                # self.host = host
                # self.username = username
                self.token_vcd = response.headers["x-vcloud-authorization"]
                # self.service_type = service_type
                # self.version = version
                self.session = sessionType.parseString(response.content, True)
                #this is also in the session, for convenience
                self.org = attrib['orgName']
                #this is also in the session, for convenience             
                self.api_url = item[0]['apiUrl']
                self.instance = instance
                return True

