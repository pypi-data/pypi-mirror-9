#!/usr/bin/python
# -*- coding: utf-8 -*-'

"""
Copyright 2010, 2011 Mikkel Munch Mortensen <3xm@detfalskested.dk>.

This file is part of SMS Gateway.

SMS Gateway is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

SMS Gateway is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with SMS Gateway.  If not, see <http://www.gnu.org/licenses/>.
"""

import cpsms

# The easiest way to send a single message.
gateway1 = cpsms.Gateway('username', 'password', 'SMS Test')
gateway1.add_recipient('+4512345678')
print gateway1.send(u'One way of sending a massage.')

# The easiest way to send a message to multiple recipients.
gateway2 = cpsms.Gateway('username', 'password', 'SMS Test', {
	'recipients' : ['+4512345678', '+4587654321'],
	'message' : u'Another way of sending a message.',
})
print gateway2.send()
