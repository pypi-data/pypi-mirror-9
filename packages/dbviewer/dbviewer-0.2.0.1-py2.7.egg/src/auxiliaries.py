#! /usr/bin/python
# -*- coding: utf-8 -*-


def insert_sql ( value, tablename ):
	lang = '?, '  * len(value)
	qs = "("  + lang[:-2] + ")"
	sql = 'insert into ' + tablename + ' values ' + qs
	return sql

def addQuest(value):
	element = [x+ '= ? ' for x in value]
	ans  = ', '.join(element)
	return ans


def flatten (nested_list):
	nl = [e for inner_list in nested_list for e in inner_list]	
	return nl


def sequence (seq):
	b = []
	for w in seq:
		if w not in b:
			b.append(w)
	return b

















