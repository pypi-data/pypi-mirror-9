# !/usr/bin/python
# -*- coding: utf-8 -*-

import os
import wx

ID_OPEN = wx.NewId()
wildcard = ["sqlite file (*.db)|*.db|" \
						"Python source (*.py; *.pyc)|*.py;*.pyc|" \
						"All files (*. *) | *.*",
						" jpeg file (*.jpg)|*.jpg|" \
						" All files (*. *) | *.*"]

class Fileloader (wx.Frame):
	def __init__ (self) : 
		wx.Frame.__init__(self, parent=None, size=(100, 100))
		self.currentDirectory = os.getcwd()
		
	def onOpenFile(self):
		dig = wx.FileDialog(
					self, message = "Choose a file",
					defaultDir = self.currentDirectory,
					defaultFile = "",
					wildcard = wildcard[0],
					style = wx.OPEN | wx.MULTIPLE | wx.CHANGE_DIR
					)
					
		if dig.ShowModal () == wx.ID_OK:
			paths = dig.GetPaths()
			
			for path in paths:
				fname = os.path.basename(path)
			
		dig.Destroy()
		self.Close()
		return fname
		
	def onPictloader (self):
		dig = wx.FileDialog(
					self, message = "Choose a file",
					defaultDir = self.currentDirectory,
					defaultFile = "",
					wildcard = wildcard[1],
					style = wx.OPEN | wx.MULTIPLE | wx.CHANGE_DIR
					)
					
		if dig.ShowModal () == wx.ID_OK:
			paths = dig.GetPaths()
			
			for path in paths:
				fname = os.path.basename(path)
			
		dig.Destroy()
		self.Close()
		return fname



					
					
					
					
					
					
					
