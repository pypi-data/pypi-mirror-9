# -*- coding: utf-8 -*-
#
# AWL data types
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

from awlsim.common.datatypehelpers import *
from awlsim.common.wordpacker import *

from awlsim.core.util import *
from awlsim.core.timers import *
from awlsim.core.offset import *

import datetime


class AwlDataType(object):
	# Data type IDs
	EnumGen.start
	TYPE_VOID	= EnumGen.item
	TYPE_BOOL	= EnumGen.item
	TYPE_BYTE	= EnumGen.item
	TYPE_WORD	= EnumGen.item
	TYPE_DWORD	= EnumGen.item
	TYPE_INT	= EnumGen.item
	TYPE_DINT	= EnumGen.item
	TYPE_REAL	= EnumGen.item
	TYPE_S5T	= EnumGen.item
	TYPE_TIME	= EnumGen.item
	TYPE_DATE	= EnumGen.item
	TYPE_DT		= EnumGen.item
	TYPE_TOD	= EnumGen.item
	TYPE_CHAR	= EnumGen.item
	TYPE_ARRAY	= EnumGen.item
	TYPE_TIMER	= EnumGen.item
	TYPE_COUNTER	= EnumGen.item
	TYPE_BLOCK_DB	= EnumGen.item # DB number type
	TYPE_BLOCK_FB	= EnumGen.item # FB number type
	TYPE_BLOCK_FC	= EnumGen.item # FC number type
	TYPE_DB_X	= EnumGen.item # DBx type
	TYPE_OB_X	= EnumGen.item # OBx type
	TYPE_FC_X	= EnumGen.item # FCx type
	TYPE_SFC_X	= EnumGen.item # SFCx type
	TYPE_FB_X	= EnumGen.item # FBx type
	TYPE_SFB_X	= EnumGen.item # SFBx type
	TYPE_UDT_X	= EnumGen.item # UDTx type
	TYPE_VAT_X	= EnumGen.item # VATx type
	EnumGen.end

	__name2id = {
		"VOID"		: TYPE_VOID,
		"BOOL"		: TYPE_BOOL,
		"BYTE"		: TYPE_BYTE,
		"WORD"		: TYPE_WORD,
		"DWORD"		: TYPE_DWORD,
		"INT"		: TYPE_INT,
		"DINT"		: TYPE_DINT,
		"REAL"		: TYPE_REAL,
		"S5TIME"	: TYPE_S5T,
		"TIME"		: TYPE_TIME,
		"DATE"		: TYPE_DATE,
		"DATE_AND_TIME"	: TYPE_DT,
		"TIME_OF_DAY"	: TYPE_TOD,
		"CHAR"		: TYPE_CHAR,
		"ARRAY"		: TYPE_ARRAY,
		"TIMER"		: TYPE_TIMER,
		"COUNTER"	: TYPE_COUNTER,
		"BLOCK_DB"	: TYPE_BLOCK_DB,
		"BLOCK_FB"	: TYPE_BLOCK_FB,
		"BLOCK_FC"	: TYPE_BLOCK_FC,
		"DB"		: TYPE_DB_X,
		"OB"		: TYPE_OB_X,
		"FC"		: TYPE_FC_X,
		"SFC"		: TYPE_SFC_X,
		"FB"		: TYPE_FB_X,
		"SFB"		: TYPE_SFB_X,
		"UDT"		: TYPE_UDT_X,
		"VAT"		: TYPE_VAT_X,
	}
	__id2name = pivotDict(__name2id)

	# Width table for types
	# -1 => Type width must be calculated
	type2width = {
		TYPE_VOID	: 0,
		TYPE_BOOL	: 1,
		TYPE_BYTE	: 8,
		TYPE_WORD	: 16,
		TYPE_DWORD	: 32,
		TYPE_INT	: 16,
		TYPE_DINT	: 32,
		TYPE_REAL	: 32,
		TYPE_S5T	: 16,
		TYPE_TIME	: 32,
		TYPE_DATE	: 16,
		TYPE_DT		: 64,
		TYPE_TOD	: 32,
		TYPE_CHAR	: 8,
		TYPE_ARRAY	: -1,
		TYPE_TIMER	: 16,
		TYPE_COUNTER	: 16,
		TYPE_BLOCK_DB	: 16,
		TYPE_BLOCK_FB	: 16,
		TYPE_BLOCK_FC	: 16,
		TYPE_DB_X	: -1,
		TYPE_OB_X	: 0,
		TYPE_FC_X	: 0,
		TYPE_SFC_X	: 0,
		TYPE_FB_X	: -1,
		TYPE_SFB_X	: -1,
		TYPE_UDT_X	: -1,
		TYPE_VAT_X	: 0,
	}

	# Table of trivial types with sign
	signedTypes = (
		TYPE_INT,
		TYPE_DINT,
		TYPE_REAL,
	)

	# Table of compound types
	compoundTypes = (
		TYPE_DT,
		TYPE_ARRAY,
		TYPE_UDT_X,
	)

	# Convert a list of array dimensions into a number of elements.
	@classmethod
	def arrayDimensionsToNrElements(cls, dimensions):
		assert(dimensions is not None)
		assert(len(dimensions) >= 1 and len(dimensions) <= 6)
		nrElems = reduce(lambda a, b: a * (b[1] - b[0] + 1),
				 dimensions, 1)
		return nrElems

	@classmethod
	def _name2typeid(cls, nameTokens):
		nameTokens = toList(nameTokens)
		try:
			return cls.__name2id[nameTokens[0].upper()]
		except (KeyError, IndexError) as e:
			raise AwlSimError("Invalid data type name: " +\
					  nameTokens[0] if len(nameTokens) else "None")

	@classmethod
	def makeByName(cls, nameTokens, arrayDimensions=None):
		type = cls._name2typeid(nameTokens)
		index = None
		if type == cls.TYPE_ARRAY:
			raise AwlSimError("Nested ARRAYs are not allowed")
		elif type in (cls.TYPE_DB_X,
			      cls.TYPE_OB_X,
			      cls.TYPE_FC_X,
			      cls.TYPE_SFC_X,
			      cls.TYPE_FB_X,
			      cls.TYPE_SFB_X,
			      cls.TYPE_UDT_X):
			if len(nameTokens) < 2:
				raise AwlSimError("Invalid '%s' block data type" %\
					nameTokens[0])
			blockNumber = cls.tryParseImmediate_INT(nameTokens[1])
			if blockNumber is None:
				raise AwlSimError("Invalid '%s' block data type "\
					"index" % nameTokens[0])
			index = blockNumber
		if arrayDimensions:
			# An ARRAY is to be constructed.
			nrArrayElements = cls.arrayDimensionsToNrElements(arrayDimensions)
			elementType = cls(type = type,
					  width = cls.type2width[type],
					  isSigned = (type in cls.signedTypes),
					  index = index)
			# Make a tuple of children types.
			# Each element is a ref to the same AwlDataType instance.
			children = tuple([ elementType, ] * nrArrayElements)
			return cls(type = cls.TYPE_ARRAY,
				   width = nrArrayElements * elementType.width,
				   isSigned = (type in cls.signedTypes),
				   index = index,
				   children = children,
				   arrayDimensions = arrayDimensions)
		else:
			return cls(type = type,
				   width = cls.type2width[type],
				   isSigned = (type in cls.signedTypes),
				   index = index)

	def __init__(self, type, width, isSigned,
		     index=None, children=None,
		     arrayDimensions=None):
		self.type = type		# The TYPE_... for this datatype
		self.width = width		# The width, in bits.
		self.isSigned = isSigned	# True, if this type is signed
		self.index = index		# The Index number, if any. May be None
		self.children = children	# The children AwlDataTypes, if ARRAY.
		self.arrayDimensions = arrayDimensions # The ARRAY's dimensions

	# Returns True, if this is a compound data type.
	@property
	def compound(self):
		return self.type in self.compoundTypes

	# Convert array indices into a one dimensional index for this array.
	# 'indices' is a list of index integers as written in the AWL operator
	# from left to right.
	def arrayIndicesCollapse(self, indices):
		if not indices:
			return None
		if len(indices) < 1 or len(indices) > 6:
			raise AwlSimError("Invalid number of array indices")
		assert(self.type == self.TYPE_ARRAY)
		signif = self.arrayIndexSignificances()
		assert(len(indices) == len(signif))
		assert(len(indices) == len(self.arrayDimensions))
		resIndex = 0
		for i, idx in enumerate(indices):
			startIdx, endIdx = self.arrayDimensions[i]
			if idx < startIdx or idx > endIdx:
				raise AwlSimError("Array index '%d' is out of bounds "
					"for array range '%d .. %d'." %\
					(idx, startIdx, endIdx))
			resIndex += (idx - startIdx) * signif[i]
		return resIndex

	# Get the array dimension sizes. Returns a tuple of integers.
	def arrayDimSizes(self):
		assert(self.type == self.TYPE_ARRAY)
		return tuple(end - start + 1
			     for start, end in self.arrayDimensions)

	# Get the array index significances. Returns a tuple of integers.
	def arrayIndexSignificances(self):
		assert(self.type == self.TYPE_ARRAY)
		sizes = self.arrayDimSizes()
		signif = [ 1, ]
		for size in sizes[:0:-1]:
			signif.append(size * signif[-1])
		return tuple(signif[::-1])

	# Get the number of array elements
	def arrayGetNrElements(self):
		assert(self.type == self.TYPE_ARRAY)
		return len(self.children)

	# Parse an immediate, constrained by our datatype.
	def parseMatchingImmediate(self, tokens):
		typeId = self.type
		if typeId == self.TYPE_ARRAY:
			typeId = self.children[0].type

		value = None
		if tokens is None:
			value = 0
		elif len(tokens) == 9:
			if typeId == self.TYPE_DWORD:
				value, fields = self.tryParseImmediate_ByteArray(
							tokens)
		elif len(tokens) == 5:
			if typeId == self.TYPE_WORD:
				value, fields = self.tryParseImmediate_ByteArray(
							tokens)
			elif typeId == self.TYPE_DT:
				value = self.tryParseImmediate_DT(tokens)
			elif typeId == self.TYPE_TOD:
				value = self.tryParseImmediate_TOD(tokens)
		elif len(tokens) == 2:
			if typeId == self.TYPE_TIMER:
				if tokens[0].upper() == "T":
					value = self.tryParseImmediate_INT(tokens[1])
			elif typeId == self.TYPE_COUNTER:
				if tokens[0].upper() in ("C", "Z"):
					value = self.tryParseImmediate_INT(tokens[1])
			elif typeId == self.TYPE_BLOCK_DB:
				if tokens[0].upper() == "DB":
					value = self.tryParseImmediate_INT(tokens[1])
			elif typeId == self.TYPE_BLOCK_FB:
				if tokens[0].upper() == "FB":
					value = self.tryParseImmediate_INT(tokens[1])
			elif typeId == self.TYPE_BLOCK_FC:
				if tokens[0].upper() == "FC":
					value = self.tryParseImmediate_INT(tokens[1])
		elif len(tokens) == 1:
			if typeId == self.TYPE_BOOL:
				value = self.tryParseImmediate_BOOL(
						tokens[0])
			elif typeId == self.TYPE_BYTE:
				value = self.tryParseImmediate_HexByte(
						tokens[0])
			elif typeId == self.TYPE_WORD:
				value = self.tryParseImmediate_Bin(
						tokens[0])
				if value is None:
					value = self.tryParseImmediate_HexWord(
							tokens[0])
				if value is None:
					value = self.tryParseImmediate_BCD(
							tokens[0])
			elif typeId == self.TYPE_DWORD:
				value = self.tryParseImmediate_Bin(
						tokens[0])
				if value is None:
					value = self.tryParseImmediate_HexDWord(
							tokens[0])
			elif typeId == self.TYPE_INT:
				value = self.tryParseImmediate_INT(
						tokens[0])
			elif typeId == self.TYPE_DINT:
				value = self.tryParseImmediate_DINT(
						tokens[0])
			elif typeId == self.TYPE_REAL:
				value = self.tryParseImmediate_REAL(
						tokens[0])
			elif typeId == self.TYPE_S5T:
				value = self.tryParseImmediate_S5T(
						tokens[0])
			elif typeId == self.TYPE_TIME:
				value = self.tryParseImmediate_TIME(
						tokens[0])
			elif typeId == self.TYPE_CHAR:
				value = self.tryParseImmediate_CHAR(
						tokens[0])
			elif typeId == self.TYPE_DATE:
				value = self.tryParseImmediate_DATE(
						tokens[0])
		if value is None:
			raise AwlSimError("Immediate value '%s' does "
				"not match data type '%s'" %\
				(" ".join(tokens), str(self)))
		return value

	def __repr__(self):
		if self.type == self.TYPE_ARRAY:
			return "ARRAY" #TODO
		elif self.type in (self.TYPE_DB_X,
				   self.TYPE_OB_X,
				   self.TYPE_FC_X,
				   self.TYPE_SFC_X,
				   self.TYPE_FB_X,
				   self.TYPE_SFB_X,
				   self.TYPE_UDT_X):
			return "%s %d" % (
				self.__id2name[self.type],
				self.index,
			)
		try:
			return self.__id2name[self.type]
		except KeyError:
			raise AwlSimError("Invalid data type: " +\
					  str(type))

	@classmethod
	def tryParseImmediate_BOOL(cls, token):
		token = token.upper().strip()
		if token == "TRUE":
			return 1
		elif token == "FALSE":
			return 0
		return None

	@classmethod
	def tryParseImmediate_INT(cls, token):
		try:
			immediate = int(token, 10)
			if immediate > 32767 or immediate < -32768:
				raise AwlSimError("16-bit immediate overflow")
		except ValueError:
			return None
		return immediate

	@classmethod
	def tryParseImmediate_DINT(cls, token):
		token = token.upper()
		if not token.startswith("L#"):
			return None
		try:
			immediate = int(token[2:], 10)
			if immediate > 2147483647 or\
			   immediate < -2147483648:
				raise AwlSimError("32-bit immediate overflow")
			immediate &= 0xFFFFFFFF
		except ValueError as e:
			raise AwlSimError("Invalid immediate")
		return immediate

	@classmethod
	def tryParseImmediate_BCD_word(cls, token):
		token = token.upper()
		if not token.startswith("C#"):
			return None
		try:
			cnt = token[2:]
			if len(cnt) < 1 or len(cnt) > 3:
				raise ValueError
			a, b, c = 0, 0, 0
			if cnt:
				a = int(cnt[-1], 10)
				cnt = cnt[:-1]
			if cnt:
				b = int(cnt[-1], 10)
				cnt = cnt[:-1]
			if cnt:
				c = int(cnt[-1], 10)
				cnt = cnt[:-1]
			immediate = a | (b << 4) | (c << 8)
		except ValueError as e:
			raise AwlSimError("Invalid C# immediate")
		return immediate

	@classmethod
	def tryParseImmediate_REAL(cls, token):
		try:
			immediate = float(token)
			immediate = pyFloatToDWord(immediate)
		except ValueError:
			return None
		return immediate

	@classmethod
	def __parseGenericTime(cls, token):
		# Parse T# or S5T# time formats.
		# The prefix is already stripped.
		if not token:
			raise AwlSimError("Invalid time")
		token = token.upper()
		p = token
		seconds = 0.0
		while p:
			if p.endswith("MS"):
				mult = 0.001
				p = p[:-2]
			elif p.endswith("S"):
				mult = 1.0
				p = p[:-1]
			elif p.endswith("M"):
				mult = 60.0
				p = p[:-1]
			elif p.endswith("H"):
				mult = 3600.0
				p = p[:-1]
			elif p.endswith("D"):
				mult = 86400.0
				p = p[:-1]
			else:
				raise AwlSimError("Invalid time")
			if not p:
				raise AwlSimError("Invalid time")
			num = ""
			while p and p[-1] in "0123456789":
				num = p[-1] + num
				p = p[:-1]
			if not num:
				raise AwlSimError("Invalid time")
			num = int(num, 10)
			seconds += num * mult
		return seconds

	@classmethod
	def formatTime(cls, seconds, leadingZeros=False):
		# Format a seconds value into time format.
		d = int(seconds // 86400)
		seconds -= d * 86400
		h = int(seconds // 3600)
		seconds -= h * 3600
		m = int(seconds // 60)
		seconds -= m * 60
		s = int(seconds)
		seconds -= s
		ms = int(seconds * 1000.0)
		ret = []
		for v, b, d in ((d, "d", 1), (h, "h", 2), (m, "m", 2),
				(s, "s", 2), (ms, "ms", 3)):
			if not v:
				continue
			if leadingZeros:
				fmt = "%0" + str(d) + "d%s"
				ret.append(fmt % (v, b))
			else:
				ret.append("%d%s" % (v, b))
		if not ret:
			return "0ms"
		return "".join(ret)

	@classmethod
	def __tryParseImmediate_STRING(cls, token, maxLen):
		if not token.startswith("'") or\
		   not token.endswith("'"):
			return None
		token = token[1:-1]
		if len(token) > maxLen:
			raise AwlSimError("String too long (>%d characters)" % maxLen)
		value = 0
		for c in token:
			value <<= 8
			value |= ord(c)
		return value

	@classmethod
	def tryParseImmediate_STRING(cls, token):
		return cls.__tryParseImmediate_STRING(token, 4)

	@classmethod
	def tryParseImmediate_CHAR(cls, token):
		return cls.__tryParseImmediate_STRING(token, 1)

	@classmethod
	def tryParseImmediate_S5T(cls, token):
		token = token.upper()
		if not token.startswith("S5T#"):
			return None
		seconds = cls.__parseGenericTime(token[4:])
		s5t = Timer.seconds_to_s5t(seconds)
		return s5t

	@classmethod
	def tryParseImmediate_TIME(cls, token):
		token = token.upper()
		if not token.startswith("T#"):
			return None
		seconds = cls.__parseGenericTime(token[2:])
		msec = int(seconds * 1000)
		if msec > 0x7FFFFFFF:
			raise AwlSimError("T# time too big")
		return msec

	@classmethod
	def tryParseImmediate_TOD(cls, tokens):
		token = "".join(tokens)
		if not token.startswith("TOD#") and\
		   not token.startswith("TIME_OF_DAY#"):
			return None
		token = token[token.find("#") + 1 : ] # Remove prefix
		try:
			time = token.split(":")
			if len(time) != 3:
				raise ValueError
			hours, minutes, fseconds = int(time[0]), int(time[1]), float(time[2])
			seconds = int(fseconds)
			msecs = int(fseconds * 1000) - (seconds * 1000)
			if hours < 0 or hours > 23 or\
			   minutes < 0 or minutes > 59 or\
			   seconds < 0 or seconds > 59 or\
			   msecs < 0 or msecs > 999:
				raise ValueError
			val = hours * 60 * 60 * 1000 +\
			      minutes * 60 * 1000 +\
			      seconds * 1000 +\
			      msecs
			return val
		except ValueError:
			raise AwlSimError("Invalid TIME_OF_DAY immediate")

	@classmethod
	def tryParseImmediate_DATE(cls, token):
		token = token.upper()
		if not token.startswith("D#") and\
		   not token.startswith("DATE#"):
			return None
		token = token[token.find("#") + 1 : ] # Remove prefix
		try:
			date = token.split("-")
			if len(date) != 3:
				raise ValueError
			year, month, day = int(date[0]), int(date[1]), int(date[2])
			delta = datetime.date(year, month, day) -\
				datetime.date(1990, 1, 1)
			days = delta.days
			if days < 0 or days > 65378:
				raise ValueError
			return days
		except ValueError:
			raise AwlSimError("Invalid DATE immediate")

	dateAndTimeWeekdayMap = {
		0	: 2,	# monday
		1	: 3,	# tuesday
		2	: 4,	# wednesday
		3	: 5,	# thursday
		4	: 6,	# friday
		5	: 7,	# saturday
		6	: 1,	# sunday
	}

	@classmethod
	def tryParseImmediate_DT(cls, tokens):
		token = "".join(tokens)
		if not token.startswith("DT#") and\
		   not token.startswith("DATE_AND_TIME#"):
			return None
		token = token[token.find("#") + 1 : ] # Remove prefix
		try:
			idx = token.rfind("-")
			date = token[ : idx]
			time = token[idx + 1 : ]
			date = date.split("-")
			time = time.split(":")
			if len(date) != 3 or len(time) != 3:
				raise ValueError
			year, month, day = int(date[0]), int(date[1]), int(date[2])
			weekday = datetime.date(year, month, day).weekday()
			weekday = cls.dateAndTimeWeekdayMap[weekday]
			if year >= 100:
				year -= 1900
				if year > 99:
					year -= 100
			if year < 0 or year > 99 or\
			   month < 1 or month > 12 or\
			   day < 1 or day > 31:
				raise ValueError
			year = (year % 10) | (((year // 10) % 10) << 4)
			month = (month % 10) | (((month // 10) % 10) << 4)
			day = (day % 10) | (((day // 10) % 10) << 4)
			hour, minute, fsecond = int(time[0]), int(time[1]), float(time[2])
			second = int(fsecond)
			msec = int(fsecond * 1000) - (second * 1000)
			if hour < 0 or hour > 23 or\
			   minute < 0 or minute > 59 or\
			   second < 0 or second > 59 or\
			   msec < 0 or msec > 999:
				raise ValueError
			hour = (hour % 10) | (((hour // 10) % 10) << 4)
			minute = (minute % 10) | (((minute // 10) % 10) << 4)
			second = (second % 10) | (((second // 10) % 10) << 4)
			msec = (msec % 10) | (((msec // 10) % 10) << 4) |\
			       (((msec // 100) % 10) << 8)
			data = ByteArray( (year, month, day, hour, minute, second,
					   (msec >> 4) & 0xFF,
					   ((msec & 0xF) << 4) | weekday) )
		except ValueError:
			raise AwlSimError("Invalid DATE_AND_TIME immediate")
		return data

	@classmethod
	def __parsePtrOffset(cls, string):
		try:
			values = string.split(".")
			if len(values) != 2:
				raise ValueError
			byteOffset = int(values[0], 10)
			bitOffset = int(values[1], 10)
			if bitOffset < 0 or bitOffset > 7 or\
			   byteOffset < 0 or byteOffset > 0x1FFFFF:
				raise ValueError
			return (byteOffset << 3) | bitOffset
		except ValueError:
			raise AwlSimError("Invalid pointer offset")

	@classmethod
	def tryParseImmediate_Pointer(cls, tokens):
		prefix = tokens[0].upper()
		if not prefix.startswith("P#"):
			return None, None
		prefix = prefix[2:] # Strip P#
		try:
			if prefix == "P":
				ptr = cls.__parsePtrOffset(tokens[1]) |\
					0x80000000
				return ptr, 2
			elif prefix in ("E", "I"):
				ptr = cls.__parsePtrOffset(tokens[1]) |\
					0x81000000
				return ptr, 2
			elif prefix in ("A", "Q"):
				ptr = cls.__parsePtrOffset(tokens[1]) |\
					0x82000000
				return ptr, 2
			elif prefix == "M":
				ptr = cls.__parsePtrOffset(tokens[1]) |\
					0x83000000
				return ptr, 2
			elif prefix == "DBX":
				ptr = cls.__parsePtrOffset(tokens[1]) |\
					0x84000000
				return ptr, 2
			elif prefix == "DIX":
				ptr = cls.__parsePtrOffset(tokens[1]) |\
					0x85000000
				return ptr, 2
			elif prefix == "L":
				ptr = cls.__parsePtrOffset(tokens[1]) |\
					0x86000000
				return ptr, 2
			else:
				# Area-internal pointer
				ptr = cls.__parsePtrOffset(prefix)
				return ptr, 1
		except IndexError:
			raise AwlSimError("Invalid pointer immediate")

	@classmethod
	def tryParseImmediate_Bin(cls, token):
		token = token.upper()
		if not token.startswith("2#"):
			return None
		try:
			string = token[2:].replace('_', '')
			immediate = int(string, 2)
			if immediate > 0xFFFFFFFF:
				raise ValueError
		except ValueError as e:
			raise AwlSimError("Invalid immediate")
		return immediate

	@classmethod
	def tryParseImmediate_ByteArray(cls, tokens):
		tokens = [ t.upper() for t in tokens ]
		if not tokens[0].startswith("B#("):
			return None, None
		try:
			if len(tokens) >= 5 and\
			   tokens[2] == ',' and\
			   tokens[4] == ')':
				fields = 5
				a, b = int(tokens[1], 10),\
				       int(tokens[3], 10)
				if a < 0 or a > 0xFF or\
				   b < 0 or b > 0xFF:
					raise ValueError
				immediate = (a << 8) | b
			elif len(tokens) >= 9 and\
			     tokens[2] == ',' and\
			     tokens[4] == ',' and\
			     tokens[6] == ',' and\
			     tokens[8] == ')':
				fields = 9
				a, b, c, d = int(tokens[1], 10),\
					     int(tokens[3], 10),\
					     int(tokens[5], 10),\
					     int(tokens[7], 10)
				if a < 0 or a > 0xFF or\
				   b < 0 or b > 0xFF or\
				   c < 0 or c > 0xFF or\
				   d < 0 or d > 0xFF:
					raise ValueError
				immediate = (a << 24) | (b << 16) |\
					    (c << 8) | d
			else:
				raise ValueError
		except ValueError as e:
			raise AwlSimError("Invalid immediate")
		return immediate, fields

	@classmethod
	def tryParseImmediate_HexByte(cls, token):
		token = token.upper()
		if not token.startswith("B#16#"):
			return None
		try:
			immediate = int(token[5:], 16)
			if immediate > 0xFF:
				raise ValueError
		except ValueError as e:
			raise AwlSimError("Invalid immediate")
		return immediate

	@classmethod
	def tryParseImmediate_HexWord(cls, token):
		token = token.upper()
		if not token.startswith("W#16#"):
			return None
		try:
			immediate = int(token[5:], 16)
			if immediate > 0xFFFF:
				raise ValueError
		except ValueError as e:
			raise AwlSimError("Invalid immediate")
		return immediate

	@classmethod
	def tryParseImmediate_HexDWord(cls, token):
		token = token.upper()
		if not token.startswith("DW#16#"):
			return None
		try:
			immediate = int(token[6:], 16)
			if immediate > 0xFFFFFFFF:
				raise ValueError
		except ValueError as e:
			raise AwlSimError("Invalid immediate")
		return immediate

class GenericInteger(object): #+cdef

#@cy	cdef public uint32_t value
#@cy	cdef public uint32_t mask

	def __init__(self, value, width): #@nocy
#@cy	def __init__(self, int64_t value, uint8_t width):
#@cy		cdef uint64_t one

		assert(width > 0 and width <= 32)
		self.value = value
		one = 1
		self.mask = int(((one << width) - 1) & 0xFFFFFFFF)

	def copyFrom(self, other): #@nocy
#@cy	cpdef copyFrom(self, GenericInteger other):
		self.value = other.value & self.mask

	def reset(self): #@nocy
#@cy	cpdef reset(self):
		self.value = 0

	def set(self, value): #@nocy
#@cy	cpdef set(self, int64_t value):
		self.value = value & self.mask

	def setByte(self, value): #@nocy
#@cy	cpdef setByte(self, int64_t value):
		self.value = ((self.value & 0xFFFFFF00) |\
			      (value & 0xFF)) &\
			     self.mask

	def setWord(self, value): #@nocy
#@cy	cpdef setWord(self, int64_t value):
		self.value = ((self.value & 0xFFFF0000) |\
			      (value & 0xFFFF)) &\
			     self.mask

	def setDWord(self, value): #@nocy
#@cy	cpdef setDWord(self, int64_t value):
		self.value = value & 0xFFFFFFFF & self.mask

	def setPyFloat(self, pyfl): #@nocy
#@cy	cpdef setPyFloat(self, pyfl):
		self.value = pyFloatToDWord(pyfl)

	def get(self): #@nocy
#@cy	cpdef uint32_t get(self):
		return self.value

	def getByte(self): #@nocy
#@cy	cpdef uint8_t getByte(self):
		return self.value & 0xFF

	def getWord(self): #@nocy
#@cy	cpdef uint16_t getWord(self):
		return self.value & 0xFFFF

	def getDWord(self): #@nocy
#@cy	cpdef uint32_t getDWord(self):
		return self.value & 0xFFFFFFFF

	def getSignedByte(self): #@nocy
#@cy	cpdef int8_t getSignedByte(self):
		return byteToSignedPyInt(self.value)

	def getSignedWord(self): #@nocy
#@cy	cpdef int16_t getSignedWord(self):
		return wordToSignedPyInt(self.value)

	def getSignedDWord(self): #@nocy
#@cy	cpdef int32_t getSignedDWord(self):
		return dwordToSignedPyInt(self.value)

	def getPyFloat(self): #@nocy
#@cy	cpdef getPyFloat(self):
		return dwordToPyFloat(self.value)

	def setBit(self, bitNumber): #@nocy
#@cy	cpdef setBit(self, uint8_t bitNumber):
		self.value = (self.value | (1 << bitNumber)) & self.mask

	def clearBit(self, bitNumber): #@nocy
#@cy	cpdef clearBit(self, uint8_t bitNumber):
		self.value &= ~(1 << bitNumber)

	def setBitValue(self, bitNumber, value): #@nocy
#@cy	cpdef setBitValue(self, uint8_t bitNumber, uint8_t value):
		if value:
			self.setBit(bitNumber)
		else:
			self.clearBit(bitNumber)

	def getBit(self, bitNumber): #@nocy
#@cy	cpdef unsigned char getBit(self, uint8_t bitNumber):
		return (self.value >> bitNumber) & 1

	def toHex(self):
		if self.mask == 0xFF:
			return "%02X" % self.value
		elif self.mask == 0xFFFF:
			return "%04X" % self.value
		elif self.mask == 0xFFFFFFFF:
			return "%08X" % self.value
		else:
			assert(0)

class GenericWord(GenericInteger): #+cdef
	def __init__(self, value=0):
		GenericInteger.__init__(self, value, 16)

class GenericDWord(GenericInteger): #+cdef
	def __init__(self, value=0):
		GenericInteger.__init__(self, value, 32)

class ByteArray(bytearray):
	"""Generic memory representation."""

	# "Natural" memory fetch operation.
	# This method returns the natural data (byte, word, dword) for
	# a given memory region of this byte array.
	# offset => An AwlOffset() that specifies the region to fetch from.
	# width => An integer specifying the width (in bits) to fetch.
	def fetch(self, offset, width): #@nocy
#@cy	def fetch(self, object offset, uint32_t width):
#@cy		cdef uint32_t byteOffset

		byteOffset = offset.byteOffset
		try:
			if width == 1:
				return (self[byteOffset] >> offset.bitOffset) & 1
			elif width == 8:
				return self[byteOffset]
			elif width == 16:
				return (self[byteOffset] << 8) |\
				       self[byteOffset + 1]
			elif width == 32:
				return (self[byteOffset] << 24) |\
				       (self[byteOffset + 1] << 16) |\
				       (self[byteOffset + 2] << 8) |\
				       self[byteOffset + 3]
			else:
				assert(not offset.bitOffset)
				nrBytes = intDivRoundUp(width, 8)
				if byteOffset + nrBytes > len(self):
					raise IndexError
				return memoryview(self)[byteOffset : byteOffset + nrBytes]
		except IndexError as e:
			raise AwlSimError("fetch: Operator offset '%s' out of range" %\
					  str(offset))

	# Fetch bytes from this memory region.
	# Returns a view of the memory region bytes (not a copy!).
	# offset => An AwlOffset() that specifies the region to fetch from.
	# width => An integer specifying the width (in bits) to fetch.
	def fetchBytes(self, offset, width):
		#TODO optimize me!
		bytesBuf = ByteArray(intDivRoundUp(width, 8))
		WordPacker.toBytes(bytesBuf, width, 0, self.fetch(offset, width))
		return bytesBuf

	# "Natural" memory store operation.
	# This method stores natural data (byte, word, dword) to
	# a given memory region of this byte array.
	# offset => An AwlOffset() that specifies the region to store to.
	# width => An integer specifying the width (in bits) to store.
	# value => The value to store. May be an integer (byte, word, dword) or
	#          a byte array for large types (>32 bit).
	def store(self, offset, width, value): #@nocy
#@cy	def store(self, object offset, uint32_t width, object value):
#@cy		cdef uint32_t byteOffset

		byteOffset = offset.byteOffset
		try:
			if width == 1:
				if value:
					self[byteOffset] |= 1 << offset.bitOffset
				else:
					self[byteOffset] &= ~(1 << offset.bitOffset)
			elif width == 8:
				self[byteOffset] = value & 0xFF
			elif width == 16:
				self[byteOffset] = (value >> 8) & 0xFF
				self[byteOffset + 1] = value & 0xFF
			elif width == 32:
				self[byteOffset] = (value >> 24) & 0xFF
				self[byteOffset + 1] = (value >> 16) & 0xFF
				self[byteOffset + 2] = (value >> 8) & 0xFF
				self[byteOffset + 3] = value & 0xFF
			else:
				assert(not offset.bitOffset)
				nrBytes = intDivRoundUp(width, 8)
				assert(nrBytes == len(value))
				if byteOffset + nrBytes > len(self):
					raise IndexError
				self[byteOffset : byteOffset + len(value)] = value
		except IndexError as e:
			raise AwlSimError("store: Operator offset '%s' out of range" %\
					  str(offset))

	# Store bytes to this memory region.
	# offset => An AwlOffset() that specifies the region to store to.
	# width => An integer specifying the width (in bits) to store.
	# valueBytes => The bytes to store.
	def storeBytes(self, offset, width, valueBytes):
		#TODO optimize me!
		self.store(offset, width, WordPacker.fromBytes(valueBytes, width))

	def __repr__(self):
		ret = [ 'ByteArray(b"', ]
		for b in self:
			ret.append("\\x%02X" % b)
		ret.append('")')
		return "".join(ret)

	def __str__(self):
		return self.__repr__()

class Accu(GenericDWord): #+cdef
	"Accumulator register"

	def __init__(self):
		GenericDWord.__init__(self)

class Adressregister(GenericDWord): #+cdef
	"Address register"

	def __init__(self):
		GenericDWord.__init__(self)

	def toPointerString(self):
		value = self.getDWord()
		area = (value >> 24) & 0xFF
		if area:
			if area == 0x80:
				prefix = "P"
			elif area == 0x81:
				prefix = "E"
			elif area == 0x82:
				prefix = "A"
			elif area == 0x83:
				prefix = "M"
			elif area == 0x84:
				prefix = "DBX"
			elif area == 0x85:
				prefix = "DIX"
			elif area == 0x86:
				prefix = "L"
			elif area == 0x87:
				prefix = "V"
			else:
				prefix = "(%02X)" % area
			prefix += " "
		else:
			prefix = ""
		byteOffset = (value & 0x00FFFFFF) >> 3
		bitOffset = value & 7
		return "P#%s%d.%d" % (prefix, byteOffset, bitOffset)
