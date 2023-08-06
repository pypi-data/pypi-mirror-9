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
import json
import logging
import os
import requests

'''
Base class for all the Boundary CLI commands
'''
class ApiCli():

  def __init__(self):
    self.path = None
    self.apihost = None
    self.email = None
    self.apitoken = None
    self.parser = argparse.ArgumentParser(description=self.getDescription())
    self.scheme = "https"
    self.path = None
    self.url_parameters = None
    self.method = "GET"
    self.data = None
    
    self.methods = {"DELETE": self.doDelete,"GET": self.doGet,"POST": self.doPost,"PUT": self.doPut}

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
    self.parser.add_argument('-a', '--api-host', dest='apihost',action='store',help='API endpoint')
    self.parser.add_argument('-e', '--email', dest='email', action='store', help='e-mail used to create the Boundary account')
    self.parser.add_argument('-t', '--api-token', dest='apitoken', required=False, action='store', help='API token to access the Boundary Account')
    self.parser.add_argument('-v', '--verbose',dest='verbose', action='store_true', help='verbose mode')
    
  def parseArgs(self):
    '''
    Handles the parse of the command line arguments
    '''
    self.addArguments()
    self.args = self.parser.parse_args()
    
  def getArgs(self):
    if self.args.apihost != None:
        self.apihost = self.args.apihost
    if self.args.email != None:
      self.email = self.args.email
    if self.args.apitoken != None:
      self.apitoken = self.args.apitoken
    if self.args.apitoken != None:
      self.apitoken = self.args.apitoken

  def doGet(self):
    return requests.get(self.url,auth=(self.email,self.apitoken))

  def doDelete(self):
    return requests.delete(self.url,auth=(self.email,self.apitoken))

  def doPost(self):
    return requests.post(self.url,auth=(self.email,self.apitoken),data=self.payload)

  def doPut(self):
    return requests.put(self.url,auth=(self.email,self.apitoken),data=self.payload)

  def callAPI(self):
    '''
    Make an API call to get the metric definition
    '''
    self.url = "{0}://{1}/{2}/".format(self.scheme,self.apihost,self.path)
    result = self.methods[self.method]()
    if result.status_code != 200:
        print(self.url)
        print(result)
    self.handleResults(result)
      
  def handleResults(self,result):
    print(result.text)
  
  def execute(self):
    self.getEnvironment()
    self.parseArgs()
    self.getArgs()
    self.callAPI()

