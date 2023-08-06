# -*- coding: utf-8 -*-
from gavi.vaex.qt import *
import math

import gavi.logging
logger = gavi.logging.getLogger("vaex.table")


PAGE_LIMIT = long(1e7)

class FullTableModel(QtCore.QAbstractTableModel): 
	def __init__(self, dataset,  page_size, page, parent=None, *args): 
		QtCore.QAbstractTableModel.__init__(self, parent, *args) 
		self.dataset = dataset
		self.page_size = page_size
		self.page = page
		self.row_count_start = 1
	
	def rowCount(self, parent): 
		#print self.dataset._length
		#return int(self.dataset._length)
		left_over = len(self.dataset) - self.page * self.page_size
		if left_over < 0:
			return 0
		elif left_over < self.page_size:
			return left_over
		else:
			return self.page_size
		
	def set_page(self, page):
		self.page = page

	def get_row_offset(self):
		return self.page * self.page_size

	def columnCount(self, parent): 
		return len(self.dataset.all_column_names)+1

	def data(self, index, role):
		#return ""
		row_offset = self.get_row_offset()
		if not index.isValid(): 
			return None
		elif role != QtCore.Qt.DisplayRole: 
			return None
		if index.column() == 0:
			return "{:,}".format(index.row()+self.row_count_start + row_offset)
		else:
			column = self.dataset.all_columns[self.dataset.all_column_names[index.column()-1]]
			if len(column.shape) == 1:
				return str(column[row_offset + index.row()])
			else:
				return "%s %s" % (column.dtype.name, column.shape)

	def headerData(self, index, orientation, role):
		#print index
		row_offset = self.get_row_offset()
		if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
			if index == 0:
				return "row"
			else:
				return self.dataset.all_column_names[index-1]
		#if orientation == QtCore.Qt.Vertical and role == QtCore.Qt.DisplayRole:
		#	return str(index+self.row_count_start + row_offset)
		return None

class TableDialog(QtGui.QDialog):
	def __init__(self, dataset, parent):
		super(TableDialog, self).__init__(parent)
		self.dataset = dataset
		#self.setModal(False)
		#self.setWindowFlags(QtCore.Qt#.FramelessWindowHint)
		
		self.resize(700, 500)
		self.tableView = QtGui.QTableView()
		self.tableView.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows);
		self.header = self.dataset.column_names
		self.tableModel = FullTableModel(self.dataset, PAGE_LIMIT, 0, self)
		self.tableView.setModel(self.tableModel)
		self.tableView.pressed.connect(self.onSelectRow)
		
		self.tableView.verticalHeader().setResizeMode(QtGui.QHeaderView.Interactive)
		
		if 0:
			for name in self.dataset.column_names:
				item = QtGui.QListWidgetItem(self.list1d)
				item.setText(name)
				item.setCheckState(False)
				#self.list1d.

		print len(self.dataset)
		pages = int(math.ceil(len(self.dataset)*1./self.tableModel.page_size))

		self.boxlayout = QtGui.QVBoxLayout(self)
		self.header_layout = QtGui.QHBoxLayout(self)
		self.spinner = QtGui.QSpinBox(self)
		self.label_prefix = QtGui.QLabel("should not see me")
		self.label_postfix = QtGui.QLabel("should not see me")
		self.header_layout.addWidget(self.label_prefix)
		self.header_layout.addWidget(self.spinner)
		self.header_layout.addWidget(self.label_postfix)

		self.count_from_zero = QtGui.QCheckBox("count rows from zero", self)
		self.boxlayout.addWidget(self.count_from_zero)
		self.boxlayout.addLayout(self.header_layout)
		self.boxlayout.addWidget(self.tableView)
		#self.setCentralWidget(self.splitter)
		self.setLayout(self.boxlayout)
		
		self.spinner.setRange(1, pages)
		#self.spinner.setValue(1)
		self.spinner.valueChanged.connect(self.onValueChanged)
		self.count_from_zero.stateChanged.connect(self.onStateCountFromZero)
		
		self.dataset.row_selection_listeners.append(self.onRowSelect)
		if self.dataset.selected_row_index is not None:
			self.onRowSelect(self.dataset.selected_row_index)
		self._check_pages()
		
	def onStateCountFromZero(self, state):
		self.tableModel.row_count_start = 0 if state == QtCore.Qt.Checked else 1
		self._update_info()
		self.update()
		# hide/show to force an update
		self.tableView.hide()
		self.tableView.show()
		#self.tableView.repaint()
		#self.tableModel.update()
		#self.resize(self.size())
		
	def _check_pages(self):
		pages = int(math.ceil(len(self.dataset)*1./self.tableModel.page_size))
		current_page = self.spinner.value() - 1
		# if 2 pages, pages 0 and 1 are ok..
		if current_page > pages-1: # oops, spinner has invalid value
			self.spinner.setValue(pages+1) # then again, gui has page+1
		self._update_info()

	def _update_info(self):
		pages = int(math.ceil(len(self.dataset)*1./self.tableModel.page_size))
		current_page = self.spinner.value() - 1
		row_from = current_page * self.tableModel.page_size +	self.tableModel.row_count_start
		row_to = row_from + self.tableModel.page_size -1
		if row_to > len(self.dataset):
			row_to = len(self.dataset) - 1 + self.tableModel.row_count_start
		info_text = "of {pages:,} (row {row_from:,} to {row_to:,})".format(**locals())
		self.label_postfix.setText(info_text)
		self.spinner.setRange(1, pages)
		
		rows_visible = len(self.dataset) if pages == 1 else self.tableModel.page_size
		
		info_text_pre = "showing {rows_visible:,} rows on page".format(**locals())
		self.label_prefix.setText(info_text_pre)

	def onRowSelect(self, row):
		self._check_pages()
		if row is None:
			return
		page = int(row * 1./ self.tableModel.page_size)
		row_offset = row - page * self.tableModel.page_size
		#selection_model = self.tableView.selectionModel()
		#item_model = QtGui.QAbstractItemModel()
		#index = item_model.createIndex(row_offset)
		#selection_model.setCurrentIndex(index)
		self.tableView.selectRow(row_offset)
		self.spinner.setValue(page+1) # in GUI, pages starts from 1
		self._update_info()
		#self.tableView.resizeColumnToContents(0)
		
	def onValueChanged(self, value):
		self.tableModel.set_page(value-1) # in GUI, pages start counting from 1, in the code from 0
		self._check_row_select()
		self._update_info()
		# next two lines make the first column (row index) fit to with under osx (bug?)
		#self.tableView.verticalHeader().resizeSections(QtGui.QHeaderView.Stretch)
		#self.tableView.verticalHeader().resizeSections(QtGui.QHeaderView.ResizeToContents)
		self.update()
		
	def _check_row_select(self):
		row_index = self.dataset.selected_row_index
		if row_index is None:
			return
		page = int(row_index / self.tableModel.page_size)
		page_current = self.spinner.value()-1
		page_index = row_index - page * self.tableModel.page_size
		logger.debug("row_index=%d page=%d page_index=%d page_current=%d" % (row_index, page, page_index, page_current))
		if page == page_current: # we are in the right page
			logger.debug("select")
			self.tableView.selectRow(page_index)
		else:
			logger.debug("deselect")
			#self.tableView.selectRow(0) # deselect
			self.tableView.selectionModel().clear()
		self.update()
		
	def onSelectRow(self, model):
		row_index = model.row() + self.tableModel.get_row_offset()
		logger.debug("row index selected %d" % row_index)
		self.dataset.selectRow(row_index)
		
		
