#!/usr/bin/env python
'''
Convert and import text files into sqlite3 databases

This module converts and imports text files into sqlite3 databases.
The first text file used for database creation needs to have a column and 
format description as a commented line beginning with #. Example:

@verbatim
# last   middle    first    age     income
#  sn      s         s       i        f
Doe      null      John      44     1523.22
@endverbatim

By default the column names are searched in the first, the format in the
second line. Column names may include whitespace if a separator is used, but
the whitespace will be stripped. Generally names should follow the SQL 
convention

Allowed formats and sqlite3 Datatype:
s, a - TEXT
i, l - INTEGER
f, d - REAL

If a format character is followed by an 'n', the field must not contain 
null values. If a format character is followed by a 'u', the column value
must be unique and not contain null values

The database file is created with a given table name if it does not exist.
If it does exist, column names are taken from the table in the database.
If no table name is given, the first part of the database file is used as 
table name. 

If you create a new database and import several text files at once, only 
the first must have a column and format line.

Any new table will forcibly have UID as first column, an auto-incremented 
integer primary key

@package  txt2sqlite
@author   mpaegert
@version  \$Revision: 1.6 $
@date     \$Date: 2015/03/13 17:46:29 $
 
@verbatim
Usage: txt2sqlite.py [options] sqlitefile textfile(s)

Options:
  -h, --help         show this help message and exit
  -c CLINE           line number with column names (default 1)
  -d DEBUG           debug setting (default: 1)
  -f FLINE           line number with format description (default 2)
  -n SNULL           string used for NULL values (default: null)
  -s SEP             separator [default = any whitespace]
  -t TNAME           table name
  --block=BSIZE      import n lines at a time (n > 0. default 100000)
  --commit=NCOMMIT   commit every n lines (n > 0, default 100000)
  --fix              fixed formats
  --ifnames=IFNAMES  file containing a list of filenames to import
  --iso=ISOLATION    isolation level (default = None)
  --ignore=IGNAME    file containing a list of space separated column numbers
                     to ignore
  --lfname=LFNAME    log file
  --or=ORCLAUSE      abort, fail, ignore, replace, rollback
  --skip=SKIP        number of lines to skip initially
@endverbatim

$Log: txt2sqlite.py,v $
Revision 1.6  2015/03/13 17:46:29  paegerm
correcting comment for version 1.5

Revision 1.5  2015/03/13 17:41:14  paegerm
Try catch format errors, print exception text, print number of errors

Revision 1.4  2012/12/03 17:45:46  paegerm
Initialize connection object with None.

Revision 1.3  2012/04/02 23:02:48  map
rstrip all values, ignore empty lines in ifnames, add fixed format and 
skip option, adding "a" as allowed format character for strings

Revision 1.2  2012/02/06 20:48:48  map
Correcting treatment of null values

'''

import sqlite3 as sql
import time

from optparse import OptionParser
from stopwatch import *
from logfile import *



options = None
dbfile  = None
flist   = []
ignores = []
lf      = None



def parsecols(line):
    '''
    Parse line with column definitions, return list with column names.
    
    @param line: string with column names
    @return: list of column names, whitespaces are stripped
    '''
    cols = []
    tmp = line.split(options.sep)
    for i in xrange(len(tmp)):
        if i in ignores:
            continue
        cols.append(tmp[i].strip())
    cols.insert(0, 'UID')     # unique numerical ID
    return cols



def parsefmts(line):
    '''
    Parse line with format description.
    
    @param line: string with formats
    @return: list of data types, list of NULL value information
    '''
    tmp   = line.split(options.sep)
    fmts   = []
    for i in xrange(len(tmp)):
        if i in ignores:
            continue
        fmts.append(tmp[i].strip().lower())

    types  = []
    nnull  = []
    flens  = None
    if options.fixed == False:
        for i in xrange(len(fmts)):
            if (fmts[i].startswith('i')) or fmts[i].startswith('l'):
                types.append('INTEGER')
            elif (fmts[i].startswith('f')) or fmts[i].startswith('d'):
                types.append('REAL')
            else:
                types.append('TEXT')
            if ('u' in fmts[i]) :
                nnull.append('UNIQUE NOT NULL')
            elif ('n' in fmts[i]):
                nnull.append('NOT NULL')
            else:
                nnull.append('')
    else:
        flens = []
        total = 0
        for fmt in fmts:
            fchar = fmt[0].lower()
            length = int(fmt[1:])
            if fchar == 'i' or fchar == 'l':
                types.append('INTEGER')
                flens.append((total, total + length))
                nnull.append('')
            elif fchar == 'f' or fchar == 'd':
                types.append('REAL')
                flens.append((total, total + length))
                nnull.append('')
            elif fchar == 's' or fchar == 'a':
                types.append('TEXT')
                flens.append((total, total + length))
                nnull.append('')
            total += length
            
    types.insert(0, 'INTEGER')     # for UID
    nnull.insert(0, 'NOT NULL')
        
    return (types, nnull, flens)



