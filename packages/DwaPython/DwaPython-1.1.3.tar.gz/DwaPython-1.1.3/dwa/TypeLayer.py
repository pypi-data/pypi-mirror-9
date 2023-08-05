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



from dwa.Requester import Requester

DEFAULT_BASE_URL = "http://api.divine-warfare.com"
DEFAULT_VERSION = 1.0
DEFAULT_TIMEOUT = 10

class TypeLayer:

  def __init__(self, apiToken=None, baseUrl=DEFAULT_BASE_URL, timeout=DEFAULT_TIMEOUT, version=DEFAULT_VERSION, userAgent='DwaPython'):
    self.requester = Requester(apiToken, baseUrl, timeout, version, userAgent)
   
  def request(self, class_name, type_name, params = None):
    if type_name in ['create']:
      type = 'POST'
      input = params
      parameters = None
    elif type_name in ['delete']:
      type = 'DELETE'
      input = None
      parameters = params
    elif type_name in ['password', 'active']:
      type = 'PUT'
      input = params
      parameters = None
    else:
      type = 'GET'
      input = None
      parameters = params
    
    url = '/{class_name}/{type_name}'.format(class_name=class_name, type_name=type_name)
    return self.requester.requestJsonCheck(type, url, parameters, input)[1]
