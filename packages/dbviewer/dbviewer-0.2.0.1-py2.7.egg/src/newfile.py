#! /usr/bin/python
# -*- coding: utf-8 -*-


import wx
import wx.lib.mixins.listctrl as listmix
import mainloader
import dbConnector
import savedialog
import sys


reload(sys)
sys.setdefaultencoding("utf-8")


class EditableListCtrl (wx.ListCtrl, listmix.TextEditMixin, listmix.CheckListCtrlMixin):
	def __init__(self, parent, ID=wx.ID_ANY, pos=wx.DefaultPosition,
							size=wx.DefaultSize, style=0):
		wx.ListCtrl.__init__(self, parent, ID, pos, size, style)
		listmix.TextEditMixin.__init__(self)
		#listmix.CheckListCtrlMixin.__init__(self)
		
		
class EditFrame(wx.Frame):
	def __init__(self, parent, title):
		super(EditFrame, self).__init__(None, wx.ID_ANY, title=title, size=(400, 500))
		
		self.index = 0
		
		self.initUI()

		self.Centre()
		self.Show()
		
	def initUI(self):
		panel = wx.Panel(self, wx.ID_ANY)
		
		font = wx.SystemSettings_GetFont(wx.SYS_SYSTEM_FONT)
		font.SetPointSize(9)
		
		self.index=0
		
		# -------------- Sizers -----------------------------------------------------------------
		topsizer = wx.BoxSizer(wx.VERTICAL)
		hsizer13 = wx.BoxSizer(wx.HORIZONTAL)
		hsizer12 = wx.BoxSizer(wx.HORIZONTAL)
		hsizer11 = wx.BoxSizer(wx.HORIZONTAL)
		hsizer10 = wx.BoxSizer(wx.HORIZONTAL)
		hsizer1 = wx.BoxSizer(wx.HORIZONTAL)
		hsizer2 = wx.BoxSizer(wx.HORIZONTAL)
		hsizer3 = wx.BoxSizer(wx.HORIZONTAL)
		
		# --------------------Widgets -----------------------------------------------------------
		dbtext= wx.StaticText(panel, wx.ID_ANY, label="Database : ")
		dbtext.SetFont(font)
		
		global dbname, tblname
		dbname = wx.TextCtrl (panel, wx.ID_ANY, size=(120, 30))
		self.extens= wx.StaticText(panel, wx.ID_ANY, label=".db")
		
		# ---------------------- Add Widget -------------------------------------------------
		hsizer13.Add(dbtext)
		hsizer13.Add(dbname)
		hsizer13.AddSpacer(10)
		hsizer13.Add(self.extens)
		
		# ----------------------- Widget 2 ----------------------------------------------------
		tabletext= wx.StaticText(panel, wx.ID_ANY, label="table name")
		#tabletext.SetFont(font)
		
		tblname = wx.TextCtrl (panel, wx.ID_ANY, size=(100, 30))
		
		self.coltext= wx.StaticText(panel, wx.ID_ANY, label="column name")
		self.coltext.SetFont(font)
		self.vtype= wx.StaticText(panel, wx.ID_ANY, label="data Type")
		self.vtype.SetFont(font)
		
		# -------------------------- Add Widget 2 ---------------------------------------------
		hsizer12.Add(tabletext)
		hsizer11.Add(tblname)
		
		hsizer10.Add(self.coltext)
		hsizer10.AddSpacer((50, 0))
		hsizer10.Add(self.vtype)
		
		# ---------------------------- Widget 3 --------------------------------------------------
		self.text = wx.TextCtrl (panel, wx.ID_ANY, size=(100, 30))
		
		datatypes = ('integer primary key', 'integer', 'text', 'none', 'real', 'numeric')
		self.combo = wx.ComboBox(panel, wx.ID_ANY, choices = datatypes, 
										size=(130, 30), style=wx.CB_DROPDOWN)
		self.combo.SetFont(font)
						 
		okbtn = wx.Button(panel, wx.ID_ANY, label='OK')
		self.Bind(wx.EVT_BUTTON, self.onOkay, okbtn)
		
		# -----------------------------Add Widget 3 ------------------------------------------------
		hsizer1.Add(self.text)
		hsizer1.AddStretchSpacer(1)
		hsizer1.Add(self.combo, 0, wx.LEFT, 10)
		hsizer1.AddSpacer(10)
		hsizer1.Add(okbtn, 10)
		
		# ----------------------------- Widget 4 ------------------------------------------
		self.box = EditableListCtrl(panel, size=(-1, 250),
											style=wx.LC_REPORT)
		self.box.InsertColumn (0, "Column No.")
		self.box.InsertColumn (1, "Col. Name")
		self.box.InsertColumn (2, "Data Type")
		
		self.box.SetFont(font)
		
		hsizer2.Add(self.box, 1, wx.EXPAND)
		
		crtbtn = wx.Button(panel, wx.ID_ANY, size=(70, 30), label='Create')
		canlbtn = wx.Button(panel, wx.ID_ANY, size=(70, 30), label='Cancel')
		
		self.Bind(wx.EVT_BUTTON, self.onCreateTbl, crtbtn)
		self.Bind(wx.EVT_BUTTON, self.onCancel, canlbtn)
		
		hsizer3.Add(crtbtn, wx.BOTTOM)
		hsizer3.Add(canlbtn, wx.LEFT | wx.BOTTOM, 10)
		
		topsizer.Add((-1, 10))
		topsizer.Add(hsizer13, 0, wx.LEFT, 10)
		topsizer.Add(hsizer12, 0, wx.LEFT, 10)
		topsizer.Add(hsizer11, 0, wx.LEFT, 10)
		topsizer.Add(hsizer10, 0, wx.LEFT | wx.TOP, 10)
		topsizer.Add(hsizer1, 0, wx.LEFT, 10)
		topsizer.Add(hsizer2, 0, wx.ALL| wx.EXPAND, 10)
		topsizer.Add((-1, 10))
		topsizer.Add(hsizer3, 0,  wx.ALIGN_RIGHT | wx.RIGHT, 10 )
		
		panel.SetSizer(topsizer)
			
	def onOkay(self, event):
		cols = self.index + 1
		line = 'Column %s' % cols
		name = self.text.GetValue()
		datatype = self.combo.GetValue()
		self.box.InsertStringItem(self.index, line)
		self.box.SetStringItem(self.index, 1, name)
		self.box.SetStringItem(self.index, 2, datatype)
		if self.index % 2 :
			self.box.SetItemBackgroundColour(self.index, "white")
		else:
			self.box.SetItemBackgroundColour(self.index, "light blue")
		self.index += 1
		
	def onCreateTbl (self, event):
		count = self.box.GetItemCount()
		table = tblname.GetValue()
		dbn = dbname.GetValue() + ".db"
		dbc = dbConnector.SqlMng(dbn)
		dialog = wx.MessageDialog(None, 'Are you sure to create table?',
							'Info', wx.ID_OK)
		if dialog.ShowModal() == wx.ID_OK:
			
			lst = []
			for i in range( count ):
				colname= self.box.GetItem(itemId=i, col=1)
				columns = colname.GetText()
				itemval = self.box.GetItem(itemId=i, col=2)
				dataType = itemval.GetText()
				lst.append(str(columns) + ' ' + str(dataType))
				 
			sql = ("create table " + table + "(" + ', '.join(['%s']*len(lst)) + ")") % tuple(lst)
			savedialog.saveDialog(dbn, sql)
			self.Close()
		
	def onCancel (self, event):
		self.Close()
		

		
		
		
		
		
		
		
		
