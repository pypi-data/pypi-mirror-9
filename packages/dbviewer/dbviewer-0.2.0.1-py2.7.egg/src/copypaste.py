# !/usr/bin/python
# -*- coding: utf-8 -*-

import wx

#class Copypaste(wx.Frame):

class Copypaste(wx.MenuBar):
	def __init__(self, text):
		wx.MenuBar.__init__(self)
		
		self.text = text
		
		#menubar = wx.MenuBar()
		
		edit = wx.Menu()
		cut = wx.MenuItem(edit, 106, '&Cut\tCtrl+X', 'Cut the Selection')
		edit.AppendItem(cut)
		
		copy = wx.MenuItem(edit, 107, '&Copy\tCtrl+C', 'Copy the Selection')
		edit.AppendItem(copy)
		
		paste = wx.MenuItem(edit, 108, '&Paste\tCtrl+V', 'Paste text from clipboard' )
		edit.AppendItem(paste)
		
		delete = wx.MenuItem(edit, 109, '&Delete', 'Delete the selected text')
		edit.AppendItem(delete)
		
		edit.Append(110, 'select &All\tCtrl+A', 'Select the entre text')
		
		self.Append(edit, '&Edit')
		"""self.SetMenuBar(menubar)
		self.SetMenuBar()
		
		self.Bind(wx.EVT_MENU, self.onCut, id=106)
		self.Bind(wx.EVT_MENU, self.onCopy, id=107)
		self.Bind(wx.EVT_MENU, self.onPaste, id=108)
		self.Bind(wx.EVT_MENU, self.onDelete, id=109)
		self.Bind(wx.EVT_MENU, self.onSelectAll, id=110)
		"""
		
	def onCut(self, event):
		self.text = self.FindFocus()
		if self.text is not None:
			self.text.Cut()
		
	def onCopy(self, event):
		self.text = self.FindFocus()
		if self.text is not None:
			self.text.Copy()
		
	def onPaste (self, event):
		self.text = self.FindFocus()
		if self.text is not None:
			self.text.Paste()
		
	def onDelete(self, event):
		self.text = self.FindFocus()
		if self.text is not None:
			frm, to = self.text.GetSelection()
			self.text.Remove(frm, to)
		
	def onSelectAll(self, event):
		self.text.SelectAll()
		
"""
if __name__ == "__main__":
	app = wx.App()
	Copypaste()
	app.MainLoop()
"""















