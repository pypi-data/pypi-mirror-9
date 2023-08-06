#!/usr/bin/env python
'''
@author: Riccardo Ravaioli
'''

import logging
import sys
import time
import os
logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p',
                    level=logging.WARNING)
import icmptool

def get_current_time():
    current_time = time.localtime() 
    current_time =  "%s-%s-%s-%s.%s.%s" % (current_time.tm_year,
                                            current_time.tm_mon, 
                                            current_time.tm_mday, 
                                            current_time.tm_hour, 
                                            current_time.tm_min, 
                                            current_time.tm_sec)
    return current_time


if __name__ == '__main__':
    # add arguments from both modules
    parser = icmptool.pass_prober_args()
    # args will include probing args and analysis args
    args = parser.parse_args()
    probing_parameters = pass_processed_prober_args(args) #icmp_prober.process_parameters(args)
    #results folder
    current_time = get_current_time()
    traces_folder = '/tmp/icmp_%s' % current_time
    probing_parameters['traces_folder'] = traces_folder
    
    icmptool.icmptool(**probing_parameters)
    
#    # 1.bis fingerpint routers
#    routers = None
#    if probing_parameters['fingerprint']:
#        _, routers = icmp_prober.fingerprint_tool(**probing_parameters)
##        print routers
#    traces_paths = icmp_prober.probing_tool(**probing_parameters)
#    # 2. process pcap traces
#    trace_info_list = icmp_analysis.process_pcap_traces(traces_paths)
#    # 3. analyze results
#    icmp_analysis.analyze_traces(trace_info_list, fp_dict=routers)
    
    sys.exit()

