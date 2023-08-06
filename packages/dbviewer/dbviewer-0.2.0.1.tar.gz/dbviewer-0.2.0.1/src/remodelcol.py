# !/usr/bin/python
# -*- coding: utf-8 -*-


import wx
import dbConnector
import mainloader
import config
import masterpanel


class remodels(wx.Frame):
	def __init__(self, parent, title):
		wx.Frame.__init__(self, parent, wx.ID_ANY, title,
											style=wx.FRAME_FLOAT_ON_PARENT|wx.DEFAULT_FRAME_STYLE)
		
		self.cp = config.confValues()
		self.db_name = str(self.cp.db_name)
		self.tbl_name = str(self.cp.table_name)
		
		# ----------------------- Panel & Sizers -----------------------------------
		panel = masterpanel.MasterPanel (self)
		
		tsizerh = wx.BoxSizer(wx.HORIZONTAL)
		bsizerh = wx.BoxSizer(wx.HORIZONTAL)
		bsizerh2 = wx.BoxSizer(wx.HORIZONTAL)
		bsizerv = wx.BoxSizer(wx.VERTICAL)
		
		sb_c = wx.StaticBox(panel, wx.ID_ANY, 'column addition')
		boxsizer_c = wx.StaticBoxSizer(sb_c, wx.HORIZONTAL)
		bsizer_c = wx.BoxSizer(wx.HORIZONTAL)
		
		sb_n = wx.StaticBox(panel, wx.ID_ANY, 'rename table')
		boxsizer_n = wx.StaticBoxSizer(sb_n, wx.HORIZONTAL)
		bsizer_n = wx.BoxSizer(wx.HORIZONTAL)
		
		vsizer = wx.BoxSizer(wx.VERTICAL)
		
		# ----------------------- Widgets ------------------------------------------
		self.title = wx.StaticText(panel, wx.ID_ANY, label="Target DataBase")
		self.file_tit = wx.StaticText(panel, wx.ID_ANY, label="File Name : ")
		self.table_tit = wx.StaticText(panel, wx.ID_ANY, label="Table Name : ")
		self.fln = wx.StaticText(panel, wx.ID_ANY, label=self.db_name)
		self.tbln = wx.StaticText(panel, wx.ID_ANY, label = self.tbl_name)
		
		subj_c = wx.StaticText(panel, wx.ID_ANY, label='New Column')
		self.newcol = wx.TextCtrl(panel, wx.ID_ANY)
		datatypes = ('integer', 'text', 'none', 'real', 'numeric')
		self.cb_type = wx.ComboBox(panel, wx.ID_ANY, choices = datatypes, 
										size=(100, 30), style=wx.CB_DROPDOWN)
		
		okbtn = wx.Button(panel, wx.ID_ANY, label = 'Ok')
		self.Bind(wx.EVT_BUTTON, self.onOkay, okbtn)
		
		subj_n = wx.StaticText(panel, wx.ID_ANY, label='New Table Name')
		self.newnm = wx.TextCtrl(panel, wx.ID_ANY)
		rebtn = wx.Button(panel, wx.ID_ANY, label = 'Rename')
		self.Bind(wx.EVT_BUTTON, self.onRename, rebtn)
		
		# ----------------------- Add widgets --------------------------------------
		tsizerh.Add(self.title, 0, wx.TOP | wx.LEFT, 5)
		bsizerh.Add(self.file_tit, 0, wx.LEFT, 5)
		bsizerh.Add(self.fln, 0, wx.LEFT, 5)
		bsizerh2.Add(self.table_tit, 0, wx.LEFT, 5)
		bsizerh2.Add(self.tbln, 0, wx.LEFT, 5)
		bsizerv.Add(tsizerh, 0, wx.ALL, 5)
		bsizerv.Add(bsizerh, 0, wx.ALL, 5)
		bsizerv.Add(bsizerh2, 0, wx.ALL, 5)
		
		boxsizer_c.Add(subj_c, 0, wx.ALL, 5)
		boxsizer_c.Add(self.newcol, 0, wx.ALL, 5)
		boxsizer_c.Add(self.cb_type, 0, wx.ALL, 5)
		boxsizer_c.Add(okbtn, 0, wx.ALL, 5)
		bsizer_c.Add(boxsizer_c)
		
		boxsizer_n.Add(subj_n, 0, wx.ALL, 5)
		boxsizer_n.Add(self.newnm, 0, wx.ALL, 5)
		boxsizer_n.Add(rebtn, 0, wx.ALL, 5)
		bsizer_n.Add(boxsizer_n)
		
		vsizer.Add(bsizerv, 1, wx.ALL, 5)
		vsizer.Add(bsizer_c, 1, wx.ALL, 5)
		vsizer.Add(bsizer_n, 1, wx.ALL, 5)
		panel.SetSizer(vsizer)
		
		self.SetSize((450, 350))
		
		self.Show()
	
		
	def onOkay (self, event):
		
		dbc = dbConnector.SqlMng(self.db_name)
		sql = "alter table "+ self.tbl_name + " add column " \
								 + self.newcol.GetValue() + " " + self.cb_type.GetValue()
		dial = wx.MessageDialog(None, "Are you sure to add a column?", 'Question',
														wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
		if dial.ShowModal() == wx.ID_YES:
			dbc.query(sql)
			dbc.commit()
			self.Close()
		
	def onRename (self, event):
		dbc = dbConnector.SqlMng(self.db_name)
		sql = "alter table " + self.tbl_name + " rename to '" + self.newnm.GetValue() + "'"
		dial = wx.MessageDialog(None, "Are you sure to add a column?", 'Question',
														wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
		if dial.ShowModal() == wx.ID_YES:
			dbc.query(sql)
			dbc.commit()
			self.Close()
		
if __name__ == "__main__" :
	app = wx.App()
	frm = remodels(None, wx.ID_ANY)
	app.MainLoop()














