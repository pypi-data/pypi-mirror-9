###
### Copyright 2014-2015 Boundary, Inc.
###
### Licensed under the Apache License, Version 2.0 (the "License");
### you may not use this file except in compliance with the License.
### You may obtain a copy of the License at
###
###     http://www.apache.org/licenses/LICENSE-2.0
###
### Unless required by applicable law or agreed to in writing, software
### distributed under the License is distributed on an "AS IS" BASIS,
### WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
### See the License for the specific language governing permissions and
### limitations under the License.
###
from api_cli import ApiCli

class HostGroupDelete (ApiCli):
     
    def __init__(self):
        ApiCli.__init__(self)
        self.method = "DELETE"
        self.path="v1/hostgroups"
        
        self.hostGroupId = ""
        self.force = False
        
    def addArguments(self):
        ApiCli.addArguments(self)
        self.parser.add_argument('-i', '--host-group-id', dest='hostGroupId',action='store',required=True,help='Host group id to delete')
        self.parser.add_argument('-f', '--force', dest='force',action='store_true',help='Remove the host group, even if in use by a dashboard or alarm')

        
    def getArguments(self):
        '''
        Extracts the specific arguments of this CLI
        '''
        ApiCli.getArguments(self)
        if self.args.hostGroupId != None:
            self.hostGroupId = self.args.hostGroupId
        if self.args.force != None:
            self.force = self.args.force

        if self.force == True:
            self.url_parameters = {"forceRemove": True}
             
        self.path = "v1/hostgroup/{0}".format(str(self.hostGroupId))
         
    def getDescription(self):
        return "Retrieves a single host group definition by id from a Boundary account"
    