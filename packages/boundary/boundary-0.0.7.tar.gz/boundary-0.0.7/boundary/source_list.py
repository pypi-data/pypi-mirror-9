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
'''
'''
import json
from api_cli import ApiCli
from user_get import UserGet

class SourceList (ApiCli):
     
    def __init__(self):
        ApiCli.__init__(self)
        self.path = "v1/account"
        self.method = "GET"
        self.projectId = None
        
    def addArguments(self):
        ApiCli.addArguments(self)
        
    def getArguments(self):
        ApiCli.getArguments(self)
        user = UserGet()
        user.apihost = self.apihost
        user.apitoken = self.apitoken
        user.email = self.email
        user.validateAndRun()
        if self.result != None:
            userInfo = json.loads(self.result.text)
            print(userInfo)
            self.projectId = userInfo.result.projectId
            
        self.path = "account/{0}/sourcetypes".format(self.projectId)
            
    def validateArguments(self):
        if self.projectId == None:
            self.setErrorMessage("Unable to get account")
            return False

        return ApiCli.validateArguments(self)
        
    def getDescription(self):
        return "Lists the plugins in a Boundary account"
    