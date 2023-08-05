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
__date__ ="$12.10.2014 4:08:10$"

import tests.DwaTestCase as DwaTestCase

class CharacterTest(DwaTestCase.DwaTestCase):
  def setUp(self):
    DwaTestCase.DwaTestCase.setUp(self)
    self.character = self.d.character()
    self.user_data = self.d.user().user.token(self.credential)

  def testList(self):
    data = self.clan.list({'server_id':1, 'limit': 20, 'page': 0})
    self.assertEqual(data['message'], 'OK')
    self.assertEqual(len(data['data']), 20)
    self.assertIsNotNone(data['pages'])
    
  def testDetail(self):
    data = self.clan.detail({'server_id': 1, 'user_id': user_data['id'], 'user_token': user_data['token']})
    self.assertEqual(data['message'], 'OK')
    self.assertEqual(len(data['data']), 5)

    