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
__date__ ="$12.10.2014 2:20:45$"

import tests.DwaTestCase as DwaTestCase
import unittest

class UserTest(DwaTestCase.DwaTestCase):
  def setUp(self):
    DwaTestCase.DwaTestCase.setUp(self)
    self.user = self.d.user()
  
  @unittest.skip("This test is skipped till ACL is implemented")
  def testCreate(self):
    params = {}
    params['password'] = self.credential['password']
    params['username'] = self.credential['username']
    params['email'] = self.credential['username'] + '@divine-warfare.com'
    params['active'] = True
    message = self.user.create(params)['message']
    self.assertEqual(message, 'User created')
    
  def testList(self):
    data = self.user.list({'limit': 20, 'page': 0})
    self.assertEqual(data['message'], 'OK')
    self.assertEqual(len(data['data']), 20)
    self.assertIsNotNone(data['pages'])
    
  def testToken(self):
    data = self.user.token(self.credential)
    self.assertEqual(data['message'], 'Token created')
    self.assertEqual(len(data['token']), 32)
    self.assertIsNotNone(data['id'])
    self.assertRegexpMatches(data['token_expiration'], '(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2})')
    
  def testPassword(self):
    data_token = self.user.token(self.credential)
    data = self.user.password({'old_password': self.credential['password'], 'new_password': self.credential['password'], 'user_token': data_token['token'], 'user_id': data_token['id']})
    self.assertEqual(data['message'], 'Password changed')
    
  def testActive(self):
    data_token = self.user.token(self.credential)
    data = self.user.active({'user_id': data_token['id'], 'active': True})
    self.assertEqual(data['message'], 'User activated/deactivated')
