'''
Created on Jun 13, 2012

@package  ebf
@author   mpaegert
@version  \$Revision: 1.5 $
@date     \$Date: 2013/10/24 23:22:23 $

read and traverse sqlite database

$Log: dbreader.py,v $
Revision 1.5  2013/10/24 23:22:23  paegerm
Adding attach

Revision 1.4  2012/10/15 16:59:24  paegerm
Adding timeout of 10 s as default

Revision 1.3  2012/08/23 16:38:53  paegerm
allow to switch off the row factory

Revision 1.2  2012/08/16 22:21:53  paegerm
allow select parameter to be None for fetchmany and fetchone

Revision 1.1  2012/07/06 20:38:49  paegerm
Initial Revision

'''

import sqlite3


class DbReader(object):
    '''
    A reader for the sqlite databases
    '''
    
    def __init__(self, filename, factory = True, tout = 10.0):
        if (filename is None) or (len(filename) == 0):
            raise NameError(filename)
        
        self.fname  = filename
        self.dbconn = sqlite3.connect(filename, timeout = tout)
        if (factory is True):
            self.dbconn.row_factory = sqlite3.Row
        self.dbcurs = self.dbconn.cursor()
        self.records = None
        self.coldesc = None
        
        
        
    def attach(self, filename, asname = 'db2'):
        cmd = "attach '" + filename + "' as '" + asname + "';"
        self.dbcurs.execute(cmd)
        
        
        
    def fetchall(self, select, args = None):
        if args is None:
            args = []
        self.dbcurs.execute(select, args)
        self.records = self.dbcurs.fetchall()
        return (self.records)
    
    
    def fetchmany(self, select = None, args = None, n = 1000):
        if args is None:
            args = []
        if (select is not None):
            self.dbcurs.execute(select, args)
            self.dbcurs.arraysize = n
        self.records = self.dbcurs.fetchmany()
        return self.records
    
    
    def fetchone(self, select = None, args = None):
        if args is None:
            args = []
        if (select is not None):
            self.dbcurs.execute(select, args)
        self.records = self.dbcurs.fetchone()
        return self.records
    
    
    
    def traverse(self, select, args = None, n = 1000):
        self.fetchmany(select, args, n)
        while (len(self.records) != 0):
            for star in self.records:
                yield star
            self.records = self.dbcurs.fetchmany()
            


    def getlc(self, staruid, tname = 'stars', order = None):
        if (staruid is None) or (staruid <= 0):
            raise ValueError
        cmd = 'select * from ' + tname + ' where staruid = ?'
        if (order != None):
            cmd += ' order by ' + order + ';'
        else:
            cmd += ';'
        self.records = self.fetchall(cmd, [staruid])
        return self.records
        
    
    def getnptypes(self, table = 'stars'):
        curs = self.dbconn.execute('PRAGMA table_info(' + table + ')')
        self.coldesc = curs.fetchall()
        nptypes = []
        for mytuple in self.coldesc:
            if mytuple[2] == 'INTEGER':
                app = (str(mytuple[1]), 'i4')
            elif mytuple[2] == 'REAL':
                app = (str(mytuple[1]), 'f4')
            elif mytuple[2] == 'TEXT':
                app = (str(mytuple[1]), 'a20')
            elif len(mytuple[2]) <= 0:      # assume float for computed values
                app = (str(mytuple[1]), 'f4')
            else:
                msg = 'Unknown type ' + mytuple[2] + ' for ' + mytuple[1]
                raise NameError(msg)
            nptypes.append(app)
        
        return nptypes


        
    def close(self):
        self.dbcurs.close()
        self.dbconn.close()
        

        
if __name__ == '__main__':
    pass
