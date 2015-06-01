'''
Created on Jul 1, 2012

@package  ebf
@author   mpaegert
@version  \$Revision: 1.1 $
@date     \$Date: 2012/07/06 20:38:49 $

$Log: dbfunctions.py,v $
Revision 1.1  2012/07/06 20:38:49  paegerm
Initial revision

'''


import sqlite3



def make_create_statement(cols, fmts, nulls, tname = 'stars'):
    cmd = 'CREATE TABLE IF NOT EXISTS ' + tname + ' ('
    cmd += 'UID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE'
    for i in xrange(len(cols)):
        cmd += ', '
        cmd += cols[i] + ' ' + fmts[i] + ' ' + nulls[i]
    cmd += ');'
    return cmd



def make_create_statement_noauto(cols, fmts, nulls, tname = 'stars'):
    # UID is not autoincrement for this table
    cmd = 'CREATE TABLE IF NOT EXISTS ' + tname + ' ('
    cmd += 'UID INTEGER PRIMARY KEY NOT NULL UNIQUE'
    for i in xrange(1, len(cols)):    # skip UID, dealt with in line above
        cmd += ', '
        cmd += cols[i] + ' ' + fmts[i] + ' ' + nulls[i]
    cmd += ');'
    return cmd



def create_db(fname, cols, fmts, nulls,
              tname = 'stars', lf = None, noauto = False):
    # check if database and table exist
    try:
        conn = sqlite3.connect(fname)
        curs = conn.cursor()
        cmd  = "select count() from sqlite_master where type='table'"
        cmd += " and name='"
        cmd += tname
        cmd += "'"
        res  = curs.execute(cmd).fetchone()
        if res[0] <= 0:
            # create, if stars does not exist, values does not exist either
            if noauto is True:
                cmd = make_create_statement_noauto(cols, fmts, nulls, tname)
            else:
                cmd = make_create_statement(cols, fmts, nulls, tname)
            if (lf is not None):
                lf.write(cmd)
            curs.execute(cmd)
            conn.commit()
            curs.close()
            conn.close()
    except sqlite3.Error, e:
        print "Database error: ", e.args[0]
        return



def make_insert_statement(cols, tname = 'stars', orclause = '', 
                          withuid = True):
    if (cols is None):
        return None
    insstar  = 'insert ' + orclause + ' into ' + tname + ' ('
    qmarks = '?'
    start  = 0
    if withuid is False:
        start = 1
    for i in xrange(start, len(cols)):
        if i - start > 0:
            qmarks += ', ?'
            insstar  += ', '
        insstar  += cols[i]
    insstar += ') VALUES (' + qmarks + ');'
    return insstar



def rowtolist(row, startwith = 0):
    if (row is None) or (len(row) == 0):
        return None
    rowlist = []
    for i in xrange(startwith, len(row)):
        rowlist.append(row[i])
    return rowlist



if __name__ == '__main__':
    pass
