DwaPython
=========

[![Build Status](https://travis-ci.org/Salamek/DwaPython.svg?branch=master)](https://travis-ci.org/Salamek/DwaPython)


Python library to communicate with Divine Warfare game API http://api.divine-warfare.com/doc/

# Installation

    pip install DwaPython
    
# Usage

Usage is simple:

```python

#import a library
from dwa import Dwa

#set API token
dwa = Dwa('32len_api_token')

#get user obj
user = dwa.user()

#get list of users
list_of_users = user.list({'limit': 20, 'page': 0})

#get user token info
user_token_info = user.token({'username': 'test', 'password': 'test'})

#get server obj
server = dwa.server()

#get list of servers
list_of_servers = server.list({'limit': 20, 'page':0})

#More info on http://api.divine-warfare.com/doc/

```




