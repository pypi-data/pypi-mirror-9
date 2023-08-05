# -*- coding: utf-8 -*-
#
# AWL simulator - GUI symbol table edit widget
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


class SymTabModel(QAbstractTableModel):
	# Signal: Emitted, if the source code changed.
	sourceChanged = Signal()

	def __init__(self, symTab):
		QAbstractTableModel.__init__(self)
		self.symTab = symTab
		self.__source = SymTabSource("Unnamed symbol table")
		self.__needSourceUpdate = True

	def emitSourceChanged(self):
		self.__needSourceUpdate = True
		self.sourceChanged.emit()

	def revert(self):
		QAbstractTableModel.revert(self)
		self.__needSourceUpdate = True

	def getSymTab(self):
		return self.symTab

	def deleteSymbol(self, row):
		if row >= 0 and row < len(self.symTab.symbols):
			self.beginResetModel()
			del self.symTab.symbols[row]
			self.endResetModel()
			self.emitSourceChanged()

	def moveSymbol(self, fromRow, toRow):
		self.beginResetModel()
		sym = self.symTab.symbols.pop(fromRow)
		self.symTab.symbols.insert(toRow, sym)
		self.endResetModel()
		self.emitSourceChanged()

	def rowCount(self, parent=QModelIndex()):
		return len(self.symTab.symbols) + 1

	def columnCount(self, parent=QModelIndex()):
		return 4

	def data(self, index, role=Qt.DisplayRole):
		if not index:
			return None
		row, column = index.row(), index.column()
		if role in (Qt.DisplayRole, Qt.EditRole):
			if row >= len(self.symTab.symbols):
				return None
			sym = self.symTab.symbols[row]
			if column == 0:
				return sym.getName()
			elif column == 1:
				return sym.getOperatorString()
			elif column == 2:
				return sym.getTypeString()
			else:
				return sym.getComment()
		elif role == Qt.BackgroundRole:
			if row >= len(self.symTab.symbols) or\
			   self.symTab.symbols[row].isValid():
				return QBrush(QColor("white"))
			return QBrush(QColor("red"))
		elif role in (Qt.ToolTipRole, Qt.WhatsThisRole):
			return (
				"The symbol name.\n(The name is case insensitive.)",
				"The symbol address.\nFor example:  M 0.0  or  QW 0",
				"The symbol data type.\nFor example: BOOL  or  INT",
				"",
			)[column]
		return None

	def headerData(self, section, orientation, role=Qt.DisplayRole):
		if role != Qt.DisplayRole:
			return None
		if orientation == Qt.Horizontal:
			return ("Symbol", "Address", "Data type", "Comment")[section]
		else:
			if section >= len(self.symTab.symbols):
				return "new"
			return "%d" % (section + 1)

	def setData(self, index, value, role=Qt.EditRole):
		if not index:
			return False
		if role == Qt.EditRole:
			row, column = index.row(), index.column()
			if row >= len(self.symTab.symbols):
				sym = Symbol()
				self.symTab.add(sym)
				self.rowsInserted.emit(QModelIndex(),
					len(self.symTab.symbols),
					len(self.symTab.symbols))
			else:
				sym = self.symTab.symbols[row]
			try:
				if column == 0:
					sym.setName(value.strip())
				elif column == 1:
					sym.setOperatorString(value)
				elif column == 2:
					sym.setTypeString(value)
				else:
					sym.setComment(value.strip())
			except AwlSimError as e:
				MessageBox.handleAwlSimError(None,
					"Invalid symbol information", e)
				return False
			self.emitSourceChanged()
			return True
		return False

	def flags(self, index):
		if not index:
			return Qt.ItemIsEnabled
		return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable

	def getSource(self):
		if self.__needSourceUpdate:
			self.__updateSource()
		return self.__source

	def __updateSource(self):
		try:
			self.__source.sourceBytes = self.symTab.toASC()
		except AwlSimError as e:
			MessageBox.handleAwlSimError(None,
				"Symbol table contains invalid characters", e)
			return
		self.__needSourceUpdate = False

	def setSource(self, newSource):
		self.beginResetModel()
		try:
			self.symTab = SymbolTable()
			self.__source = newSource.dup()
			self.__source.sourceBytes = b""
			self.symTab = SymTabParser.parseData(newSource.sourceBytes)
		except AwlSimError as e:
			MessageBox.handleAwlSimError(None,
				"Could not parse symbol table information", e)
		finally:
			self.endResetModel()
			self.__needSourceUpdate = True

class SymTabView(QTableView):
	# Signal: Keyboard focus in/out event.
	focusChanged = Signal(bool)

	def __init__(self, parent=None):
		QTableView.__init__(self, parent)

		if isQt4:
			self.verticalHeader().setMovable(True)
		else:
			self.verticalHeader().setSectionsMovable(True)
		self.verticalHeader().sectionMoved.connect(self.__rowMoved)

		self.pressed.connect(self.__handleMousePress)

	def __rebuild(self):
		model = self.model()
		yscroll = self.verticalScrollBar().value()
		xscroll = self.horizontalScrollBar().value()
		self.setModel(None)
		self.setModel(model)
		self.verticalScrollBar().setValue(yscroll)
		self.horizontalScrollBar().setValue(xscroll)

	def __rowMoved(self, logicalIndex, oldVisualIndex, newVisualIndex):
		self.model().moveSymbol(oldVisualIndex, newVisualIndex)
		self.__rebuild()

	def resizeEvent(self, ev):
		QTableView.resizeEvent(self, ev)
		hdr = self.horizontalHeader()
		if hdr.sectionSize(0) < 150:
			hdr.resizeSection(0, 150)
		if hdr.sectionSize(3) < 200:
			hdr.resizeSection(3, 200)

	def deleteSym(self, index=None):
		if not index:
			index = self.currentIndex()
		if not index:
			return
		self.model().deleteSymbol(index.row())

	def __handleMousePress(self, index):
		btns = QApplication.mouseButtons()
		if btns & Qt.RightButton:
			pass#TODO context menu

	def keyPressEvent(self, ev):
		QTableView.keyPressEvent(self, ev)

		if ev.key() == Qt.Key_Delete:
			self.deleteSym()

	def focusInEvent(self, ev):
		QTableView.focusInEvent(self, ev)
		self.focusChanged.emit(True)

	def focusOutEvent(self, ev):
		QTableView.focusOutEvent(self, ev)
		self.focusChanged.emit(False)

	def setSymTab(self, symTab):
		self.setModel(SymTabModel(symTab))

	def getSymTab(self):
		return self.model().getSymTab()

	def getSource(self):
		return self.model().getSource()

	def setSource(self, newSource):
		return self.model().setSource(newSource)
