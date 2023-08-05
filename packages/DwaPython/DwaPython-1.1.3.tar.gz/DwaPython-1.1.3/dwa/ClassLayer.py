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
__date__ ="$8.10.2014 1:44:13$"

from dwa.TypeLayer import TypeLayer

class ClassLayer:
  
  type = None
  def __init__(self, api_key, class_name):
    self.typeLayer = TypeLayer(api_key)
    self.class_name = class_name

  def __getattr__(self, type_name):
    def function(params):
      return (self.typeLayer.request(self.class_name, type_name, params))
    return function
