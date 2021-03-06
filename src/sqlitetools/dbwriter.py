'''
Created on Jun 18, 2012

@package  ebf
@author   mpaegert
@version  \$Revision: 1.8 $
@date     \$Date: 2013/08/07 15:22:06 $

create and write to sqlite databases

$Log: dbwriter.py,v $
Revision 1.8  2013/08/07 15:22:06  paegerm
add fetchall and orclause, addinf generic create_index function

Revision 1.7  2013/07/19 16:54:26  parvizm
double commit

Revision 1.6  2013/07/19 16:50:46  parvizm
include functions creat_dict_idx and create_lc_idx for dynamic db index

Revision 1.5  2013/06/06 18:19:57  paegerm
add isolation level

Revision 1.4  2013/04/22 21:27:18  paegerm
cols may be None if table exists, adding column description to class

Revision 1.3  2012/10/15 16:57:19  paegerm
adding default timeout of 10 s

Revision 1.2  2012/08/16 22:21:53  paegerm
adding getlastuid, extending parameters for init (lf and noauto)

Revision 1.1  2012/07/06 20:38:49  paegerm
Initial Revision

'''

import sqlite3

from dbfunctions import *


class DbWriter(object):
    '''
    A writer for sqlite databases
    '''
    def __init__(self, filename, cols = None, table = 'stars', types = None, 
                 nulls = None, lf = None, noauto = False, tout = 10.0,
                 isolevel = '', orclause = ''):
        
        if (filename is None) or (len(filename) == 0):
            raise NameError(filename)
        
        if (cols is not None) and (types is not None) and (nulls is not None):
            create_db(filename, cols, types, nulls, table, lf, noauto)
        
        self.table = table
        self.fname = filename
        self.coldesc = None
        if (isolevel is None):
            self.dbconn = sqlite3.connect(filename, timeout = tout)
        else:
            self.dbconn = sqlite3.connect(filename, timeout = tout,
                                          isolation_level = isolevel)
        if (cols is None):
            # get columns from an existing database
            curs = self.dbconn.execute('PRAGMA table_info(' + table + ')')
            self.coldesc = curs.fetchall()
            cols = [tmptuple[1] for tmptuple in self.coldesc]
            
        self.dbconn.row_factory = sqlite3.Row
        self.dbcurs = self.dbconn.cursor()
        self.dbcurs.execute('PRAGMA synchronous=OFF;')
        
        self.inscmd = make_insert_statement(cols, table, orclause)
        self.newins = make_insert_statement(cols, table, orclause, False)
    
    
    def deletebystaruid(self, staruid):
        if (staruid is None) or (staruid <= 0):
            raise ValueError
        cmd = 'delete from ' + self.table + ' where staruid = ?;'
        self.dbcurs.execute(cmd, [staruid])
        self.dbconn.commit()


    def getlastuid(self):
        cmd = 'select max(uid) from ' + self.table + ';'
        res = self.dbcurs.execute(cmd)
        return res
        
        
    def insert(self, values, commit = False):
        if (self.inscmd is None):
            raise ValueError
        self.dbcurs.executemany(self.inscmd, values)
        if (commit is True):
            self.dbconn.commit()
        
        
    def update(self, cmd, values, commit = False):
        if (cmd is None):
            raise ValueError
        self.dbcurs.executemany(cmd, values)
        if (commit is True):
            self.dbconn.commit()
        
        
    def fetchall(self, select, args = None):
        if args is None:
            args = []
        self.dbcurs.execute(select, args)
        self.records = self.dbcurs.fetchall()
        return (self.records)

            
    def create_dict_idx(self):
        cmd = 'create index staruididx on ' + self.table + ' (uid asc);'
        res = self.dbcurs.execute(cmd)
        return res


    def create_lc_idx(self):
        cmd = 'create index staruididx on ' + self.table + ' (staruid asc);'
        res = self.dbcurs.execute(cmd)
        return res
    
    
    def create_index(self, idxname, fielddesc):
        cmd = 'create index ' + idxname + ' on ' + self.table + \
              ' (' + fielddesc + ');'
        res = self.dbcurs.execute(cmd)
        return res


    def commit(self):
        self.dbconn.commit()
                
        
    def close(self):
        self.dbcurs.close()
        self.dbconn.close()
        
        

if __name__ == '__main__':
    pass
