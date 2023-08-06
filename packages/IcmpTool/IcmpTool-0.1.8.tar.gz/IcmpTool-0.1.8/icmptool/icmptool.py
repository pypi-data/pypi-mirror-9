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


def pass_prober_args():
    return icmp_prober.create_prober_parser()


def pass_processed_prober_args(args):
    return icmp_prober.process_parameters(args)


def icmptool(duration=10.0, runs=1, ttls=[1], n_of_rates=1, min_rate=100, max_rate=500,
                protocols=['icmp'], dest='8.8.8.8', payload_sizes=[0],
                traces_folder='/tmp/icmp', interface='eth0',fingerprint=False, **extra):
    """Sends TTL-limited probes at constant rate(s) to the routers at the specified hops
    and by studying the timeseries of the received ICMP time-exceeded replies 
    it determines their responsiveness to these probes. On the specified range of probing
    rates, a router typically shows 3 phases in the following order:
     [fully-responsive]  [rate-limited] [irregular]
    Depending on the chosen probing rates and on the configuration of the router,
    not all phases might appear. The most common implementation
    of rate limitation is with an on-off pattern, of which we provide the parameters:
    burst size, period length and resulting answering rate. In some cases,
    rate limitation is implemented with a maximum constant answering rate, but no such
    pattern is observable. We call this a generically rate-limited router (rl).
    
    The tool will output to screen the details of each router found and return a dictionary
    where the router details at each tested hop.
    
    Args:
        duration: duration of one probing experiment, in seconds. Default is 10 s.
        runs: number of runs for each probing rate. Default is 1.
        min_rate: minimum probing rate, in packets per second (pps).
        max_rate: maximum probing rate, in packets per second (pps).
        protocols: list of types of probes to be used. Choice is between icmp, tcp and udp. Specify ping
                    to use directly the Ping utility. Default is [icmp].
        dest: IP destination of the probes. Default is 8.8.8.8.
        payload: list of probe payload sizes to be used. Default is [0], i.e. no extra payload.
        traces_folder: destination folder for the pcap files. Default is /tmp/icmp/
        interface: network interface to use for the experiments. Default is eth0.
        fingerprint: use technique described in http://orbi.ulg.ac.be/handle/2268/154575
                     in order to determine the brand of targeted routers.

    Returns:
        Nested dictionary in the form routers_by_hop[hop][router_IP] containing
        responsiveness details of the router encountered at each hop.    
    """
    routers = None
    if fingerprint:
        _, routers = icmp_prober.fingerprint_tool(ttls=ttls, dest=dest, interface=interface)
        
    traces_paths = icmp_prober.probing_tool(duration=duration, runs=runs, ttls=ttls,
                                            n_of_rates=n_of_rates, min_rate=min_rate,
                                            max_rate=max_rate, protocols=protocols,
                                            dest=dest, payload_sizes=payload_sizes,
                                            traces_folder=traces_folder, interface=interface)
    trace_info_list = icmp_analysis.process_pcap_traces(traces_paths)
    routers_by_ttl = icmp_analysis.analyze_traces(trace_info_list, fp_dict=routers)
    return routers_by_ttl 

