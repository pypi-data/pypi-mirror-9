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
__date__ ="$12.10.2014 3:35:14$"

import tests.DwaTestCase as DwaTestCase

class ApiTest(DwaTestCase.DwaTestCase):
  def setUp(self):
    DwaTestCase.DwaTestCase.setUp(self)
    self.api = self.d.api()
    self.user_data = self.d.user().token(self.credential)

  def testCreate(self):
    data = self.api.create({'user_token': self.user_data['token'], 'user_id': self.user_data['id'], 'description': 'UNIT TESTING API Token'})
    self.assertEqual(data['message'], 'Token created')
    self.assertEqual(len(data['token']), 32)
    
  def testList(self):
    data = self.api.list({'limit': 1, 'page': 0, 'user_token': self.user_data['token'], 'user_id': self.user_data['id']})
    self.assertEqual(data['message'], 'OK')
    self.assertEqual(len(data['data']), 1)
    self.assertIsNotNone(data['pages'])
    
  def testDelete(self):
    data_token = self.api.create({'user_token': self.user_data['token'], 'user_id': self.user_data['id'], 'description': 'UNIT TESTING API Token'})
    data = self.api.delete({'user_token': self.user_data['token'], 'user_id': self.user_data['id'], 'token_id': data_token['id']})
    self.assertEqual(data['message'], 'Token deleted')

    