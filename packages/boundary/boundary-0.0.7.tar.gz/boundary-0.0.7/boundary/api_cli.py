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
import json


'''
Base class for all the Boundary CLI commands
'''
class ApiCli():

  def __init__(self):
    self.logLevel = None
    self.message = None
    self.path = None
    self.apihost = "premium-api.boundary.com"
    self.email = None
    self.apitoken = None
    self.parser = argparse.ArgumentParser(description=self.getDescription())
    self.scheme = "https"
    self.path = None
    self.url_parameters = None
    self.method = "GET"
    self.headers = None
    self.data = None
    
    # Construct a dictionary with each of the HTTP methods that we support
    self.methods = {"DELETE": self.doDelete,"GET": self.doGet,"POST": self.doPost,"PUT": self.doPut}
    self.levels = {"debug": logging.DEBUG,
                   "info": logging.INFO,
                   "warn": logging.WARN,
                   "error": logging.ERROR,
                   "critical": logging.CRITICAL}

  def getDescription(self):
    '''
    Returns a description of the CLI
    '''
    return "General API CLI"

  def getEnvironment(self):
    '''
    Gets the configuration stored in environment variables
    '''
    try:
      self.email = os.environ['BOUNDARY_EMAIL']
    except(KeyError):
      self.email = None
    try:
      self.apitoken = os.environ['BOUNDARY_API_TOKEN']
    except(KeyError):
      self.apitoken = None
    try:
      self.apihost = os.environ['BOUNDARY_API_HOST']
    except(KeyError):
      self.apihost = 'premium-api.boundary.com'

  def addArguments(self):
    '''
    Configure handling of command line arguments.
    '''
    self.parser.add_argument('-l', '--log-level',dest='logLevel', action='store',choices=['debug','info','warning','error','critical'],
                             help='Sets logging level to one of debug,info,warning,error,critical. Default is logging is disabled')
    self.parser.add_argument('-a', '--api-host',dest='apihost',action='store',metavar="api_host",help='Boundary API host endpoint')
    self.parser.add_argument('-e', '--email',dest='email',action='store',metavar="e_mail",
                             help='e-mail that has access to the Boundary account')
    self.parser.add_argument('-t', '--api-token',dest='apitoken',required=False,action='store',metavar="api_token",
                             help='API token for given e-mail that has access to the Boundary account')
    
  def parseArgs(self):
    '''
    Handles the parse of the command line arguments
    '''
    self.addArguments()
    self.args = self.parser.parse_args()
    
  def configureLogging(self):
    '''
    Configure logging based on command line options
    '''
    if self.args.logLevel != None:
        logging.basicConfig(level=self.levels[self.args.logLevel])
        logging.info("Set logging level to {0}".format(self.args.logLevel))

  def getArguments(self):
    '''
    CLIs get called back so that they can process any command line arguments
    that are given. This method handles the standard command line arguments for:
    API Host, user, password, etc.
    '''
    self.configureLogging()
    
    if self.args.apihost != None:
        self.apihost = self.args.apihost
    if self.args.email != None:
        self.email = self.args.email
    if self.args.apitoken != None:
        self.apitoken = self.args.apitoken
        
    logging.debug("apihost: {0}".format(self.apihost))
    logging.debug("email: {0}".format(self.email))
    logging.debug("apitoken: {0}".format(self.apitoken))
      
  def setErrorMessage(self,message):
        self.message = message
      
  def validateArguments(self):
    if self.email == None:
        self.setErrorMessage("E-mail for the account not provided")
        return False
    if self.apitoken == None:
        self.setErrorMessage("API Token for the account not provided")
        return False
    return True

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
    
  def getPayload(self):
    if self.data == None:
        payload = None
    else:
        payload = json.dumps(self.data)
        logging.debug(payload)

    return payload

  def doGet(self):
    '''
    HTTP Get Request
    '''
    return requests.get(self.url,data=self.getPayload(),headers=self.headers,auth=(self.email,self.apitoken))

  def doDelete(self):
    '''
    HTTP Delete Request
    '''
    return requests.delete(self.url,data=self.getPayload(),headers=self.headers,auth=(self.email,self.apitoken))

  def doPost(self):

    return requests.post(self.url,data=self.getPayload(),headers=self.headers,auth=(self.email,self.apitoken))

  def doPut(self):
    '''
    HTTP Put Request
    '''
    return requests.put(self.url,data=self.getPayload(),headers=self.headers,auth=(self.email,self.apitoken))

  def callAPI(self):
    '''
    Make an API call to get the metric definition
    '''

    self.url = "{0}://{1}/{2}{3}".format(self.scheme,self.apihost,self.path,self.getUrlParameters())

    result = self.methods[self.method]()
    if result.status_code != urllib2.httplib.OK:
        logging.error(self.url)
        logging.error(self.method)
        if self.getPayload() != None:
            logging.error(self.getPayload())
        logging.error(result)
    self.handleResults(result)
      
  def handleResults(self,result):
    '''
    Call back function to be implemented by the CLI.
    Default is to just print the results to standard out
    '''
    print(result.text)
  
  def execute(self):
    '''
    Run the steps to execute the CLI
    '''
    self.getEnvironment()
    self.parseArgs()
    self.getArguments()
    if self.validateArguments() == True:
        self.callAPI()
    else:
        print(self.message)

