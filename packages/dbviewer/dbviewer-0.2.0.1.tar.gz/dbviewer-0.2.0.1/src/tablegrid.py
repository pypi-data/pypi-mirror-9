#! /usr/bin/python
# -*- coding: utf-8 -*-

import wx
import wx.grid as gridlib
import search_eng
import dbConnector
import config


class CustomDataTable(gridlib.PyGridTableBase):
	def __init__(self, argv):
		gridlib.PyGridTableBase.__init__(self)
		
		global data
		data = argv
		
		self.cp = config.confValues()
		self.db_name = str(self.cp.db_name)
		self.table_name =str(self.cp.table_name)
		dbc = dbConnector.SqlMng(self.db_name)
		
		self.colLabels = dbc.col_names(self.table_name)
		
		"""self.dataTypes = [gridlib.GRID_VALUE_NUMBER,
							gridlib.GRID_VALUE_STRING,
							gridlib.GRID_VALUE_CHOICE + "  : EAST,WEST,SOUTH,NORTH ",
							gridlib.GRID_VALUE_BOOL,
							gridlib.GRID_VALUE_FLOAT + " : 6.2",
							]"""

	def GetNumberRows (self):
		return len(data) 		#+1
		
	def GetNumberCols (self):
		if len(data[0]) != 0:
			leng = len(data[0])
		else:
			leng = 1
		return leng
		
	def IsEmptyCell (self, row, col ):
		try:
			return not data[row][col]
		except IndexError :
			return True
			
	def GetValue (self, row, col):
		try:
			return data[row][col]
		except IndexError:
			return ''
				
	def SetValue (self, row, col, value):
		def innerSetValue(row, col, value):
			try:
				data[row][col] = value
			except IndexError :
				data.append([' '] * self.GetNumberCols())
				innerSetValue (row, col, value)
				msg = gridlib.GridTableMessage(self,
				   			gridlib.GRIDTABLE_NOTIFY_ROWS_APPENDED, 1)
				self.GetView().ProcessTableMessage(msg)
				data[row][col] = value
		innerSetValue(row, col, value)
		
	def GetColLabelValue (self, col):
		return self.colLabels[col]
		
	"""def GetTypeName (self, row, col):
		return self.dataTypes[col]
		
	def CanGetValueAs (self, row, col, typeName):
		colType = self.dataTypes[col].split(' :')[0]
		if typeName == colType:
			return True
		else:
			return False
			
	def CanSetValueAs (self, row, col, typeName):
		return self.CangetValueAs (row, col, typeName)"""
	

class CustTableGrid (gridlib.Grid):
	def __init__ (self, parent):
		gridlib.Grid.__init__(self, parent, wx.ID_ANY)
		
		table = CustomDataTable(data)
		self.SetTable (table, True)
		
		self.SetRowLabelSize(0)
		self.SetMargins(0, 0)
		self.AutoSizeColumns(False)
		
		
class GridFrame(wx.Frame):
	def __init__(self, parent):
		wx.Frame.__init__(self, parent, wx.ID_ANY, "Search Results")
		
		panel = wx.Panel(self, wx.ID_ANY)
		grid = CustTableGrid(panel)
		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add (grid, 1, wx.GROW | wx.ALL, 5)
		panel.SetSizerAndFit(sizer)
		self.Centre()