def make_create_statement(table, cols, fmts, nnull):
    '''
    Generate the CREATE statement
    
    @param table: name of the table
    @param cols:  list of column names
    @param fmts:  data types
    @param nnull: information about NULL values  
    @return:      SQL CREATE TABLE statement as string
    '''
    cmd = 'CREATE TABLE ' + table + ' ('
    cmd += 'UID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE'
    for i in xrange(1, len(cols)):
        cmd += ', '
        cmd += cols[i] + ' ' + fmts[i] + ' ' + nnull[i]
    
    cmd += ');'
    return cmd




def fileimport(fname):
    '''
    Import text file
    
    @param fname: string with filename
    @return: number of data lines, number of lines that created an error
    '''
    conn = None
    if (options.isolation is None):
        conn = sql.connect(dbfile)
    else:
        conn = sql.connect(dbfile, isolation_level=options.isolation)
    curs = conn.cursor()
    curs.execute('PRAGMA synchronous=OFF;')

    create = False
    cols   = None
    fmts   = None
    nnull  = None
    
    # check if database and table exist
    try:
        cmd  = "select count() from sqlite_master where type='table'"
        cmd += " and name='"
        cmd += options.tname
        cmd += "'"
        res  = curs.execute(cmd).fetchone()
        if res[0] <= 0 :
            create = True        # table needs to be created
        else:
            # get column names and types from existing table
            cmd = 'PRAGMA TABLE_INFO(' + options.tname + ');'
            res = curs.execute(cmd).fetchall()
            cols = []
            fmts = []
            for i in xrange(len(res)):
                cols.append(res[i][1])
                fmts.append(res[i][2])
    except sql.Error, e:
        print "Database error: ", e.args[0]
        return

    tlines = 0
    dlines = 0
    errors = 0
    insert = None
    flens  = None
    ilist = []
    blockwatch = Stopwatch()     # bsize chunk timing information
    blockwatch.start()
    
    # main loop over input file
    nrskip = 0
    for line in open(fname):
        tlines += 1
        if nrskip < options.skip:
            nrskip += 1
            continue
        line = line[:-1]
        if len(line) == 0:
            continue
        if (line.find('#') == 0):      # pound sign in first column
            if (create == True) and (tlines == options.cline):
                cols = parsecols(line[1:])
            if (((create == True) and (tlines == options.fline)) or
                ((create == False) and (tlines == options.fline) and 
                 (options.fixed == True))):
                (fmts, nnull, flens) = parsefmts(line[1:])
            if (create == True) and (cols != None) and (fmts != None):
                if (options.debug > 0):
                    print "Creating table ", options.tname
                cmd = make_create_statement(options.tname, cols, fmts, nnull)
                if (options.debug > 0):
                    print cmd
                curs.execute(cmd)
                create = False
            continue
        
        # check if we have column names and format information
        if (cols is None):
            print 'Could not find line with column names: use -c option'
            exit(1)
        if (fmts is None):
            print 'Could not fine line with format description: use -f option'
            exit(2)
            
        # make a text template for the isert statement
        if (insert is None):
            insert = 'INSERT ' + options.orclause + ' INTO ' + options.tname \
                     + ' (' + cols[1]
            qmarks = '?'
            for i in xrange(2, len(cols)):
                insert += ', ' + cols[i]
                qmarks += ', ?'
            insert += ') VALUES (' + qmarks + ');'
            
        # We have a data line. Replace NULL strings and split into columns
        dlines += 1
        vals = []
        if options.fixed == False:
            tmp = line.split(options.sep)
            for i in xrange(len(tmp)):
                if i in ignores:
                    continue
                vals.append(tmp[i])                
        else:
            for (start, end) in flens:
                if (len(line[start:end].strip()) > 0):
                    vals.append(line[start:end])
                else:
                    vals.append(options.snull)
        for i in xrange(len(vals)):
            if (vals[i] == options.snull) or (len(vals[i].strip()) == 0):
                vals[i] = None
            elif fmts[i+1] == 'INTEGER':       # offset due to UID
                vals[i] = int(vals[i].strip())
            elif fmts[i+1] == 'REAL':
                try:
                    vals[i] = float(vals[i].strip())
                except ValueError, e:
                    print 'ValueError for real: ', i, vals[i].strip()
            else:
                vals[i] = vals[i].rstrip()
        ilist.append(vals)
        if ((options.bsize > 0) and (tlines % options.bsize == 0)):
            try:
                curs.executemany(insert, ilist)
            except sql.IntegrityError, e:
                errors += 1
                if (options.bsize == 1):
                    print line
            blockwatch.stop()
            if options.debug > 1:
                print tlines, ' processed, ', blockwatch.elapsed, ' s'
            blockwatch.start()
            ilist = []
        if ((options.ncommit > 0) and (tlines % options.ncommit == 0)):
            conn.commit()
         
    if len(ilist) > 0:
        try:
            curs.executemany(insert, ilist)            
            conn.commit()
        except sql.IntegrityError, e:
            errors += 1
            print e
    else:
        conn.commit()      # we might have pending inserts
    curs.close()
    conn.close()
    return (dlines, errors)



