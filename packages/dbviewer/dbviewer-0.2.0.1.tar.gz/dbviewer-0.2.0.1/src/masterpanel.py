# !/usr/bin/python
# -*- coding: utf-8 -*-


import wx
import os, sys
import addin_value
import search_eng
import update
import delete_data
import newfile
import tablemaker
import remodelcol
import mainloader
import dbConnector
import config


reload(sys)
sys.setdefaultencoding("utf-8")


class MasterPanel (wx.Panel):
	def __init__(self, parent, showChild=False):
		wx.Panel.__init__(self, parent)
		
		self.vsizer = wx.BoxSizer(wx.VERTICAL)
		self.hsizer = wx.BoxSizer(wx.HORIZONTAL)
		
		if showChild:
		
			self.filename = wx.Button (self, wx.ID_ANY, " SQLite file ")
			self.Bind(wx.EVT_BUTTON, self.fname_handler, self.filename)
			array = [] 
			self.cb = wx.ComboBox(self, wx.ID_ANY, "SQLite Table", size=(130, 30),
									choices=array, style=wx.CB_SIMPLE)
		
			insbtn = wx.Button(self, wx.ID_ANY, "Insert Date" )
			updbtn = wx.Button(self, wx.ID_ANY, "Update Data" )
			delebtn = wx.Button(self, wx.ID_ANY, "Delete Data" )
			altbtn = wx.Button(self, wx.ID_ANY, "Alter Data" )
		
			se= search_eng.MainPanel(self)
		
			imgfile = './icons/exit2.png'
			img1 = wx.Image(imgfile, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
		
			exitbtn = wx.BitmapButton(self, wx.ID_ANY, bitmap = img1,
									size=(img1.GetWidth(), img1.GetHeight()))
			self.Bind(wx.EVT_BUTTON, self.onQuit, exitbtn)
		
			self.Bind(wx.EVT_BUTTON, self.insertData, insbtn)
			self.Bind(wx.EVT_BUTTON, self.updateData, updbtn)
			self.Bind(wx.EVT_BUTTON, self.deleteData, delebtn)
			self.Bind(wx.EVT_BUTTON, self.onAlt, altbtn)
			self.Bind(wx.EVT_COMBOBOX, self.onCombo, self.cb)
		
			self.hsizer.Add(self.filename, 0, wx.GROW | wx.ALL, 5)
			self.hsizer.Add(self.cb, 0, wx.GROW | wx.ALL, 5)
			self.hsizer.Add(insbtn, 0, wx.GROW | wx.ALL, 5)
			self.hsizer.Add(updbtn, 0, wx.GROW | wx.ALL, 5)
			self.hsizer.Add(delebtn, 0, wx.GROW | wx.ALL, 5)
			self.hsizer.Add(altbtn, 0, wx.GROW | wx.ALL, 5)
			self.hsizer.Add(se, 0, wx.EXPAND | wx.ALIGN_RIGHT | wx.ALL, 5)
			self.hsizer.Add(exitbtn, 0, wx.ALL, 5)
		
			self.vsizer.Add(self.hsizer)
		
			self.SetSizerAndFit(self.vsizer)
		
			self.Centre()
	
	def tblname_getter (self, dbname):
		self.dbname= dbname
		dbset = dbConnector.SqlMng(self.dbname)
		sql= "select * from sqlite_master where type='table' "
		qu = dbset.query(sql)
		tables = map(lambda t: t[1], qu.fetchall())
		arr = []
		for i in tables:
			arr.append(i)
		self.arays(arr)
	
	def arays (self, item):
		choices = item
		self.cb.Clear()
		
		for it in choices:
			self.cb.Append(it)
				
	def onCombo (self, event):
		tbl_name = self.cb.GetValue()
		conf = config.Configure()
		config.Configure.tname = tbl_name
		
	def newFile(self, event):
		newfile.EditFrame(self.GetParent(), title="New File")
		
	def newTable (self, event):
		tablemaker.EditPanel(self.GetParent(), title='New Table')
		
	def insertData(self, event):
		addin_value.MainFrame(self.GetParent(), 'Insert Data')
		
	def updateData (self, event):
		update.Viewer(self.GetParent(), "Update Data")
	
	def deleteData (self, event):
		#delete_data.Viewer(None, 'DELETE DATA')
		delete_data.Viewer(self.GetParent(), 'Delete Data')
		
		
	def onAlt (self, event):
		remodelcol.remodels(self.GetParent(), 'Alter Data')
		
	def onQuit(self, event):
		self.Close()
		
	def fname_handler(self, event): 			# database file income
		ff = mainloader.Fileloader()
		name = ff.onOpenFile()
		self.filename.SetLabel(name)
		self.tblname_getter(name)
		if event.Id == self.filename.Id:
			config.Configure.fname = name

















