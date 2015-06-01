'''
@package : pytest.hipcount
@author  : map
@version : \$Revision$
@Date    : \$Date$

$Log$
Initial revision
'''


import pyutils as pyu
import sqlitetools as sqlt



if __name__ == '__main__':
    hipreader = sqlt.DbReader('../../data/hip.sqlite')
    
    res = hipreader.fetchall('select count(*) ' + 
                             'from stars ' + 
                             'where vt >= 8.0 and vt < 8.5')
    print res
    
    hipreader.close()
    
    print 'done'