if __name__ == '__main__':
    flist = []
    dbfile = None
    usage = '%prog [options] sqlitefile textfile(s)'
    parser = OptionParser(usage=usage)
    parser.add_option('-c', dest='cline', type='int', default=1,
                      help='line number with column names (default 1)')
    parser.add_option('-d', dest='debug', type='int', default=1,
                      help='debug setting (default: 1)')
    parser.add_option('-f', dest='fline', type='int', default=2,
                      help='line number with format description (default 2)')
    parser.add_option('-n', dest='snull', type='string', default='null',
                      help='string used for NULL values (default: null)')
    parser.add_option('-s', dest='sep', 
                      help='separator [default = any whitespace]')
    parser.add_option('-t', dest='tname', help='table name')
    parser.add_option('--block', dest='bsize', type='int', default=100000,
                      help='import n lines at a time (n > 0. default 100000)')
    parser.add_option('--commit', dest='ncommit', type='int', default=100000,
                      help='commit every n lines (n > 0, default 100000)')
    parser.add_option('--fix', dest='fixed', action='store_true', default=False,
                      help='fixed formats')
    parser.add_option('--ifnames', dest='ifnames', 
                      help='file containing a list of filenames to import')
    parser.add_option('--iso', dest='isolation', default=None, 
                      help='isolation level (default = None)')
    parser.add_option('--ignore', dest='igname', default='',
                      help='file containing a list of space separated ' + 
                           'column numbers to ignore') 
    parser.add_option('--lfname', dest='lfname', default=None, 
                      help='log file')   
    parser.add_option('--or', dest='orclause', type='string', default='',
                      help='abort, fail, ignore, replace, rollback')
    parser.add_option('--skip', dest='skip', type='int', default=0,
                      help='number of lines to skip initially')
    (options, args) = parser.parse_args()
    
    # check options
    if (options.ifnames is None) and (len(args) < 2):
        print 'Too few arguments: --ifnames or textfile missing'
        parser.print_help()
        exit(1)
    if (options.ifnames is not None):
        if (len(args) < 1):
            print "sqlitefile missing"
            parser.print_help()
            exit(1)
        for line in open(options.ifnames):
            tmp = line[:-1].rstrip()
            if len(tmp) > 0:
                flist.append(line[:-1])
                
    if (len(options.igname) > 0):
        for line in open(options.igname):
            if line.startswith('#'):
                continue
            line = line[:-1]
            if len(line) > 0:
                splitted = line.split()
                for col in splitted:
                    ignores.append(int(col) - 1)

    if len(args) >= 2:
        for i in xrange(1, len(args)):
            flist.append(args[i])
    dbfile = args[0]
    if (options.tname is None):
        tmp = dbfile.split('/')
        tmp = tmp[len(tmp) - 1]
        tmp = tmp.split('.')
        options.tname = tmp[0]
        
    if (options.orclause != ''):
        options.orclause = ' OR ' + options.orclause
        
    if (options.isolation is not None):
        options.isolation = options.isolation.upper()
        
    if options.bsize <= 0:
        print 'block size must be >= 1'
        exit(1)
    if options.ncommit <= 0:
        print 'commit option must be >= 1'
        exit(1)

    lf = Logfile(options.lfname, True, True)

    # we are good to go
    watch = Stopwatch()
    watch.start()
    fwatch = Stopwatch()
    fcount = 0
    
    for fname in flist:       # loop over input files
        fwatch.start()
        if (options.debug > 0):
            print "processing ", fname
        (dlines, errors) = fileimport(fname)
        if (options.debug > 0):
            if errors > 0:
                print errors, ' errors encountered, check result!!!'
            else:
                print dlines, ' lines found, ', dlines - errors, 'lines imported ' \
                      'in ', fwatch.stop(), ' seconds'
        fcount += 1
        
    if options.debug > 0:
        print fcount, ' files in ', watch.stop(), ' seconds = ', \
              watch.elapsed / fcount, ' seconds / file'
        print 'Done'
    
##
#@mainpage txt2sqlite and fits2sqlite
#@copydetails txt2sqlite
    