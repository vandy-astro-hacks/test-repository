'''
Created on May 31, 2015

@module  : pytest.tappend
@author  : map
@version : \$Revision$
@Date    : \$Date$

$Log$
initial revision
'''

import pyutils as pyu



def doAppend(size = 10000):
    result = []
    for i in range(size):
        message = "some unique object %d" % (i,)
        result.append(message)
    return result



def doAllocate(size = 10000):
    result = size * [None]
    for i in range(size):
        message = "some unique object %d" % (i,)
        result[i] = message
    return result



if __name__ == '__main__':
    watch = pyu.Stopwatch()
    
    for i in xrange(1, 7):
        size = int(pow(10, i))
        
        watch.start()
        l1 = doAppend(size)
        apptime = watch.stop()
        
        watch.start()
        l2 = doAllocate(size)
        alltime = watch.stop()
    
        print 'size = %8d:   append / allocate = %3.2f' % \
        (size, apptime / alltime)
    
    print 'done'
