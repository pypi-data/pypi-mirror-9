#!/usr/bin/env python
'''
@author: Riccardo Ravaioli
'''

import time

class bcolors:
    HEADER = '\033[95m' #violet
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m' #yellow
    FAIL = '\033[91m'   #red
    ENDC = '\033[0m'

    def disable(self):
        self.HEADER = ''
        self.OKBLUE = ''
        self.OKGREEN = ''
        self.WARNING = ''
        self.FAIL = ''
        self.ENDC = ''
        
        
def drange(start, stop, step):
    r = start
    l = []
    while r < stop:
        l.append(r)
        r += step
    return l
    
def get_current_time():
    current_time = time.localtime() 
    current_time =  "%s-%s-%s-%s.%s.%s" % (current_time.tm_year,
                                            current_time.tm_mon, 
                                            current_time.tm_mday, 
                                            current_time.tm_hour, 
                                            current_time.tm_min, 
                                            current_time.tm_sec)
    return current_time
