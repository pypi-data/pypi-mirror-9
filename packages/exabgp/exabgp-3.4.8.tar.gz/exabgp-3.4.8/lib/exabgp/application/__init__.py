# encoding: utf-8
"""
__init__.py

Created by Thomas Mangin on 2014-12-31.
Copyright (c) 2014-2015 Exa Networks. All rights reserved.
"""


def run_exabgp ():
	from exabgp.application.bgp import main
	main()


def run_exabmp ():
	from exabgp.application.bmp import main
	main()
