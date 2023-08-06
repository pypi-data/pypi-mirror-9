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
from plugin_base import PluginBase

class PluginUninstall (PluginBase):
     
    def __init__(self):
        PluginBase.__init__(self)
        self.method = "DELETE"
        self.path = "v1/plugins/installed"
        self.removeMetrics = False
        self.removeDashes = False
        
    def addArguments(self):
        PluginBase.addArguments(self)
        self.parser.add_argument('-d', '--remove-Dashes', dest='removeDashes',action='store_true',help='Remove dashboards associated with the plugin')
        self.parser.add_argument('-r', '--remove-Metrics', dest='removeMetrics',action='store_true',help='Remove metrics associated with the plugin')

    def getArguments(self):
        PluginBase.getArguments(self)
        self.path = "v1/plugins/installed/{0}".format(self.pluginName)
        self.url_parameters = {"removeMetrics": self.removeMetrics,"removeDashes": self.removeDashes}
         
    def getDescription(self):
        return "Uninstalls a plugin from a Boundary account"
    