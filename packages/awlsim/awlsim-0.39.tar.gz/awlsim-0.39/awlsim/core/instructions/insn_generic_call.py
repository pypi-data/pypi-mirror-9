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


class AwlInsn_GENERIC_CALL(AwlInsn): #+cdef
	"""Generic callback pseudo-instruction.
	This instruction calls the supplied callback."""

	def __init__(self, cpu, callback):
		AwlInsn.__init__(self, cpu, AwlInsn.TYPE_GENERIC_CALL, None)
		self.callback = callback

	def run(self):
#@cy		cdef S7StatusWord s

		try:
			self.callback()
		except AwlSimError as e:
			# An exception occurred. We try to blame that on the
			# instruction calling us, so the user gets a
			# sane error message.
			if len(self.cpu.callStack) >= 2:
				cse = self.cpu.callStack[-2] # Previous stack frame
				ip = cse.ip - 1
				if ip >= 0 and ip < len(cse.insns):
					# Assign the calling instruction to the exception.
					insn = cse.insns[ip]
					e.setInsn(insn)
					e.setRawInsn(None)
					raise e
			raise # Out of luck
