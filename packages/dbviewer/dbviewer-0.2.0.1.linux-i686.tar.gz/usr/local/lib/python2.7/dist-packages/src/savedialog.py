# /usr/bin/python
# -*- coding: utf-8 -*-


import os
import wx
import dbConnector
import sqlite3


class saveDialog(wx.Frame):
	def __init__(self, filename, que):
		wx.Frame.__init__(self, parent=None)
		self.sql = que
		self.filename = filename
		self.wildcard = "sqlite data (*. db) | *.db|" \
								" all files (*.*) | *.* "
		self.saves()
		
	def saves (self):
		dia = wx.FileDialog(self,
					message = "Save file as ..",
					defaultDir = "",
					defaultFile = self.filename,
					wildcard = self.wildcard,
					style = wx.FD_SAVE | wx.CHANGE_DIR
					)
					
		if dia.ShowModal() == wx.ID_OK:
			path = dia.GetPath()
			db = dbConnector.SqlMng(path)
			db.query(self.sql)	
			
		dia.Destroy()








