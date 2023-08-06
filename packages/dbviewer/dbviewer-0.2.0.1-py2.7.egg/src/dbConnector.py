# !/usr/bin/python
# -*- coding: utf-8 -*-


import sqlite3
import sys


reload(sys)
sys.setdefaultencoding("utf-8")


class SqlMng (object):
	def __init__ (self, db):
		self.con = None
		try:
			self.con = sqlite3.connect(db, isolation_level='IMMEDIATE')
			self.con.execute("pragma foreign_keys = off")
			self.con.execute("pragma encoding =  'UTF-8' ")
		except Exception, e:
			print e
			if self.con:		self.con.rollback()
		finally:
			if self.con:
				self.con.commit()
				self.cur = self.con.cursor()
		
	def commit(self):
		return self.con.commit()
		
	def query (self, arg) :			#  query 実行
		self.cur.execute(arg)
		self.con.commit()
		return self.cur
		
	def queries (self, sql, arg) :		#  multiple query 実行
		self.cur.execute(sql, arg)

		return self.cur
		
	def col_names (self, tn):		# Column Names(list)
		col_name = self.names(tn)
		nl = [e for inner_list in col_name for e in inner_list]
		
		return nl
		
	def names(self, tn):		#  colname 取得(２重リスト)
		curs = self.query("select*from " + tn)
		colname = list(map(lambda x: x[0], curs.description))
		tup_name = zip(*[iter(colname)]*len(colname))
		name = [list(v) for v in tup_name]
		return name
		
	def col_num(self, tablename):		#  col行数取得
		cname = self.names(tablename)
		for i in cname:
			colc = i
		col_count = len(colc)
		return col_count
		
	def row_num(self, tablename):		#  row全行数取得
		curs = self.query("select count(*) from " + tablename)
		for i in curs:
			num = i[0]
		return num
		
	def rowid (self, tablename, rowid):			#  row番号からdata取得
		curs = self.query(
					'select *, ROWID from ' + tablename + " where ROWID = " + str(rowid))
		for i in curs:
			num = i
			return num
		
	def __del__ (self):				#  デストラクタ
		self.con.close()















