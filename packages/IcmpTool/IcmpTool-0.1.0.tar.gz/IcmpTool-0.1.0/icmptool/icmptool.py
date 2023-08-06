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

import icmp_analysis
import icmp_prober
import utils



def icmp_tool(duration=10.0, runs=1, ttls=[1], n_of_rates=1, rate_min=100, rate_max=500,
                protocols=['icmp'], dest='8.8.8.8', payload_sizes=[0],
                traces_folder='icmp_results', interface='eth0',fingerprint=False):
    routers = None
    if fingerprint:
        _, routers = icmp_prober.fingerprint_tool(ttls=ttls, dest=dest, interface=interface)
        
    traces_paths = icmp_prober.probing_tool(duration=duration, runs=runs, ttls=ttls,
                                            n_of_rates=n_of_rates, rate_min=rate_min,
                                            rate_max=rate_max, protocols=protocols,
                                            dest=dest, payload_sizes=payload_sizes,
                                            traces_folder=traces_folder, interface=interface)
    trace_info_list = icmp_analysis.process_pcap_traces(traces_paths)
    routers_by_ttl = icmp_analysis.analyze_traces(trace_info_list, fp_dict=routers)
    return routers_by_ttl 

if __name__ == '__main__':
    # add arguments from both modules
    parser = icmp_prober.create_prober_parser()
    # args will include probing args and analysis args
    args = parser.parse_args()
    # 1. probe
    probing_parameters = icmp_prober.process_parameters(args)
    #results folder
    current_time = utils.get_current_time()
    traces_folder = 'icmp_%s' % current_time
    probing_parameters['traces_folder'] = traces_folder
    # 1.bis fingerpint routers
    routers = None
    if probing_parameters['fingerprint']:
        _, routers = icmp_prober.fingerprint_tool(**probing_parameters)
#        print routers
    traces_paths = icmp_prober.probing_tool(**probing_parameters)
    # 2. process pcap traces
    trace_info_list = icmp_analysis.process_pcap_traces(traces_paths)
    # 3. analyze results
    icmp_analysis.analyze_traces(trace_info_list, fp_dict=routers)
    
    sys.exit()

