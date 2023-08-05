# Copyright (C) 2014 Adam Schubert <adam.schubert@sg1-game.net>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

__author__="Adam Schubert <adam.schubert@sg1-game.net>"
__date__ ="$6.10.2014 5:09:42$"

import logging
import json

import sys



isPython3 = sys.version_info >= (3, 0)

if isPython3:
  import http.client as httplib
  from urllib.parse import urljoin
  from urllib.parse import urlencode
  from urllib.parse import urlparse
else:
  import httplib 
  from urlparse import urljoin
  from urllib import urlencode
  from urlparse import urlparse


import dwa.DwaException as DwaException


class Requester:
  httpConnectionClass = httplib.HTTPConnection
  httpsConnectionClass = httplib.HTTPSConnection

  @classmethod
  def injectConnectionClasses(cls, httpConnectionClass, httpsConnectionClass):
    cls.httpConnectionClass = httpConnectionClass
    cls.httpsConnectionClass = httpsConnectionClass

  @classmethod
  def resetConnectionClasses(cls):
    cls.httpConnectionClass = httplib.HTTPConnection
    cls.httpsConnectionClass = httplib.HTTPSConnection

  def __init__(self, token, baseUrl, timeout, version, userAgent):
    self.token = token
    self.baseUrl = baseUrl
    baseUrlParsed = urlparse(baseUrl)
    self.hostname = baseUrlParsed.hostname
    self.port = baseUrlParsed.port
    self.prefix = baseUrlParsed.path
    
    self.scheme = baseUrlParsed.scheme
    if baseUrlParsed.scheme == "https":
      self.connectionClass = self.httpsConnectionClass
    elif baseUrlParsed.scheme == "http":
      self.connectionClass = self.httpConnectionClass
    else:
      assert False, "Unknown URL scheme"
    self.timeout = timeout
    self.version = version
    self.userAgent = userAgent

  def requestJsonCheck(self, type, url, parameters=None, input=None):
    return self.check(*self.requestJson(type, url, parameters, input))

  def check(self, status, responseHeaders, output):
    output = self.structuredFromJson(output)
    if status >= 400:
      raise self.createException(status, responseHeaders, output)
    return responseHeaders, output

  def createException(self, status, headers, output):
    if status == 500:
      exp = DwaException.ServerErrorException
    elif status == 401:
      exp = DwaException.BadCredentialsException
    elif status == 404:
      exp = DwaException.UnknownObjectException
    else:
      exp = DwaException.BadRequestException
    return exp(status, output)

  def structuredFromJson(self, data):
    if len(data) == 0:
      return None
    else:
      #if we got data in bytes in python2, decode it to unicode
      if isPython3 and isinstance(data, bytes):
        data = data.decode("utf-8")
      try:
        return json.loads(data)
      except ValueError as e:
        return {'data': data}

  def requestJson(self, type, url, parameters=None, input=None):
    def encode(input):
      return "application/json", json.dumps(input)

    return self.requestEncode(type, url, parameters, {}, input, encode)

  def requestEncode(self, type, url, parameters, requestHeaders, input, encode):
    if parameters is None:
      parameters = {}
    if requestHeaders is None:
      requestHeaders = {}

    requestHeaders["User-Agent"] = self.userAgent

    url = self.buildUrl(url, parameters)
    print (url)
    encodedInput = "null"
    if input is not None:
      requestHeaders["Content-Type"], encodedInput = encode(input)

    return self.requestRaw(type, url, requestHeaders, encodedInput)

  def buildUrl(self, url, parameters):
    final = urljoin(self.baseUrl, str(self.version) + url + '/' + self.token)
    if (len(parameters) > 0):
      final += '?' + urlencode(parameters)
    return final 


  def requestRaw(self, type, url, requestHeaders, input):
    connection = self.createConnection()
    connection.request(
      type,
      url,
      input,
      requestHeaders
    )
    response = connection.getresponse()

    status = response.status
    responseHeaders = dict((k.lower(), v) for k, v in response.getheaders())
    output = response.read()

    connection.close()

    self.log(type, url, requestHeaders, input, status, responseHeaders, output)

    return status, responseHeaders, output

  def createConnection(self):
    kwds = {}
    if not isPython3:
      kwds["strict"] = True
    kwds["timeout"] = self.timeout
    return self.connectionClass(self.hostname, self.port, **kwds)

  def log(self, type, url, requestHeaders, input, status, responseHeaders, output):
    logger = logging.getLogger(__name__)
    if logger.isEnabledFor(logging.DEBUG):
      logger.debug("%s %s://%s%s %s %s ==> %i %s %s", str(type), self.scheme, self.hostname, str(url), str(requestHeaders), str(input), status, str(responseHeaders), str(output))