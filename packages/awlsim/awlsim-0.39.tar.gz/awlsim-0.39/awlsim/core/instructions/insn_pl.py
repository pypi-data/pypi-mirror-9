# -*- coding: utf-8 -*-
#
# AWL simulator - instructions
#
# Copyright 2012-2014 Michael Buesch <m@bues.ch>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

from __future__ import division, absolute_import, print_function, unicode_literals
from awlsim.common.compat import *

from awlsim.core.instructions.main import * #@nocy
from awlsim.core.operators import *
#from awlsim.core.instructions.main cimport * #@cy


class AwlInsn_PL(AwlInsn): #+cdef
	def __init__(self, cpu, rawInsn):
		AwlInsn.__init__(self, cpu, AwlInsn.TYPE_PL, rawInsn)
		self.assertOpCount(1)
		if self.ops[0].type != AwlOperator.IMM:
			raise AwlSimError("Immediate expected")

	def run(self):
#@cy		cdef S7StatusWord s

		oper = self.ops[0]
		if oper.width == 16:
			self.cpu.accu1.setWord(self.cpu.accu1.getSignedWord() +\
					       self.cpu.fetch(oper))
		elif oper.width == 32:
			self.cpu.accu1.setDWord(self.cpu.accu1.getSignedDWord() +\
						self.cpu.fetch(oper))
		else:
			raise AwlSimError("Unexpected operator width")
