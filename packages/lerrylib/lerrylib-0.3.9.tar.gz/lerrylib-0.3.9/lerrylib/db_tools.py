#!/usr/bin/python
# -*- coding: utf-8 -*-
import logging
import _mysql
import MySQLdb
from torndb import Row
from cache import mc as _mc
from lerry_signal import SIGNAL
from torndb import Connection as _Connection
from msgpack import packb, unpackb


class Model(object):

	def KEY(self, id):
		return '%s:%s' % (self._table, id)

	def __init__(self, name, db):
		self._table = name
		self.db = db
		self.mc = db.mc

	def get(self, id):
		id = int(id)
		MC_KEY = self.KEY(id)
		item = self.mc.get(MC_KEY)
		if item is None:
			item = self.db.get('SELECT * FROM %s WHERE id = %%s' % self._table, id)
			self.mc.set(MC_KEY, packb(item))
		else:
			item = Row(unpackb(item))
		return item

	def update(self, id, **kwargs):
		MC_KEY = self.KEY(id)
		self.db.execute('UPDATE %s SET %%s WHERE id=%%s' % self._table, kwargs, id)

	def get_list(self, id_list):
		_di = self.mc.get_multi(map(self.KEY, id_list))

		result = []
		for id in id_list:
			value = _di.get(id)
			if value is None:
				value = self.get(id)
			result.append(value)
		return map(Row, result)

	def rm(self, id):
		self.db.execute('DELETE FROM %s WHERE id = %%s' % self._table, id)
		self.mc.delete('%s:%s' % (self._table, id))

def _getattr(self, name):
	if self.__dict__.get(name):
		return self.__dict__[name]
	#self.query('SELECT 1 FROM %s' % name)
	return Model(name, self)

def _execute(self, cursor, query, parameters):
    try:
        result = cursor.execute(query, parameters)
        sql_expresstion = cursor._last_executed
        SIGNAL.db_query.send(sql_expresstion)
        sql_parse(sql_expresstion)
        print result
        return result
    except MySQLdb.OperationalError:
        logging.error("Error connecting to MySQL on %s", self.host)
        self.close()
        raise

def Connection(host, db, user, pw, mc=None):
	'''
		wrapper of torndb
	'''
	if mc is None:
		mc = _mc
	_Connection.__getattr__ = _getattr
	_Connection.mc = mc
	_Connection._execute = _execute
	return _Connection(host, db, user, pw)
		

def sql_parse(sql):
	"""Parse sql expressions so the program can know when to flush memcached
	A normal sql expressions may contains several parts
	>> SELECT * FROM Data WHERE id = 123
	>> UPDATE Data SET uid = 1 cid = 2 WHERE id = 3
	>> DELETE FROM Data where id = 2

	Keyword SELECT UPDATE delete
	Condition   WHERE
	Parameters, id = 1, name = 'lerry'
	Only when you do a "UPDTAE" or "DELETE" opration you need to flush the memcached
	and you can set a memcached record when do a "INSERT" or "UPDATE" opration
	I don't want to do a very complex system, just support simple expressions is ok, 
	I won't try to support expressions contains "JOIN" opration
	The default format of a memcached key is like "User:123", the table name and id will be splited
	by a semicolon

	"""
	_splited = sql.split()
	print _splited
	keyword = _splited[0].upper()
	if keyword in ['DELETE', 'UPDATE']:
		table_name = _splited[2] if keyword == 'DELETE' else _splited[1]
		print '%s' % table_name





def test():
	db = Connection('127.0.0.1', 'cheshang_dev', 'root', '')
	#print db.Data.get(1)
	db.Data.rm(7)
		
if __name__ == '__main__':
	pass
	test()

