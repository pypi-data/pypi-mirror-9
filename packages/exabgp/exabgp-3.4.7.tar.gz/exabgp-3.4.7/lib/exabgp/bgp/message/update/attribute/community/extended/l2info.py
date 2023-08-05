# encoding: utf-8
"""
encapsulation.py

Created by Thomas Mangin on 2014-06-20.
Copyright (c) 2014-2015 Orange. All rights reserved.
Copyright (c) 2014-2015 Exa Networks. All rights reserved.
"""

from struct import pack
from struct import unpack

from exabgp.bgp.message.update.attribute.community.extended import ExtendedCommunity

# ============================================================ Layer2Information
# RFC 4761

class L2Info (ExtendedCommunity):
	COMMUNITY_TYPE = 0x80
	COMMUNITY_SUBTYPE = 0x0A

	__slots__ = ['encaps','control','mtu','reserved']

	def __init__ (self,encaps,control,mtu,reserved,community=None):
		self.encaps = encaps
		self.control = control
		self.mtu = mtu
		self.reserved = reserved
		ExtendedCommunity.__init__(self,community if community is not None else pack("!BBLH",0x80,0x0A,0,self.tunnel_type))

	def __str__ (self):
		return "l2info:%s:%s:%s:%s" % (self.encaps,self.control,self.mtu,self.reserved)

	@staticmethod
	def unpack (data):
		encaps,control,mtu,reserved = unpack('!BBHH',data[2:8])
		return L2Info(encaps,control,mtu,reserved,data[:8])

L2Info.register_extended()
