#! /usr/bin/python
# -*- coding: utf-8 -*-


import wx
import controlpanel
import remodelcol


class Configure():
	def __init__(self):
		self._x = None
		
	@property
	def x(self):
		return self._x
		
	@x.setter
	def x(self, x):
		self.__x = x
	

class confValues(wx.Frame):
	def __init__(self):
		wx.Frame.__init__(self, None, wx.ID_ANY)
		self.conf = Configure()
		self.db_name = self.conf.fname
		self.table_name = self.conf.tname



	




