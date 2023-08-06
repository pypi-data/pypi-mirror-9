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

import urllib, getopt

class Gateway():
	'''
	A Python wrapper around the SMS gateway from CPSMS <https://www.cpsms.dk/>.

	Please look at the README for further description.
	'''
	default_options = {
		'recipients' : [],
		'message' : '',        # Should be a unicode string.
		'callback_url' : '',
		'timestamp' : '',      # For delaying messages. Format: YYYYMMDDHHMM.
		'utf8' : 1,
		'flash' : 0,
		'group' : 0,
		'gateway_base_url' : 'https://www.cpsms.dk/sms/?'
	}
	options = {}
	
	def __init__(self, username, password, sender_name, options = None):
		'''
		Initialize SMS gateway, with some options.
		'''
		self.options = self.default_options
		if options != None:
			self.options.update(options)

		self.options['username'] = username
		self.options['password'] = password
		self.options['from'] = sender_name
	
	def add_recipient(self, number):
		'''
		Add a number to the list of recipients.
		'''
		self.options['recipients'].append(number)
	
	def send(self, message = None):
		'''
			Send the message specified in self.options to all recipients. Optionally, override the message to be sent.
		'''
		# Decide what to send
		if message == None:
			message = self.options['message']
		
		# Raise error if message is empty.
		if len(message) == 0:
			raise ValueError('Message empty.')
		
		# Raise error if message is too long.
		if len(message) > 459:
			raise ValueError('Message not allowed to be more than 459 characters. Current message is %i characters.' % len(message))
		
		# Raise error if recipients is empty.
		if len(self.options['recipients']) == 0:
			raise ValueError('No recipients.')
		
		# Construct gateway URL.
		options = [
			('username', self.options['username']),
			('password', self.options['password']),
			('message', message.encode('utf-8')),
			('from', self.options['from']),
			('utf8', self.options['utf8']),
			('flash', self.options['flash']),
			('group', self.options['group']),
			('url', self.options['callback_url']),
		]
		
		for r in self.options['recipients']:
			options.append(('recipient[]', r))
		
		if self.options['timestamp'] != '':
			options.append(('timestamp', self.options['timestamp']))
		
		url = self.options['gateway_base_url'] + urllib.urlencode(options)
		
		# Send SMS.
		remote_call = urllib.urlopen(url)
		result = remote_call.read()
		remote_call.close()
		if result.find('<succes>') > -1:
			return True, result
		else:
			return False, result
