# -*- coding: utf-8 -*-
#
# AWL simulator - Generic source code edit widget
#
# Copyright 2014 Michael Buesch <m@bues.ch>
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

from awlsim.gui.util import *


class SourceCodeEdit(QPlainTextEdit):
	# Signal: Change the font size.
	#         If the parameter is True, increase font size.
	resizeFont = Signal(bool)

	def __init__(self, parent=None):
		QPlainTextEdit.__init__(self, parent)

		self.__wheelSteps = 0.0

		self.__undoIsAvailable = False
		self.__redoIsAvailable = False
		self.__copyIsAvailable = False

		self.__prevLineNr = self.textCursor().blockNumber()
		self.__prevColumnNr = self.textCursor().columnNumber()
		self.__columnChange = False

		self.enableAutoIndent()
		self.enablePasteIndent()
		self.__validateEn = True
		self.__prevErrLines = ()

		self.cursorPositionChanged.connect(self.__handleCursorChange)
		self.undoAvailable.connect(self.__handleUndoAvailableChange)
		self.redoAvailable.connect(self.__handleRedoAvailableChange)
		self.copyAvailable.connect(self.__handleCopyAvailableChange)

	def __handleUndoAvailableChange(self, available):
		self.__undoIsAvailable = available

	def undoIsAvailable(self):
		return self.__undoIsAvailable

	def __handleRedoAvailableChange(self, available):
		self.__redoIsAvailable = available

	def redoIsAvailable(self):
		return self.__redoIsAvailable

	def __handleCopyAvailableChange(self, available):
		self.__copyIsAvailable = available

	def copyIsAvailable(self):
		return self.__copyIsAvailable

	def enableAutoIndent(self, enable=True):
		self.__autoIndentEn = enable

	def enablePasteIndent(self, enable=True):
		self.__pasteIndentEn = enable

	def enableValidation(self, enable=True):
		self.__validateEn = enable
		self.setErraticLines(())
		self.__validate()

	def __getLineIndent(self, cursor):
		cursor.select(QTextCursor.LineUnderCursor)
		line = cursor.selectedText()
		if not line:
			return ""
		# Get the indent-string (that is the whitespace line prefix)
		for i, c in enumerate(line):
			if not c.isspace():
				break
		else:
			i += 1
		return line[:i]

	def __autoIndentHandleNewline(self):
		if not self.__autoIndentEn:
			return
		# Move cursor to previous line and get its indent string.
		cursor = self.textCursor()
		if not cursor.movePosition(QTextCursor.Up,
					   QTextCursor.MoveAnchor, 1):
			return
		indentStr = self.__getLineIndent(cursor)
		# Insert the indent string into the current line
		cursor = self.textCursor()
		cursor.insertText(indentStr)
		self.setTextCursor(cursor)
		# Remove any old indent (righthand of the cursor)
		cursor = self.textCursor()
		if not cursor.movePosition(QTextCursor.EndOfLine,
					   QTextCursor.KeepAnchor, 1):
			return
		selText = cursor.selectedText()
		stripCount = len(selText) - len(selText.lstrip())
		if stripCount > 0:
			cursor = self.textCursor()
			if not cursor.movePosition(QTextCursor.Right,
						   QTextCursor.KeepAnchor,
						   stripCount):
				return
			cursor.deleteChar()

	def keyPressEvent(self, ev):
		QPlainTextEdit.keyPressEvent(self, ev)

		if ev.key() in (Qt.Key_Return, Qt.Key_Enter):
			self.__autoIndentHandleNewline()
		elif ev.key() == Qt.Key_Delete:
			self.__validate()

	def wheelEvent(self, ev):
		if ev.modifiers() & Qt.ControlModifier:
			# Ctrl + Scroll-wheel: Font resizing
			if isQt4:
				numDegrees = ev.delta() / 8
			else:
				numDegrees = ev.angleDelta().y() / 8
			numSteps = numDegrees / 15
			self.__wheelSteps += numSteps
			if self.__wheelSteps >= 1.0:
				while self.__wheelSteps >= 1.0:
					self.resizeFont.emit(False)
					self.__wheelSteps -= 1.0
			elif self.__wheelSteps <= -1.0:
				while self.__wheelSteps <= -1.0:
					self.resizeFont.emit(True)
					self.__wheelSteps += 1.0
			return
		else:
			self.__wheelSteps = 0.0

		QPlainTextEdit.wheelEvent(self, ev)

	# Add the current indent to all lines (except the first) in 'text'.
	def __makeSeamlessIndent(self, text):
		indentStr = self.__getLineIndent(self.textCursor())
		lines = []
		for i, line in enumerate(text.splitlines()):
			if i == 0:
				lines.append(line)
			else:
				lines.append(indentStr + line)
		return "\n".join(lines)

	def pasteText(self, text):
		if self.__autoIndentEn:
			text = self.__makeSeamlessIndent(text)
		self.insertPlainText(text)

	def insertFromMimeData(self, mimeData):
		if mimeData.hasText() and self.__pasteIndentEn:
			# Replace the mimeData by a re-indented mimeData.
			newText = self.__makeSeamlessIndent(mimeData.text())
			mimeData = QMimeData()
			mimeData.setText(newText)
		QPlainTextEdit.insertFromMimeData(self, mimeData)

	def __handleCursorChange(self):
		cursor = self.textCursor()
		columnNr = cursor.columnNumber()
		lineNr = cursor.blockNumber()

		if columnNr != self.__prevColumnNr:
			self.__columnChange = True

		if lineNr in self.__prevErrLines or\
		   (lineNr != self.__prevLineNr and\
		    self.__columnChange):
			self.__validate()
			self.__columnChange = False

		self.__prevColumnNr = columnNr
		self.__prevLineNr = lineNr

	def setPlainText(self, text):
		QPlainTextEdit.setPlainText(self, text)
		self.__validate()

	@staticmethod
	def __makeExtraSel(cursor, format):
		sel = QTextEdit.ExtraSelection()
		sel.cursor = cursor
		sel.format = format
		return sel

	@staticmethod
	def __makeTextCursorLineSel(cursor, lineNr):
		cursor.movePosition(QTextCursor.Start,
				    QTextCursor.MoveAnchor, 1)
		cursor.movePosition(QTextCursor.Down,
				    QTextCursor.MoveAnchor, lineNr)
		cursor.select(QTextCursor.LineUnderCursor)
		return cursor

	__errLineBrush = QBrush(QColor("#FFC0C0"))

	def __validate(self):
		if not self.__validateEn:
			return

		# Validate the current document
		text = self.toPlainText()
		if text.strip():
			# Run the validator.
			self.validateText(text, self.textCursor().blockNumber())
		else:
			# No text. Mark everything as ok.
			self.setErraticLines(())

	# Validation callback.
	# Override this in the subclass.
	# The default implementation marks everything as Ok.
	# In case of validation failure, call setErraticLines.
	def validateText(self, text, currentLineNr):
		self.setErraticLines(())

	# Mark erratic lines
	def setErraticLines(self, errLines):
		cursor = self.textCursor()
		fmt = self.currentCharFormat()
		fmt.setBackground(self.__errLineBrush)
		extraSel = [
			self.__makeExtraSel(self.__makeTextCursorLineSel(cursor, line),
					    fmt)
			for line in errLines
		]
		self.setExtraSelections(extraSel)

		self.__prevErrLines = errLines
