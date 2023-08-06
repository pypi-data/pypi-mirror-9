#! /usr/bin/python
# -*- coding: utf-8 -*-


import wx
import dbConnector
import tablegrid
import config
import auxiliaries
import sys

reload(sys)
sys.setdefaultencoding("utf-8")


class MainPanel(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent, id=wx.ID_ANY)
		
		self.txt = wx.SearchCtrl(self, wx.ID_ANY, size=(-1, 30), style=wx.TE_PROCESS_ENTER)
		self.btn = wx.Button(self, wx.ID_ANY, size = (-1, 30), label="Search")
		
		self.Bind(wx.EVT_BUTTON, self.OnScreen, self.btn)
		
		self.layout = wx.BoxSizer(wx.HORIZONTAL)
		self.layout.Add(self.txt)
		self.layout.AddSpacer(10)
		self.layout.Add(self.btn)
		self.SetSizer(self.layout)
		self.layout.Fit(self)
		
	def OnScreen (self, event):
		keyword = self.txt.GetValue()
		dbh = Db_Head()
		dbh.db_header(keyword)
		tg  = tablegrid.GridFrame(self)
		tg.Show()

		
class Db_Head (wx.Frame):
	def __init__(self):
		wx.Frame.__init__(self, None, wx.ID_ANY)
		
		self.cp = config.confValues()
		self.db_name = str(self.cp.db_name)
		self.table_name =str(self.cp.table_name)
		self.dbs = dbConnector.SqlMng(self.db_name)
		
	def db_header(self, word):
		keyword = word
		colname = self.dbs.col_names(self.table_name)
		nomi = []
		for col in colname:
			sql = u"select*from " + self.table_name + u" where " \
													+ col + u" like '%" + keyword + u"%' "
			que = self.dbs.query(sql)
			tup = que.fetchall()
			ls = [list(r) for r in tup]
			nomi.append(ls)
		listin = []
		for lst in nomi:
			if lst != []:
				listin.extend(lst)
			else:
				lst = ["NO DATA"] * len(colname)
				listin.append(lst)
		listed = auxiliaries.sequence(listin)
		cdt = tablegrid.CustomDataTable(listed)























