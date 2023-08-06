#!/usr/bin/env python
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

import argparse
import logging
import os
import requests
import urllib2


'''
Base class for all the Boundary CLI commands
'''
class ApiCall():

  def __init__(self):
    self.message = None
    self.path = None
    self.apihost = "premium-api.boundary.com"
    self.email = None
    self.apitoken = None
    self.scheme = "https"
    self.path = None
    self.url_parameters = None
    self.method = "GET"
    self.data = None
    self.result = None
    
    # Construct a dictionary with each of the HTTP methods that we support
    self.methods = {"DELETE": self.doDelete,"GET": self.doGet,"POST": self.doPost,"PUT": self.doPut}
      
  def setErrorMessage(self,message):
        self.message = message
      
  def getUrlParameters(self):
    urlParameters = ""
    if self.url_parameters != None:
        urlParameters = "?"
        values = self.url_parameters
        first = True
        for key in values:
            if first == True:
                first = False
            else:
                urlParameters = urlParameters + "&"
            urlParameters = urlParameters + "{0}={1}".format(key,values[key])
    return urlParameters

  def doGet(self):
    '''
    HTTP Get Request
    '''
    return requests.get(self.url,auth=(self.email,self.apitoken),data=self.data)

  def doDelete(self):
    '''
    HTTP Delete Request
    '''
    return requests.delete(self.url,auth=(self.email,self.apitoken),data=self.data)

  def doPost(self):
    return requests.post(self.url,auth=(self.email,self.apitoken),data=self.data)

  def doPut(self):
    '''
    HTTP Put Request
    '''
    return requests.put(self.url,auth=(self.email,self.apitoken),data=self.data)

  def callAPI(self):
    '''
    Make an API call to get the metric definition
    '''

    self.url = "{0}://{1}/{2}{3}".format(self.scheme,self.apihost,self.path,self.getUrlParameters())
    logging.debug(self.url)

    self.result = self.methods[self.method]()
    if self.result.status_code != urllib2.httplib.OK:
        logging.error(self.url)
        if self.data != None:
            logging.error(self.data)
        logging.error(self.result)
      
  def handleResults(self,result):
    '''
    Call back function to be implemented by the CLI.
    Default is to just print the results to standard out
    '''
    print(result.text)
    
    
    

