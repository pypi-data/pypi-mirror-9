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
__date__ ="$6.10.2014 5:12:30$"

class DwaException(Exception):
  def __init__(self, status, output):
    Exception.__init__(self)
    self.status = status
    self.output = output

  def __str__(self):
    return str(self.status) + " " + str(self.output)
    
class BadCredentialsException(DwaException):
  """
  Exception raised in case of bad credentials (when Dwa replies with a 401 or 403 http status)
  """
    
class UnknownObjectException(DwaException):
  """
  Exception raised in case when requested object is not found (when Dwa replies with a 404 http status)
  """

class ServerErrorException(DwaException):
  """
  Exception raised in case when server fails to procces request (when Dwa replies with a 500 http status)
  """
  
class BadRequestException(DwaException):
  """
  Exception raised in case when server fails to understand request (when Dwa replies with a 400 http status)
  """