#! /usr/bin/python
# -*- coding: utf-8 -*-

"""
データ削除
"""

import wx
import sqlite3
import dbConnector as db
import copypaste
import auxiliaries
import config
import masterpanel

class Viewer (wx.Frame):
	def __init__(self, parent, title):
		wx.Frame.__init__(self, parent, wx.ID_ANY, title,
									style=wx.FRAME_FLOAT_ON_PARENT|wx.DEFAULT_FRAME_STYLE)
		
		self.items = []
		self.dataIndex = 1
		self.dbset = db_assist()
		self.table_name = self.dbset.table_name
		self.columnize = self.dbset.colName
		self.aux = auxiliaries
		self.data = self.dataMaker(1)
		
		# -------------------- Panel & Sizer --------------------------------------------
		#self.vwp = wx.Panel(self, wx.ID_ANY)
		self.vwp = masterpanel.MasterPanel(self)
		
		self.vbox = wx.BoxSizer(wx.VERTICAL)
		self.hbox = wx.BoxSizer(wx.HORIZONTAL)
		self.titlesizer = wx.BoxSizer (wx.HORIZONTAL)
		self.bodysizer = wx.BoxSizer (wx.HORIZONTAL)
		self.hbox2 = wx.BoxSizer(wx.HORIZONTAL)
		
		preitems = []
		
		for co in self.columnize:
			title=wx.StaticText(self.vwp, wx.ID_ANY, label=co)
			self.titlesizer.Add(title, 1, wx.EXPAND)
			self.titlesizer.Add((10, 10))
		for it in self.data:
			self.text = wx.TextCtrl(self.vwp, value=it, size=(100, 30), style=wx.TE_MULTILINE)
			self.text.SetFocus()
			self.bodysizer.Add(self.text, 1, wx.EXPAND)
			self.bodysizer.Add((10, 10))
			preitems.append(self.text)
		self.items = preitems
		
		# ------------------------- Buttons -------------------------------------------
		prev_btn = wx.Button(self.vwp, id = wx.ID_ANY, label="<< Prev.")
		next_btn = wx.Button(self.vwp, id = wx.ID_ANY, label="Next >>")
		canl_btn = wx.Button(self.vwp, id = wx.ID_ANY, label="Cancel")
		upd_btn = wx.Button(self.vwp, id = wx.ID_ANY, label="Delete")
		
		self.Bind(wx.EVT_BUTTON, self.data_prev, prev_btn)
		self.Bind(wx.EVT_BUTTON, self.data_next, next_btn)
		self.Bind(wx.EVT_BUTTON, self.cancel, canl_btn)
		self.Bind(wx.EVT_BUTTON, self.data_update, upd_btn)
		
		# --------------- Add Widget --------------------------------------------
		
		self.hbox.Add(prev_btn, 1)
		self.hbox.Add(next_btn, 1)
		
		self.hbox2.Add(canl_btn, 1, 5)
		self.hbox2.Add(upd_btn, 1, 5)
		
		self.vbox.Add(self.hbox, 0, wx.EXPAND | wx.ALL, 5)
		self.vbox.Add(self.titlesizer, 0, wx.EXPAND | wx.ALL, 5)
		self.vbox.Add(self.bodysizer, 0, wx.EXPAND | wx.ALL, 5)
		self.vbox.Add(self.hbox2, 0, wx.EXPAND | wx.ALL, 5)
		
		# ----------------- MenuBar ----------------------------------------
		
		self.word = self.text
		self.menu = copypaste.Copypaste(self.word)
		self.SetMenuBar(self.menu)
		self.Bind(wx.EVT_MENU, self.menu.onCut, id=106)
		self.Bind(wx.EVT_MENU, self.menu.onCopy, id=107)
		self.Bind(wx.EVT_MENU, self.menu.onPaste, id=108)
		self.Bind(wx.EVT_MENU, self.menu.onDelete, id=109)
		self.Bind(wx.EVT_MENU, self.menu.onSelectAll, id=110)
		
		# -------------------------------------------------------------------------
		
		self.vwp.SetSizer(self.vbox)
		self.Show()
		self.vbox.Fit(self)
		self.Centre()
		
	def cancel (self, event):
		self.Close()
				
	def dataMaker (self, val):
		pre_data = self.dbset.PresentData(val)
		data = []
		for i in pre_data:
			ch = str(i)
			data.append(ch)
		return data
			
	def data_prev (self, event):
		if self.dataIndex == 1:
			self.dataIndex = self.dbset.maxRow
		else:
			self.dataIndex -= 1
		for j, val in enumerate(self.dbset.PresentData(self.dataIndex)):
			self.items[j].SetValue(str(val))
			
	def data_next (self, event):
		if self.dataIndex == self.dbset.maxRow:
			self.dataIndex = 1
		else:
			self.dataIndex += 1
		for j, val in enumerate(self.dbset.PresentData(self.dataIndex)):
			self.items[j].SetValue(str(val))
		
	def data_update (self, event):
		data = []
		sql= "delete from " + self.table_name + " where rowid = " + str(self.dataIndex)
			
		dial = wx.MessageDialog(None, "Are you sure to delete ?", "Confirmation",
									wx.YES_NO | wx.NO_DEFAULT | wx.ICON_EXCLAMATION)
		
		response = dial.ShowModal()
		
		if response == wx.ID_YES:
			self.dbset.query(sql)
			self.dbset.query("vacuum")

		
class db_assist (object):
	def __init__(self):
		self.cp = config.confValues()
		self.db_name = str(self.cp.db_name)
		self.table_name = str(self.cp.table_name)
		self.dbc = db.SqlMng(self.db_name)
		self.commit = self.dbc.commit()
		self.maxRow = self.dbc.row_num(self.table_name)
		self.colName = self.dbc.col_names(self.table_name)
		
	def query(self, sql):
		que = self.dbc.query(sql)
		return que
				
	def PresentData (self, dataNo):
		content = list(self.dbc.rowid( self.table_name, dataNo))
		if content is not None:
			content.pop()
		else:
			content = list(self.dbc.rowid(self.table_name, 1))
			content.pop()

		return content
		
	"""def DataNo (self, dataNo):
		content = list(self.dbc.rowid( table_name, dataNo))
		return content[-1]"""
		












