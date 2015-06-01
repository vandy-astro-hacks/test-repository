'''
A very simple stopwatch class

@package  txt2sqlite
@author   mpaegert
@version  \$Revision: 1.2 $
@date     \$Date: 2013/08/13 20:39:03 $

$Log: stopwatch.py,v $
Revision 1.2  2013/08/13 20:39:03  paegerm
initial revision


'''

import time

class Stopwatch(object):
    '''
    A very simple stopwatch class
    
    Attributes
    
    elapsed - time elapsed
    laptime - time the last lap began
    '''

    def __init__(self):
        '''
        Constructor: setting start and stop time
        '''
        self.__class__ = Stopwatch
        self._stop  = None
        self.elapsed = 0.0
        self.laptime = 0.0
        self._start = time.time()
        
    def cont(self):
        '''
        restarting the watch, keeping elapsed time 
        '''
        self._stop  = None
        self._start = time.time()

    def start(self):
        '''
        starting the watch, nulling elapsed time
        '''
        self.elapsed = 0.0
        self.cont()
        
    def stop(self):
        '''
        stopping the watch, computing time elapsed
        @return: elapsed time
        '''
        self._stop  = time.time()
        self.elapsed = self.elapsed + (self._stop - self._start)
        return self.elapsed
        
    def elapsed(self):
        '''
        returning elapsed time since start
        @return elapsed time scince start
        '''
        self.elapsed = self.elapsed + (time.time() - self._start)
        return self.elapsed
    
    def lap(self):
        '''
        compute time for one lap
        @return: time between laps
        '''
        if self.laptime == 0.0:
            self.laptime = self._start
        current = time.time()
        retval  = current - self.laptime
        self.laptime = current
        return retval
    
    def stopintermediate(self):
        '''
        Stopping and returning intermediate time
        @return: elapsed time since last cont() or start()
        '''
        self.stop()
        return self._stop - self._start
        
    def __str__(self):
        '''
        @return: formatted string of elapsed time in seconds
        '''
        return 'elapsed time = ' + str(self.elapsed) + ' sec'


if __name__ == '__main__':
    watch = Stopwatch()
    print 'started with creation, waiting some time'
    time.sleep(1.5)
    watch.stop()
    print "time = ", watch.elapsed
    print watch
    
    print ""
    print "restarting"
    watch.cont()
    time.sleep(1)
    print 'intermediate time = ', watch.stopintermediate()
    
    print ''
    print 'laptime 1 =', watch.lap()
    time.sleep(2.0)
    print 'laptime 2 =', watch.lap()
    print 'elapsed   =', watch.stop()
    
    print watch
    print 'done'
    