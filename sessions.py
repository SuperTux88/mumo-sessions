#!/usr/bin/env python
# -*- coding: utf-8

# Copyright (C) 2011 Stefan Hacker <dd0t@users.sourceforge.net>
# Copyright (C) 2013 Natenom <natenom@googlemail.com>
# Copyright (C) 2014 Benjamin Neff <benjamin@coding4coffee.ch>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:

# - Redistributions of source code must retain the above copyright notice,
#   this list of conditions and the following disclaimer.
# - Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
# - Neither the name of the Mumble Developers nor the names of its
#   contributors may be used to endorse or promote products derived from this
#   software without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# `AS IS'' AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE FOUNDATION OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# sessions.py - see README

from mumo_module import (commaSeperatedIntegers,
			 commaSeperatedBool,
			 MumoModule)
import re

class sessions(MumoModule):
	default_config = {'sessions':(
				('servers', commaSeperatedIntegers, []),
				),
				lambda x: re.match('(all)|(server_\d+)', x):(
				('canlistsessions', str, 'admin'),
				('cmd_listsessions', str, '!sessions')
				)
		}

	def __init__(self, name, manager, configuration = None):
		MumoModule.__init__(self, name, manager, configuration)
		self.murmur = manager.getMurmurModule()

	def connected(self):
		manager = self.manager()
		log = self.log()
		log.debug("Register for Server callbacks")

		servers = self.cfg().sessions.servers
		if not servers:
			servers = manager.SERVERS_ALL

		manager.subscribeServerCallbacks(self, servers)

	def disconnected(self): pass

	#
	#--- Server callback functions
	#

	def userTextMessage(self, server, user, message, current=None):
		try:
			scfg = getattr(self.cfg(), 'server_%d' % server.id())
		except AttributeError:
			scfg = self.cfg().all

		operator = user

		log = self.log()
		words = re.split(ur"[\u200b\s]+", message.text)
		command = words[0]

		ACL=server.getACL(0)
		for group in ACL[1]:
			if (group.name == scfg.canlistsessions):
				if (operator.userid in group.members):
					if (command == scfg.cmd_listsessions): #Show operator a list of all sessions connected to the server.
						listusers="<br />Online users: "
						listusers+="<table border='1'><tr><td>SessionID</td><td>Name</td></tr>"
						for iteruser in server.getUsers().itervalues():
							listusers+="<tr><td align='right'>%s</td><td>%s</td></tr>" % (iteruser.session, iteruser.name)

						listusers+="</table>"

						server.sendMessage(operator.session, listusers)
						return

	def userConnected(self, server, state, context = None): pass
	def userDisconnected(self, server, state, context = None): pass
	def userStateChanged(self, server, state, context = None): pass
	def channelCreated(self, server, state, context = None): pass
	def channelRemoved(self, server, state, context = None): pass
	def channelStateChanged(self, server, state, context = None): pass
