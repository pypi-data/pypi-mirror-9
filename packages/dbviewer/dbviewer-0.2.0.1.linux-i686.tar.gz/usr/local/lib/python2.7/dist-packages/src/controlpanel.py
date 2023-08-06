# !/usr/bin/python
# -*- coding: utf-8 -*-


import wx
import os, sys
import masterpanel


reload(sys)
sys.setdefaultencoding("utf-8")


class MainApp (wx.App):
	def __init__(self):
		wx.App.__init__(self)
		frm = MainFrame(None, wx.ID_ANY, 'DBViewer')
		frm.SetPosition((0, 0))
		frm.SetSize((1000, 50))
		self.SetTopWindow(frm)
		frm.Show()
		self.MainLoop()
		
		
class MainFrame(wx.Frame):
	def __init__(self, parent, id, title):
		wx.Frame.__init__(self, parent, id, title)
		
		# ----------------------- Panel ---------------------------------------------------
		self.panel = masterpanel.MasterPanel(self, showChild=True) 
		
		# ------------------ IDs ----------------------------------------------------------------
		ID_NEWFILE = wx.NewId()
		ID_NEWTABLE = wx.NewId()
		ID_INSERT = wx.NewId()
		ID_UPDATE = wx.NewId()
		ID_DELETE = wx.NewId()
		
		# -------------------- menubar ---------------------------------------------------------
		menu_file = wx.Menu()
		menu_new = wx.Menu()
		menu_new.Append(ID_NEWFILE,  'File')
		menu_new.Append(ID_NEWTABLE,  'Table')
		menu_file.AppendSubMenu(menu_new, 'New')
		quit = menu_file.Append(wx.ID_NEW, '&Quit')
		
		menu_edit = wx.Menu()
		menu_data = wx.Menu()
		menu_data.Append(ID_INSERT, 'Insert Data')
		menu_data.Append(ID_UPDATE, 'Update Data')
		menu_data.Append(ID_DELETE, 'Delete Data')
		menu_edit.AppendSubMenu(menu_data, 'Data')
		
		self.Bind(wx.EVT_MENU, self.panel.newFile, id=ID_NEWFILE)
		self.Bind(wx.EVT_MENU, self.panel.newTable, id=ID_NEWTABLE)
		self.Bind(wx.EVT_MENU, self.panel.onQuit, quit)
		self.Bind(wx.EVT_MENU, self.panel.insertData, id = ID_INSERT)
		self.Bind(wx.EVT_MENU, self.panel.updateData, id = ID_UPDATE)
		self.Bind(wx.EVT_MENU, self.panel.deleteData, id=ID_DELETE)
		
		menubar = wx.MenuBar()
		menubar.Append (menu_file, '&File' )
		menubar.Append (menu_edit, '&Edit')
		
		self.SetMenuBar ( menubar )
		
		self.Show()


if __name__ == '__main__':
	MainApp()




