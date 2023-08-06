#!/usr/bin/env python
'''
@author: Riccardo Ravaioli
'''
import argparse
from copy import deepcopy
import itertools
import logging
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)
import math
import operator
import os
import pickle
import sys
import time
if '2.6' in sys.version.split(' ')[0]:
    import ordereddict
import numpy as np
from scapy.all import *
import scipy.stats
from scipy.stats import gaussian_kde

import prettytable

from utils import bcolors, get_current_time
import maclookup #my module

VARIANTS = [4] #just use gaps=4


class rtypes:
    unresponsive = 0
    always_responsive = 1
    pure_onoff = 2
#    onoff_off = 3
    busy_onoff = 4
    irregular_onoff = 5
    mostly_responsive = -1
    mostly_responsive_rl = -2
    noisy_responsive = -3
    poorly_responsive = -4
    
#def rtype_to_str(r):
##    "from code to description"
#    r_dict = { rtypes.unresponsive: 'unresponsive',
#               rtypes.always_responsive: 'always_responsive',
#               rtypes.pure_onoff: 'pure_onoff',
#               rtypes.onoff_off: 'onoff_off',
#               rtypes.busy_onoff: 'busy_onoff',
#               rtypes.irregular_onoff: 'irregular_onoff',
#               rtypes.mostly_responsive: 'mostly_responsive',
#               rtypes.mostly_responsive_rl: 'mostly_responsive_RL',
#               rtypes.noisy_responsive: 'noisy_responsive',
#               rtypes.poorly_responsive: 'poorly_responsive'
#             }
#    return r_dict[r]
    
def rtype_to_str(r):
#    "from code to description"
    r_dict = { rtypes.unresponsive: 'unresponsive',
               rtypes.always_responsive: 'fr',
               rtypes.pure_onoff: 'fr-onoff',
               rtypes.busy_onoff: 'fr-onoff-irr',
               rtypes.irregular_onoff: 'irregular_onoff',
               rtypes.mostly_responsive: 'fr-irr',
               rtypes.mostly_responsive_rl: 'fr-rl',
               rtypes.noisy_responsive: 'noisy_responsive',
               rtypes.poorly_responsive: 'poorly_responsive'
             }
    return r_dict[r]
def rtype_to_str_full(r):
#    "from code to description"
    r_dict = { rtypes.unresponsive: 'unresponsive',
               rtypes.always_responsive: 'fully responsive',
               rtypes.pure_onoff: 'fully responsive - onoff',
               rtypes.busy_onoff: 'fully responsive - onoff - irregular',
               rtypes.irregular_onoff: 'irregular_onoff',
               rtypes.mostly_responsive: 'fully responsive - irregular',
               rtypes.mostly_responsive_rl: 'fully responsive - generically rate-limited',
               rtypes.noisy_responsive: 'responsive but noisy (retry with wider range of probing rates)',
               rtypes.poorly_responsive: 'poorly responsive (retry with wider range of probing rates)'
             }
    return r_dict[r]


def remove_dupl_from_list_of_pairs(list_of_pairs):
        list_of_pairs.sort()
        list_of_pairs = list(k for k,_ in itertools.groupby(list_of_pairs))
        list_of_pairs = sorted(list_of_pairs, key=lambda el: (el[0], el[1]))
        return list_of_pairs



def insert_newline_every_n(data, n, tabs=0):
    def add_after_every_n(iterator, item_to_add='\n', after_every=3):
        for i, element in enumerate(iterator, 1):  # i counts from 1
            yield element
            if i % after_every == 0:
                yield item_to_add
    data = [str(d) + ', ' for d in data]
    to_add = '\n' + '\t' * tabs
    data_string = ''.join(add_after_every_n(data, item_to_add=to_add, after_every=n))
    data_string = data_string.strip().rstrip(', ')
    return data_string
    

def round_up_value_to_closest_in_a_list(value, list_of_values):
    min_index =  min(range(len(list_of_values)), key=lambda i: abs(list_of_values[i]-value))
    return list_of_values[min_index]


def match_probes_from_trace(trace, probes_protocol, replies_icmp_code):
    #get probes and replies
    probes = get_probes(trace, probes_protocol)
    replies = get_replies(trace, replies_icmp_code)

def get_probe_id_from_probe(probe, protocol, replies_ttl=1):
    if protocol.upper() == 'ICMP' or protocol.lower() == 'ping':
        probe_id = 65536 * probe[ICMP].id + probe[ICMP].seq
    elif protocol.upper() == 'TCP':
        probe_id = probe[TCP].seq
    elif protocol.upper() == 'UDP':
        # CAREFUL! You need to set TTL=1 in order to match checksums between probe and response
        # Generate a duplicate in order to not mess up with the timestamps (Scapy's fault!)
        p = deepcopy(probe)
        p[IP].ttl = 1
        del p[IP].chksum
        del p[UDP].chksum
        p = p.__class__(str(p))
        probe_id = p[UDP].chksum
    return probe_id

def get_probe_id_from_reply(reply, protocol):
    if protocol.upper() == 'ICMP':
        probe_id = 65536 * reply[ICMP].payload.payload.id + reply[ICMP].payload.payload.seq
    elif protocol.lower() == 'ping':
        probe_id = 65536 * reply[ICMP].id + reply[ICMP].seq
    elif protocol.upper() == 'TCP':
        probe_id = reply[ICMP].payload.payload.seq
    elif protocol.upper() == 'UDP':
        probe_id = reply[ICMP].payload.payload.chksum
    return probe_id


def match_probes(probes, replies, protocol, replies_protocol):
    DEBUG = False #set to True to see matched probes
    pairs = []
    # probe id is store in [ICMP].seq
    # [ICMP].type==8 if echo request
    # [ICMP.type==11 if time-exceeded
    if protocol == 'UDP': #
        replies_ttls = set()
    matched_probe_ids = []
    probes = sorted(probes, key=lambda packet: packet.time)
    logging.info("\t- Matching probes ")
    probes_ids = [get_probe_id_from_probe(pkt, protocol) for pkt in probes]
    replies_ids = [get_probe_id_from_reply(repl, protocol) for repl in replies]
    matched_replies_indices = []
    matched_probes_indices = []
    pairs_of_indices = []
    for i in xrange(len(probes_ids)):
        p_id = probes_ids[i]
        if p_id in replies_ids:
            matched_reply_index = replies_ids.index(p_id)
            pairs_of_indices.append((i, matched_reply_index))
            matched_replies_indices.append(matched_reply_index)
            if DEBUG:
                sys.stdout.write('.')
                sys.stdout.flush()
        else:
            pairs_of_indices.append((i, None))
            if DEBUG:
                sys.stdout.write('x')
                sys.stdout.flush()
        if DEBUG and i % 255 == 0 : #cut line: extremely long lines slow down the terminal
            sys.stdout.write('\n')
            sys.stdout.flush()
    pairs = []
    for pair in pairs_of_indices:
        if pair[1] is not None:
            pairs.append((probes[pair[0]], replies[pair[1]]))
        else:
            pairs.append((probes[pair[0]], None))
    if DEBUG:
        sys.stdout.write('\n')
        sys.stdout.flush()
    return pairs


def get_timeseries_from_trace(trace, probes_protocol, replies_icmp_code):
    pairs = match_probes_from_trace(trace, probes_protocol, replies_icmp_code)
    return get_timeseries(pairs)


def get_timeseries_from_probes_and_replies(probes, replies, protocol):
    pairs = match_probes(probes,replies, protocol)
    return get_timeseries(pairs)


def get_full_timeseries(pairs):
    timeseries = []
    for p in pairs:
        tmp = dict()
        if not p[1]:
            rtt = 'L' # loss
        else:
            rtt = p[1].time - p[0].time
        if rtt < 0:
            logging.warning("rtt is negative!!!")
        timeseries.append({'probe':{'timestamp':p[0].time},# 'size':len(p[0][IP])},
                            'reply': None if not p[1] else {'timestamp':p[1].time},
                                                        #'size':len(p[1][IP])},
                            'rtt':rtt
                            })
    return timeseries


def get_timeseries(pairs):
    timeseries = []
    for p in pairs:
        if not p[1]:
            rtt = 'L' # loss
        else:
            rtt = p[1].time - p[0].time
        timeseries.append(rtt)
    return timeseries


def get_probes(trace, protocol):
    protocol = protocol.upper()
    if protocol.upper() == 'ICMP' or protocol.lower() == 'ping':
        def is_a_probe(packet):
            return 'ICMP' in packet and packet[ICMP].type == 8
    elif protocol.upper() == 'TCP':
        def is_a_probe(packet):
            return 'TCP' in packet
    elif protocol.upper() == 'UDP':
        def is_a_probe(packet):
            return 'UDP' in packet
    else:
        def is_a_probe(packet):
            return False
    return [p for p in trace if is_a_probe(p)]


def get_replies(trace, icmp_type, code=None):
    # ICMP code 11: time-exceeded
    # ICMP code 0: echo reply
    if icmp_type == 11: # time exceeded
        def is_a_reply(packet):
            return 'ICMP' in packet and packet[ICMP].type == 11
    elif icmp_type == 0: #echo replies
        def is_a_reply(packet):
            return 'ICMP' in packet and packet[ICMP].type == 0
    elif icmp_type == 3 and code == 3: #port unreachable
        def is_a_reply(packet):
            return 'ICMP' in packet and packet[UDP].type == 8
    else:
        def is_a_reply(p):
            print p
            return False
    return [p for p in trace if is_a_reply(p)]


def get_size_series_from_trace(trace, probes_protocol='ICMP', replies_icmp_code=11):
    probes = get_probes(trace, probes_protocol)
    replies = get_replies(trace, replies_icmp_code) #time-exceeded if it's 11
    return get_size_series(probes=probes, replies=replies, probes_protocol=probes_protocol,
                            replies_icmp_code=replies_icmp_code)


def get_size_series(probes, replies, probes_protocol='ICMP', replies_icmp_code=11):
    probes_sizes = [len(p[IP]) for p in probes]
    replies_sizes = [len(p[IP]) for p in replies]
    return probes_sizes, replies_sizes


def get_probes_timestamps_from_trace(trace, probes_protocol='ICMP'):
    probes = get_probes(trace, probes_protocol)
    return get_timestamps(probes, probes_protocol=probes_protocol)


def get_timestamps(probes):
    probes_timestamps = sorted([p.time for p in probes])
    return probes_timestamps


def get_inter_packet_interval_series(timestamps):
    series = []
    for i in xrange(1,len(timestamps)):
        series.append(timestamps[i] - timestamps[i-1])
    return series

#########################################################
## aggregate results  ###################################
########################################################
def most_common(lst):
    return max(set(lst), key=lst.count)
    
    
def chunks(l, n):
    """ Yield successive n-sized chunks from l.
    """
    for i in xrange(0, len(l), n):
        yield l[i:i+n]

def divide_traces_into_chunks(traces, n, crit='host-and-ttl'):
    """ return list of n-sized sublists of traces and number of ids used to arrange data
    """
    if crit == 'host-and-ttl':
        ids = [[t['hostname'], t['ttl']] for t in traces]
        ids.sort()
        ids = list(k for k,_ in itertools.groupby(ids))
        ids = sorted(ids, key=lambda el: (el[0], el[1]))
        def get_iden(t):
            return [t['hostname'], t['ttl']]
    elif crit == 'host':
        ids = sorted(list(set([t['hostname'] for t in traces])))
        def get_iden(t):
            return t['hostname']
    ids_chunks = chunks(ids, n)
    res_traces = []
    for an_id_chunk in ids_chunks:
        res_traces.append([t for t in traces if get_iden(t) in an_id_chunk])
    return res_traces


def cov_test(vals):
    if all([el < 10 for el in vals]): #all small values
        k = 0.5
    else:
        k = 0.1
    return scipy.stats.variation(vals) < k


def get_path_id(t):
        return (t['hostname'], t['ttl'])
        
def get_router_id(t):
    return t['router']


def find_unresponsive_routers(analyzed_traces):
    #not sure why I'm not just saying that there is an unresponsive router whenever a whole experiment
    # hasn't experienced any responses. If a load balancer
    # directs packets to a responsive and to an unresponsive node, you won't discover
    # the unresponsive node.
    paths = list(set([(t['hostname'], t['ttl']) for t in analyzed_traces]))
    unresp = []
    for p in paths:
        traces_this_path = [t for t in analyzed_traces
                            if t['hostname'] == p[0] and t['ttl']==p[1]]
        routers_this_path = []
        for t in traces_this_path:
            if t['router'] is not None and t['router'] not in routers_this_path:
                routers_this_path.append(t['router'])
        if not routers_this_path:
            unresp.append(p)
            continue
    return unresp

def print_router_details(extra_info, r_type):
    #print for all
    if 'min_probing_rate' in extra_info and 'max_probing_rate' in extra_info:
        print "\t- [probing_rates] tested range: [%d, %d] pps" % (extra_info['min_probing_rate'],
                                                              extra_info['max_probing_rate'])
    if r_type == 0: #unresponsive
        pass
    elif r_type == 1: # fully responsive
        pass
    elif r_type == 2: #pure on-off
        print "\t- [probing_rates] min: %d pps; min_onoff: %d pps ; max_onoff=max: %d pps" % (
                        extra_info['min_probing_rate'],
                        extra_info['min_rate_low_cvs'],
                        extra_info['max_probing_rate'])
        print "\t- [on-off] burst size: %s packets, period length: %s s" % (extra_info['onoff_config_filtered']['bsize'],
                                                                extra_info['onoff_config_filtered']['ibt'])
        print "\t- [on-off] answering rate: %s pps" % (extra_info['onoff_rate'])
    elif r_type == 4: #busy_onoff, or rather fr-onoff-irr
        print "\t- [probing_rates] min: %s pps; min_onoff: %s pps ; max_onoff: %s pps ; max: %s pps" % (
                        extra_info['min_probing_rate'],
                        extra_info['min_rate_low_cvs'],
                        extra_info['max_rate_low_cvs'],
                        extra_info['max_probing_rate'])
        print "\t- [on-off] burst size: % packets, period length: %s s" % (extra_info['onoff_config_filtered']['bsize'],
                                                                extra_info['onoff_config_filtered']['ibt'])
        print "\t- [on-off] answering rate: %s pps" % (extra_info['onoff_rate'])
    
    elif r_type == -1: #mostly responsive, or rather fr-irr
        print "\t- [probing_rates] min: %s pps; max_fully_responsive: %s pps ; max: %s pps" % (
                        extra_info['min_probing_rate'],
                        extra_info['max_rate_always_responsive'],
                        extra_info['max_probing_rate'])
    elif r_type == -2: #mostly responsive rl, or rather fr-RL
        print "\t- [probing_rates] min: %d pps; max_fully_responsive: %d pps ; max: %d pps" % (
                        extra_info['min_probing_rate'],
                        extra_info['max_rate_always_responsive'],
                        extra_info['max_probing_rate'])
        print "\t- [generic_rate_limitation] answering rate: %s pps" % extra_info['limited_ans_rate']
    
    return


def classify_all_routers(analyzed_traces, v='_gaps_0', verbose=False, fp_dict=None):
#    unresponsive = 0
#    always_responsive = 1
#    pure_onoff = 2
#    onoff_off = 3
#    onoff_busy = 4
#    irregular_onoff = 5
#    mostly_responsive = -1
#    mostly_responsive_rl = -2
#    noisy_responsive = -3
#    poorly_responsive = -4
    all_types = [attr for attr in dir(rtypes)
                 if not callable(attr) and not attr.startswith("__")]
    routers_by_type = {rtypes.unresponsive: {},
                       rtypes.always_responsive: {},
                       rtypes.pure_onoff: {},
                       rtypes.busy_onoff: {},
                       rtypes.irregular_onoff: {},
                       rtypes.mostly_responsive: {},
                       rtypes.mostly_responsive_rl: {},
                       rtypes.noisy_responsive: {},
                       rtypes.poorly_responsive: {}
                       }
    # check every router
    ids = extract_all_routers(analyzed_traces)
    for an_id in ids:
        router_type, regular, irregular, extra_info = classify_router(an_id, analyzed_traces,
                                                                        v, verbose=verbose,
                                                                        fp_dict=fp_dict,
                                                                        study_rtt=False)
        if router_type not in routers_by_type:
            routers_by_type[router_type] = {}
        try:
            routers_by_type[router_type][an_id] = {'id': an_id, 'onoff_parameters': regular,
            'irregular': irregular, 'ttl':extra_info['ttl'], 'paths': extra_info['paths'],
            'extra_info': extra_info}
        except:
            code.interact(local=dict(globals(), **locals()))
    unresp = find_unresponsive_routers(analyzed_traces)
    for path in unresp:
        routers_by_type[rtypes.unresponsive][path] = {'ttl': path[1], 'extra_info':{}}
    num_all_routers = len(ids) + len(unresp)
    allttls = sorted(list(set([t['ttl'] for t in analyzed_traces])))
    # print parameters 
    routers_by_ttl = {}
    for ttl in allttls:
        routers_by_ttl[ttl] = {}
        for r_type in routers_by_type:
            for router in routers_by_type[r_type]:
                if routers_by_type[r_type][router]['ttl'] == ttl:
                    routers_by_ttl[ttl][router] = routers_by_type[r_type][router]
                    routers_by_ttl[ttl][router]['rtype'] = r_type
                    routers_by_ttl[ttl][router]['rtype_description'] = rtype_to_str_full(r_type)
                    routers_by_ttl[ttl][router]['rtype_str'] = rtype_to_str(r_type)
    #print details of each router
    for ttl in sorted(allttls):
        print "*** TTL = %s *** " % ttl
        for router in routers_by_ttl[ttl]:
            vendor_str = ''
            if routers_by_ttl[ttl][router]['extra_info']['vendor'] is not None:
                vendor_str = '(%s)' %  routers_by_ttl[ttl][router]['extra_info']['vendor']
            print "router %s " % str(router) + vendor_str
            print "\ttype: %s" % rtype_to_str_full(routers_by_ttl[ttl][router]['rtype'])
            print_router_details(routers_by_ttl[ttl][router]['extra_info'], routers_by_ttl[ttl][router]['rtype'])
                    
    return routers_by_ttl


def classify_router(router, analyzed_traces, v, verbose=False, fp_dict=None, allowed_noise=0.0, study_rtt=False):
    """
    Given a router's IP address and all analyzed traces, it analyzes all traces where
    this router appears and it classifies it as being:
        - unresponsive if no bursts appear and loss rate > 0.9 (90%) [ NEVER GONNA HAPPEN HERE]
        - always responsive if no bursts appear and loss rate < 0.1 (10%)
        - pure on-off if bursts appear, their IBT CoV and burst size CoV are < max_cv, 
            and all traces where the sending rate is >= minimum rate with low CoVs have
            low CoVs too
        - on-off-off if it's pure on-off only within a range of probing rates, and
            for all traces with higher probing rates the router becomes unresponsive
            (no bursts and loss rate > 0.9)
        - busy on-onoff: most often pure on-off, but with occasional irregular episodes
            Case 1) Similar parameters, with noise. For any probing rates, CoVs are high but average IBT
                    and burst size are within a 20% change from the parameters found
                    in the pure onoff experiments.
            Case 2) Occasional irregularity. For probing rates within the pure on-off
                    rate range, there are irregular episodes that amount to less than
                    20% of the number of pure on-off traces
        - irregularly on-off: low CoVs never appear, and we cannot draw any conclusions
            [there are low CoVs in a few traces, but the rest of
             the experiments are too noisy to draw any conclusions]
        - bursty routers with only high CoVs
    
    Returns:
        - classification number: 0 for unreponsive, 1 for always responsive,
                                2 for pure on-ff, 3 for on-off-off, 4 for busy on-off,
                                5 for irregularly on-off, -1 high CoVs bursty routers
        - on_off_details = parameters for pure on-off episodes, if any, otherwise empty list
        - irregular_details = values for irregular episodes, if any, otherwise empty list
    """
    def get_corresponding_expected_rate(some_traces, actual_rate):
        corr_expected_rates = [t['expected_rate'] for t in some_traces if t['actual_rate']==actual_rate]
        return max(corr_expected_rates)
    #set parameters
    max_cv = 0.05
    max_loss_rate = 0.05
    IBT_avg = 'IBT_avg' + v
    IBT_variation = 'IBT_variation' + v
    IBT_std = 'IBT_std' + v
    burst_size_variation = 'ans_burst_size_variation' + v
    ans_burst_size_avg = 'ans_burst_size_avg' + v
    ans_burst_size_std = 'ans_burst_size_std' + v
    
    traces_this_router = [t for t in analyzed_traces if t['router'] == router]
    router_ttl = traces_this_router[0]['ttl']
    traces_low_cvs = [t for t in traces_this_router
                        if t[IBT_variation] is not None
                        and t[burst_size_variation] is not None
                        and 0 <= t[IBT_variation] < max_cv
                        and 0 <= t[burst_size_variation] < max_cv]
   
    paths = list(set([get_path_id(t) for t in traces_this_router]))    
    extra_info = {'ttl': router_ttl, 'paths': paths}
    r_max = extra_info['max_probing_rate'] = max([t['actual_rate'] for t in traces_this_router])
    r_min = extra_info['min_probing_rate'] = min([t['actual_rate'] for t in traces_this_router])
    desired_probing_rate_r_max = get_corresponding_expected_rate(traces_this_router, r_max)
    logging.info("- [%s] (%s)" % (router, paths))
    table_to_print = prettytable.PrettyTable(['rates', 'IBT_cv', 'bsize_cv',
                                            'IBT_avg', 'bsize_avg', 'loss_rate',
                                            'answering_rate', 'tot_replies'])
    table2 = prettytable.PrettyTable(['low_cvs_rate_range', 'on-off in',
                                        'irregular in', 'traces above range'])
                                        
    # assign vendor
    extra_info['vendor'] = None
    def normalize_vendor(vv):
        if vv is None:
            return vv
        if 'cisco' in vv.lower():
            return 'cisco'
        elif 'juniper' in vv.lower():
            return 'juniper'
        else:
            return 'others'                         
    if router_ttl==1 and any([('router_vendor' in t and t['router_vendor'] is not None) 
                               for t in traces_this_router]):
        #assign vendor name based on MAC Address
        matching_trace = next(t for t in traces_this_router
                               if 'router_vendor' in t and t['router_vendor'] is not None)
        extra_info['vendor'] = normalize_vendor(matching_trace['router_vendor'])
    else:
        if fp_dict is not None and router in fp_dict:
            correct_vals = ['cisco', 'juniper_junos', 'linux_and_others', 'juniper_junosE'] 
            candidate_vendor = fp_dict[router]['router_brand']
            if candidate_vendor in correct_vals:
                extra_info['vendor'] = normalize_vendor(candidate_vendor)
    logging.info("\t- Vendor: %s" % extra_info['vendor'])

    def generic_interval_test(traces, r_start, r_end, condition):
        traces_in_range = [t for t in traces if r_start <= t['actual_rate'] <= r_end]
        traces_condition_true = [t for t in traces_in_range if condition(t)]
        if traces_in_range:
            noise_fraction = 1 - len(traces_condition_true) * 1.0 / len(traces_in_range)
        else:
            noise_fraction = 0
        return noise_fraction
        
    def fully_responsive_interval_test(traces, r, allowed_loss_rate=0.05, allowed_noise=0.2):
        #check that for all traces in [r_min, r] loss rate is below allowed_loss_rate
        noise_fraction = generic_interval_test(traces, 0, r,
                                     lambda x: x['loss_rate'] <= allowed_loss_rate)
        return noise_fraction <= allowed_noise, noise_fraction
        
    # # # # # # # # # # # # # # # # # # #
    # low CoVs NEVER appear
    # # # # # # # # # # # # # # # # # # #
    if not traces_low_cvs:
        table3 = prettytable.PrettyTable(['max_rate_always_responsive', 'always_responsive',
                                        'other at < max_rate', 'traces > max_rate'])
        extra_info['loss_rates'] = [t['loss_rate'] for t in traces_this_router]
        always_responsive_traces = [t for t in traces_this_router 
                                    if t['loss_rate'] < max_loss_rate]
#                                    and t[IBT_variation] is None
#                                    and t[burst_size_variation] is None]
        # * * * * * * * * * * * * * * * * * *
        # * * * * * poorly responsive * * * * 
        # * * * * * * * * * * * * * * * * * *
        # never any always_responsive traces!
        if not always_responsive_traces:
            logging.info("\t- poorly responsive router (no always_responsive traces!)")
            if verbose:
                for t in sorted(traces_this_router, key=lambda x: x['actual_rate']):
                    new_row = [t['actual_rate'],
                                round(t[IBT_variation], 4) if t[IBT_variation] else None,
                                round(t[burst_size_variation], 4) if t[burst_size_variation] else None,
                                t[IBT_avg],
                                t[ans_burst_size_avg],
                                round(t['loss_rate'], 4),
                                t['answering_rate'],
                                round((1 - t['loss_rate']) * t['initial_probes_num'], 0)]
                    table_to_   .add_row(new_row)
                table_txt = table_to_print.get_string()
                print table_to_print
            return rtypes.poorly_responsive, [], [], extra_info
        max_rate_always_responsive = max(t['actual_rate'] for t in always_responsive_traces)
        desired_probing_rate_r_always_resp = get_corresponding_expected_rate(traces_this_router, max_rate_always_responsive)
        # allow some noise inside the always_responsive range
        traces_below_max_rate = [t for t in traces_this_router
                                 if t['actual_rate'] <= max_rate_always_responsive]
        other_traces_below_max_rate = [t for t in traces_below_max_rate
                                        if t not in always_responsive_traces]
        # traces_above_max_rate are BOUND to be not-always-responsive by definition
        traces_above_max_rate = [t for t in traces_this_router
                                if t not in traces_below_max_rate]
        parameters = sorted([{'ibt': t[IBT_avg],
                            'rate': int(t['actual_rate']),
                            'bsize': t[ans_burst_size_avg],
                            'iat_cv': round(t[IBT_variation], 4) if t[IBT_variation] else None,
                            'bsize_cv': round(t[burst_size_variation], 4) if t[burst_size_variation] else None,
                            'answering_rate': t['answering_rate'],
                            'loss_rate': round(t['loss_rate'], 4),
                            'total_replies' : round((1 - t['loss_rate']) * t['initial_probes_num'], 0)}
                            for t in traces_this_router],
                            key=lambda x: x['rate'])
        # all traces have loss_rate<max_loss_Rate and no bursts ever appear
        is_always_responsive, fully_resp_noise_fract = fully_responsive_interval_test(
                                                              traces_this_router,
                                                              max_rate_always_responsive, #it's r_max when fully resp
                                                              allowed_loss_rate=max_loss_rate,
                                                              allowed_noise=allowed_noise) #best: 0.2
        
        is_always_responsive = desired_probing_rate_r_always_resp == desired_probing_rate_r_max or\
                                max_rate_always_responsive == r_max
        extra_info['fully_responsive_noise_fraction'] = fully_resp_noise_fract
        # * * * * * * * * * * * * * * * * * *
        # * * * * ALWAYS RESPONSIVE * * * * *
        # * * * * * * * * * * * * * * * * * *
        if is_always_responsive:
            logging.info("\t- always responsive router")
            if verbose:
                for t in sorted(traces_this_router, key=lambda x: x['actual_rate']):
                    new_row = [t['actual_rate'],
                                round(t[IBT_variation], 4) if t[IBT_variation] else None,
                                round(t[burst_size_variation], 4) if t[burst_size_variation] else None,
                                t[IBT_avg],
                                t[ans_burst_size_avg],
                                round(t['loss_rate'], 4),
                                t['answering_rate'],
                                round((1 - t['loss_rate']) * t['initial_probes_num'], 0)]
                    table_to_print.add_row(new_row)
                table_txt = table_to_print.get_string()
                print table_to_print
            return rtypes.always_responsive, [], [], extra_info
        # at this point, there is some noise
        if verbose:
            #print always_responsive_traces, then other_traces_below_max in yellow, then 
            for t in sorted(always_responsive_traces, key=lambda x: x['actual_rate']):
                new_row = [t['actual_rate'],
                            round(t[IBT_variation], 4) if t[IBT_variation] else None,
                            round(t[burst_size_variation], 4) if t[burst_size_variation] else None,
                            t[IBT_avg],
                            t[ans_burst_size_avg],
                            round(t['loss_rate'], 4),
                            t['answering_rate'],
                            round((1 - t['loss_rate']) * t['initial_probes_num'], 0)]
                table_to_print.add_row(new_row)
            for t in sorted(other_traces_below_max_rate, key=lambda x: x['actual_rate']):
                new_row = [t['actual_rate'],
                            round(t[IBT_variation], 4) if t[IBT_variation] else None,
                            round(t[burst_size_variation], 4) if t[burst_size_variation] else None,
                            t[IBT_avg],
                            t[ans_burst_size_avg],
                            round(t['loss_rate'], 4),
                            t['answering_rate'],
                            round((1 - t['loss_rate']) * t['initial_probes_num'], 0)]
                new_row = [ bcolors.WARNING + str(el) + bcolors.ENDC for el in new_row]
                table_to_print.add_row(new_row)
            for t in sorted(traces_above_max_rate, key=lambda x: x['actual_rate']):
                new_row = [t['actual_rate'],
                            round(t[IBT_variation], 4) if t[IBT_variation] else None,
                            round(t[burst_size_variation], 4) if t[burst_size_variation] else None,
                            t[IBT_avg],
                            t[ans_burst_size_avg],
                            round(t['loss_rate'], 4),
                            t['answering_rate'],
                            round((1 - t['loss_rate']) * t['initial_probes_num'], 0)]
                new_row = [ bcolors.FAIL + str(el) + bcolors.ENDC for el in new_row]
                table_to_print.add_row(new_row)
            new_row = [max_rate_always_responsive, 
                   (len(always_responsive_traces),
                    '%.1f%%' % (len(always_responsive_traces) * 100.0 / len(traces_below_max_rate))
                    ),
                    (len(other_traces_below_max_rate),
                    '%.1f%%' % (len(other_traces_below_max_rate) * 100.0 / len(traces_below_max_rate))
                    ),
                    len(traces_above_max_rate)]
            table3.add_row(new_row)
        extra_info['max_rate_always_responsive'] = max_rate_always_responsive
#        is_mostly_responsive_c1 = len(other_traces_below_max_rate) <= allowed_noise * len(traces_below_max_rate)
        is_mostly_responsive = max_rate_always_responsive < r_max
        # * * * * * * * * * * * * * * * * *
        # * * * * MOSTLY RESPONSIVE * * * * 
        # * * * * * * * * * * * * * * * * * 
        if is_mostly_responsive:
            ans_rates_irr = [t['answering_rate'] for t in traces_above_max_rate]
            if min(ans_rates_irr) < 0.9 * np.mean(ans_rates_irr):
                ans_rates_irr.remove(min(ans_rates_irr)) #basic filtering
            c_1 = all([0.9 * np.mean(ans_rates_irr) <= el <= 1.1*np.mean(ans_rates_irr)
                         for el in ans_rates_irr])
            #verify that the answering rate is consistent with the loss rate
            ratios = [(t['answering_rate']*1.0/t['actual_rate'])*1.0/(1-t['loss_rate']) 
                       for t in traces_above_max_rate]
            c_2 = all([0.9 <= el <= 1.1 for el in ratios])
            if c_1 and c_2:
                # *****************************************
                # MOSTLY RESPONSIVE RATE LIMITED
                # *****************************************
                logging.info("\t- mostly responsive RATE-LIMITED router")
#                # first approximation of ans rate
                traces_above_rlim = [t for t in traces_this_router
                                    if t['actual_rate'] > max(ans_rates_irr)]
                logging.info("\t- ans rates irr phase: %s" % sorted(ans_rates_irr))
                extra_info['limited_ans_rate_most_common'] = most_common(ans_rates_irr)
                extra_info['limited_ans_rate'] = max(ans_rates_irr)
                logging.info("\t- ans ratios irr phase: %s" % sorted(ratios))
                if verbose:
                    print table_to_print
                    print table3
                return rtypes.mostly_responsive_rl, [], [], extra_info
            else:
                # *****************************************
                # MOSTLY RESPONSIVE
                # *****************************************
                logging.info( "\t- mostly responsive router")
                logging.info( "\t- ans rates irr phase: %s" % ans_rates_irr)
                logging.info( "\t- ans ratios irr phase: %s" % ratios)
                if verbose:
                    #print always_responsive_traces, then other_traces_below_max in yellow, then 
                    # traces_above_max_rate in red
                    print table_to_print
                    print table3
                return rtypes.mostly_responsive, [], [], extra_info
        else:
            logging.info("\t- noisy responsive router")
            if verbose:
                print table_to_print
                print table3
            return rtypes.noisy_responsive, [], [], extra_info
    # # # # # # # # # # # # # # # # # # # # # ## 
    # Here routers are suspected to be on-off # # # 
    # # # # # # # # # # # ## # # # ## # # # # ## # #
    extra_info['ibt_cvs'] = [t[IBT_variation] for t in traces_low_cvs]
    extra_info['bs_cvs'] = [t[burst_size_variation] for t in traces_low_cvs]
    extra_info['min_ibt_cv'] = min(extra_info['ibt_cvs'])
    extra_info['min_bs_cv'] = min(extra_info['bs_cvs'])
    extra_info['max_ibt_cv'] = max(extra_info['ibt_cvs'])
    extra_info['max_bs_cv'] = max(extra_info['bs_cvs'])
    extra_info['total_trace_number'] = len(traces_this_router)
    extra_info['low_cvs_trace_number'] = len(traces_low_cvs)
    # list of dictionaries, each one representing a single experiment with low CoVs 
    # and its parameters
    experiments_low_covs = [{'IBT_avg': t[IBT_avg],
                'rate': int(t['actual_rate']),
                'ans_burst_size_avg': t[ans_burst_size_avg],
                'ibt_cv': round(t[IBT_variation], 4),
                'b_cv': round(t[burst_size_variation], 4),
                'answering_rate': t['answering_rate'],
                'loss_rate': round(t['loss_rate'], 4),
                'total_replies' : round((1 - t['loss_rate']) * t['initial_probes_num'], 0)}
                for t in traces_low_cvs]
    # * * grouping (1) * * *
    #group values when IBT and burst size are roughly the same
    for p in experiments_low_covs:
        #ibt
        if p['IBT_avg'] > 0.9:
            p['IBT_avg'] = round(p['IBT_avg'], 1)
        else:
            p['IBT_avg'] = round(p['IBT_avg'], 3)
        #burst
        p['ans_burst_size_avg'] = round(p['ans_burst_size_avg'], 0)
    pairs = list(set([(p['IBT_avg'], p['ans_burst_size_avg']) for p in experiments_low_covs]))
    onoff_params = []
    for p in pairs:
        rates_this_pair = sorted(list(set([el['rate'] for el in experiments_low_covs
                            if el['IBT_avg'] == p[0]
                            and el['ans_burst_size_avg'] == p[1]])))
        answering_rates_this_pair = sorted(list(set([el['answering_rate'] for el in experiments_low_covs
                            if el['IBT_avg'] == p[0]
                            and el['ans_burst_size_avg'] == p[1]])))
        totalreplies_this_pair = sorted(list(set([el['total_replies'] for el in experiments_low_covs
                            if el['IBT_avg'] == p[0]
                            and el['ans_burst_size_avg'] == p[1]])))
        lossrates_this_pair = sorted(list(set([round(el['loss_rate'], 4) for el in experiments_low_covs
                            if el['IBT_avg'] == p[0]
                            and el['ans_burst_size_avg'] == p[1]])))
        ibtcvs_this_pair = sorted(list(set([round(el['ibt_cv'], 3) for el in experiments_low_covs
                            if el['IBT_avg'] == p[0]
                            and el['ans_burst_size_avg'] == p[1]])))
        bcvs_this_pair = sorted(list(set([round(el['b_cv'], 3) for el in experiments_low_covs
                            if el['IBT_avg'] == p[0]
                            and el['ans_burst_size_avg'] == p[1]])))
        onoff_params.append({'IBT_avg': p[0], 'ans_burst_size_avg': p[1],
                            'IBT_cvs': ibtcvs_this_pair, 'bsize_cvs': bcvs_this_pair,
                            'rates': rates_this_pair,# 'answering_rates': answering_rates_this_pair,
                            'total_replies': totalreplies_this_pair,
                            'loss_rates': lossrates_this_pair})
    onoff_params = sorted(onoff_params, key=lambda x: x['rates'][0])
    # * * grouping (2) * * *
    onoff_config_params = []
    pairs_onoff = sorted([(p['IBT_avg'], p['ans_burst_size_avg'], p['rates']) for p in onoff_params])
    groups = [[pairs_onoff[0]]]
    for p in pairs_onoff[1:]:
        group_found = False
        ibt = p[0]
        bsize = p[1]
        for i, g in enumerate(groups):
            if all( 0.75 <= 1.0 * ibt / el[0] <= 1.25 and   
                    0.75 <= 1.0 * bsize / el[1] <= 1.25
                    for el in g):
                #the pair belongs to this group
               groups[i].append(p)
               group_found = True
               break
        if not group_found:
            #this is a new group
            groups.append([p])
    for g in groups:
        ibt_occurrences = [[el[0]] * sum(1 for p in experiments_low_covs if p['IBT_avg'] == el[0]) for el in g]
        ibt = np.mean([el for sublist in ibt_occurrences for el in sublist])
        bsize_occurrences = [[el[1]] * sum(1 for p in experiments_low_covs if p['ans_burst_size_avg'] == el[1]) for el in g]
        bsize = np.mean([el for sublist in bsize_occurrences for el in sublist])
        onoff_config_params.append({'ibt': ibt, 'bsize': round(bsize, 1),
                                    'rates': sorted([r for el in g for r in el[2]])})
    extra_info['onoff_config_params'] = onoff_config_params
    # now filter out the "wrong" parameters: only consider one per router,
    # the one that appeared most often 
    # in the lines above it seems that I keep track of the experiments as a repeated rate in the
    # onoff_config_params. I'll trust myself on this!
    extra_info['onoff_config_filtered'] = max(onoff_config_params, key=lambda x: len(x['rates']))
    
    #check that for *all* traces sent at a rate >= min_rate_low_cvs the CoV is < max_cv
    min_rate_low_cvs = min(val['rate'] for val in experiments_low_covs)
    max_rate_low_cvs = max(val['rate'] for val in experiments_low_covs)
    rate_range_low_cvs = (min_rate_low_cvs, max_rate_low_cvs)
    extra_info['min_rate_low_cvs'] = min_rate_low_cvs
    extra_info['max_rate_low_cvs'] = max_rate_low_cvs
    traces_higher_rates = [t for t in traces_this_router
                           if t['actual_rate'] >= min_rate_low_cvs]
    # check the responsiveness *before* the on-off range
    # the answering rate should roughly the same as the probing rate in [r_min, r_onoff];
    # in (r_onoff, min_rate_low_covs=r_0) there might be no tested rate or
    # the gaps might cancel out the on-off behaviour
    # in [r_, max_rate_low_covs=r_1] the on-off behaviour is observed
    # in (r_1, r_max] no on-off behaviour is observed
    ########st
    # the loss rate should be very small (let's say <=0.1)
    # ===>>>> discard this test. The behaviour *before* rate limitation is first seen 
    # is more or less predictable, but subject to noise when we are getting close
    # to the rate limitation threshold. Checking this isn't relevant anyway.
#    below_min_test = all([t['loss_rate'] <= 0.1 and 
#                            0.9 <= t['answering_rate']*1.0/t['actual_rate'] <= 1.1
#                          for t in traces_below_min_rate])
    traces_above_onoff_range = [t for t in traces_this_router
                                if t['actual_rate'] > max_rate_low_cvs]
    traces_onoff_range  = [t for t in traces_this_router
                           if min_rate_low_cvs <= t['actual_rate'] <= max_rate_low_cvs]
    onoff_traces_onoff_range = [t for t in traces_onoff_range
                                if t[IBT_variation] is not None
                                and t[burst_size_variation] is not None
                                and 0 <= t[IBT_variation] < max_cv
                                and 0 <= t[burst_size_variation] < max_cv]
    irregular_traces_onoff_range = [t for t in traces_onoff_range
                                    if t not in onoff_traces_onoff_range]
    onoff_rate = int(round(max([params['bsize']*1.0 / params['ibt']
                                for params in extra_info['onoff_config_params']]), 0))
#    onoff_rate_max = onoff_rate
#    extra_info['onoff_rate_max'] = onoff_rate_max
#    extra_info['onoff_rate_most'] = extra_info['onoff_config_filtered']['bsize'] * 1.0 / extra_info['onoff_config_filtered']['ibt']
    extra_info['onoff_rate'] = onoff_rate #extra_info['onoff_rate_most']
    
    onoff_params_final = extra_info['onoff_config_filtered']
    onoff_params_final['answering_rate'] = extra_info['onoff_rate']
    
    traces_below_onoff_rate =  [t for t in traces_this_router
                              if t['actual_rate'] <= onoff_rate]
    traces_between_onoff_rate_and_r0 = [t for t in traces_this_router
                                        if onoff_rate < t['actual_rate'] < min_rate_low_cvs ]
                                        
    if extra_info['min_rate_low_cvs'] < extra_info['onoff_rate'] :
        logging.warning( "OPS OPS OPS! r_0 (%s) < r_onoff (%s) !!!!!" % (extra_info['min_rate_low_cvs'], extra_info['onoff_rate']))
    pre_onoff_fully_responsive, noise = fully_responsive_interval_test(
                                                              traces_this_router,
                                                              onoff_rate,
                                                              allowed_loss_rate=max_loss_rate,
                                                              allowed_noise=allowed_noise)
    extra_info['fully_responsive_noise_fraction'] = noise
    below_onoff_test = pre_onoff_fully_responsive
    # test2: can't test conditions on bursts, since they might be cancelled out by the gaps tolerance
    # So we test the answering rate: it should equal r_onoff
    r_onoff_r0_test = all([0.90* onoff_rate * t['actual_duration'] <= (1-t['loss_rate'])*t['initial_probes_num'] <= 1.1* onoff_rate * t['actual_duration']
                           for t in traces_between_onoff_rate_and_r0])
    traces_to_consider = [(traces_below_onoff_rate, below_onoff_test, bcolors.OKBLUE, bcolors.FAIL),
                          (traces_between_onoff_rate_and_r0, r_onoff_r0_test, bcolors.HEADER, bcolors.HEADER)] #bcolors.WARNING
    for trace_to_print, a_test, ok_color, fail_color in traces_to_consider:
        for t in sorted(trace_to_print, key=lambda x: x['actual_rate']):
            new_row = [t['actual_rate'],
                    round(t[IBT_variation], 4) if t[IBT_variation] else None,
                    round(t[burst_size_variation], 4) if t[burst_size_variation] else None,
                    t[IBT_avg],
                    t[ans_burst_size_avg],
                    round(t['loss_rate'], 4),
                    t['answering_rate'],
                    round((1 - t['loss_rate']) * t['initial_probes_num'], 0)]
            new_row = [ ok_color + str(el) + bcolors.ENDC for el in new_row] #old: color
            table_to_print.add_row(new_row)
    test1_str = below_onoff_test
    if not below_onoff_test:
        test1_str = bcolors.FAIL + str(below_onoff_test) + bcolors.ENDC
    test2_str = r_onoff_r0_test
    if not r_onoff_r0_test:
        test2_str = bcolors.FAIL + str(r_onoff_r0_test) + bcolors.ENDC
    pre_onoff_test_str = "\t- [r_min, r_onoff]-test: %s ; (r_onoff, r_0)-test: %s" % (
                                                    test1_str, test2_str) #extra_info['pre_onoff_tests']
    extra_info['below_onoff_test'] = below_onoff_test
    extra_info['r_onoff_r0_test'] = r_onoff_r0_test
    extra_info['onoff_noise'] = len(irregular_traces_onoff_range)*1.0/len(traces_onoff_range)
    if study_rtt:
        extra_info['mean_rtt_onoff'] = np.mean([t['rtt_avg'] for t in onoff_traces_onoff_range])
        extra_info['std_rtt_onoff'] = np.mean([t['rtt_std'] for t in onoff_traces_onoff_range])
        extra_info['cov_rtt_onoff'] = np.mean([t['rtt_variation'] for t in onoff_traces_onoff_range])
        if irregular_traces_onoff_range:
            extra_info['mean_rtt_other'] = np.mean([t['rtt_avg'] for t in irregular_traces_onoff_range])
            extra_info['std_rtt_other'] = np.mean([t['rtt_std'] for t in irregular_traces_onoff_range])
            extra_info['cov_rtt_other'] = np.mean([t['rtt_variation'] for t in irregular_traces_onoff_range])
        else:
            extra_info['mean_rtt_other'] = extra_info['std_rtt_other'] = extra_info['cov_rtt_other'] = -1
        if traces_above_onoff_range:
            extra_info['mean_rtt_above'] = np.mean([t['rtt_avg'] for t in traces_above_onoff_range])
            extra_info['std_rtt_above'] = np.mean([t['rtt_std'] for t in traces_above_onoff_range])
            extra_info['cov_rtt_above'] = np.mean([t['rtt_variation'] for t in traces_above_onoff_range])
        else:
            extra_info['mean_rtt_above'] = extra_info['std_rtt_above'] = extra_info['cov_rtt_above'] = -1
    onoff_in = (len(onoff_traces_onoff_range),
                '%.1f%%' % (len(onoff_traces_onoff_range)*100.0 / len(traces_onoff_range))
                if traces_onoff_range else None)
    irregular_in = (len(irregular_traces_onoff_range),
                    '%.1f%%' % (len(irregular_traces_onoff_range)*100.0 / len(traces_onoff_range))
                    if traces_onoff_range else None)
    desired_probing_rate_r_min = get_corresponding_expected_rate(traces_this_router, r_min)
    desired_probing_rate_r_max = get_corresponding_expected_rate(traces_this_router, r_max)
    desired_probing_rate_r_1 = get_corresponding_expected_rate(traces_this_router, max_rate_low_cvs)
    # pure on-off test
    is_onoff_at_one_rate = ((min_rate_low_cvs == max_rate_low_cvs) or (desired_probing_rate_r_min == desired_probing_rate_r_max))\
                                and ((max_rate_low_cvs != r_max) or (desired_probing_rate_r_1 != desired_probing_rate_r_max))
    if is_onoff_at_one_rate:
        logging.info("\t !!!! r_0 == r_1 !!!!")
    is_pure_onoff_old_old = all([0 <= t[IBT_variation] < max_cv 
                    and 0 <= t[burst_size_variation] < max_cv
                    for t in traces_higher_rates])
    onoff_traces = [ t for t in traces_higher_rates
                    if 0 <= t[IBT_variation] < max_cv 
                    and 0 <= t[burst_size_variation] < max_cv]
#    is_pure_onoff_oldish = max_rate_low_cvs == r_max
    # condition: r_1 == r_max 
    is_pure_onoff = (desired_probing_rate_r_1 == desired_probing_rate_r_max) or (max_rate_low_cvs == r_max)
    is_pure_onoff = is_pure_onoff and not is_onoff_at_one_rate
    if verbose:
        for p in onoff_params:
            new_row = [insert_newline_every_n(p['rates'], 2),
                        insert_newline_every_n(p['IBT_cvs'], 2),
                        insert_newline_every_n(p['bsize_cvs'], 2),
                        p['IBT_avg'], 
                        p['ans_burst_size_avg'],
                        insert_newline_every_n(p['loss_rates'],2),
                        insert_newline_every_n(p['answering_rates'],2),
                        insert_newline_every_n(p['total_replies'], 2)
                        ]
            new_row = [ str(el) for el in new_row]
            table_to_print.add_row(new_row)
        table2.add_row([rate_range_low_cvs, onoff_in, irregular_in,
                        len(traces_above_onoff_range)])
    # * * * * * pure on-off* * * * *
    if is_pure_onoff:
        logging.info(bcolors.OKGREEN + "\t- Pure on-off!" + bcolors.ENDC)
        logging.info("\t- r_min: %s,  r_onoff: %s,  r_0: %s,  r_1: %s,  r_max: %s" %(
                    extra_info['min_probing_rate'], onoff_rate, extra_info['min_rate_low_cvs'],
                    extra_info['max_rate_low_cvs'], extra_info['max_probing_rate']))
        logging.info(pre_onoff_test_str)
        logging.info(table_to_print)
        table_txt = table_to_print.get_string()
        return rtypes.pure_onoff, onoff_params_final, [], extra_info
    else:
        irregular = [{ 'rate': int(t['actual_rate']),
                    'ibt_cv': round(t[IBT_variation], 4)
                            if t[IBT_variation] is not None else None,
                    'bsize_cv': round(t[burst_size_variation], 4)
                            if t[burst_size_variation] is not None else None,
                    'ibt': round(t[IBT_avg], 3)
                            if t[IBT_avg] is not None else None,
                    'bsize': round(t[ans_burst_size_avg], 0)
                            if t[ans_burst_size_avg] is not None else None,
                    'answering_rate': t['answering_rate'],
                    'loss_rate': round(t['loss_rate'], 4),
                    'total_replies' : round((1 - t['loss_rate']) * t['initial_probes_num'], 0)}
                    for t in traces_this_router
                    if t['actual_rate'] >= min_rate_low_cvs
                    and not (0 <= t[IBT_variation] < max_cv
                    and 0 <= t[burst_size_variation] < max_cv)]
        irregular = sorted(irregular, key=lambda x: x['rate'])
        episodes_above_onoff_range =[{
                    'rate': int(t['actual_rate']),
                    'input_rate': t['expected_rate'],
                    'ibt_cv': round(t[IBT_variation], 4)
                            if t[IBT_variation] is not None else None,
                    'bsize_cv': round(t[burst_size_variation], 4)
                            if t[burst_size_variation] is not None else None,
                    'ibt': round(t[IBT_avg], 3)
                            if t[IBT_avg] is not None else None,
                    'bsize': round(t[ans_burst_size_avg], 0)
                            if t[ans_burst_size_avg] is not None else None,
                    'answering_rate': t['answering_rate'],
                    'loss_rate': round(t['loss_rate'], 4),
                    'total_replies' : round((1 - t['loss_rate']) * t['initial_probes_num'], 0)}
                    for t in traces_above_onoff_range
                    ]
        episodes_above_onoff_range = sorted(episodes_above_onoff_range, key=lambda x: x['rate'])
        extra_info['irregular_trace_number'] = len(irregular)
        #it could be busy-on-off or irregular on-off 
        #allow occasional noise within the range of probing rates in the on-off traces
        noise_in_onoff_range = [ep for ep in irregular
                                if min_rate_low_cvs <= ep['rate'] <= max_rate_low_cvs]
        if len(noise_in_onoff_range) != len(irregular_traces_onoff_range):
            logging.warning( '\t!!!!!!   %s != %s' % (len(noise_in_onoff_range), len(irregular_traces_onoff_range)))
        busy_test_4 = len(noise_in_onoff_range) <= 0.2 * len(traces_low_cvs)
#        allowed_noise = 0.35 #now an input parameter
        busy_test_5 = len(noise_in_onoff_range) <= allowed_noise * len(traces_onoff_range) #used to be: 0.35
        busy_test_6 = max_rate_low_cvs < r_max
        logging.info('irregular rates: %s' % [ep['rate'] for ep in irregular])
        logging.info('noisy traces:   ', len(noise_in_onoff_range), ' / ' , len(traces_onoff_range))
        if verbose:
            for p in noise_in_onoff_range:#used to be: for p in irregular
                    new_row = [ p['rate'],
                            p['ibt_cv'],
                            p['bsize_cv'],
                            p['ibt'], 
                            p['bsize'],
                            p['loss_rate'],
                            p['answering_rate'],
                            p['total_replies']]
                    new_row = [ bcolors.WARNING + str(el) + bcolors.ENDC for el in new_row]
                    table_to_print.add_row(new_row)
            for p in episodes_above_onoff_range:#used to be: for p in irregular
                new_row = [ p['rate'],
                        p['ibt_cv'],
                        p['bsize_cv'],
                        p['ibt'], 
                        p['bsize'],
                        p['loss_rate'],
                        p['answering_rate'],
                        p['total_replies']]
                new_row = [ bcolors.FAIL + str(el) + bcolors.ENDC for el in new_row]
                table_to_print.add_row(new_row)
        is_busy_onoff  = busy_test_6 and not is_onoff_at_one_rate
        if is_busy_onoff:
            logging.info("- Found a BUSY on-off router!! ")
            logging.info("\t- r_min: %s,  r_onoff: %s,  r_0: %s,  r_1: %s,  r_max: %s" %(
                    extra_info['min_probing_rate'], onoff_rate, extra_info['min_rate_low_cvs'],
                    extra_info['max_rate_low_cvs'], extra_info['max_probing_rate']))
            logging.info(pre_onoff_test_str)
            logging.info(table_to_print)
            logging.info(table2)
            if verbose:
                table_txt = table_to_print.get_string()
                table2_txt = table2.get_string()
            return rtypes.busy_onoff, onoff_params_final, irregular, extra_info
        else:
            # irregularly-onoff router
            logging.info("\t- Irregular on-off router")
            logging.info("\t- r_min: %s,  r_onoff: %s,  r_0: %s,  r_1: %s,  r_max: %s" %(
            extra_info['min_probing_rate'], onoff_rate, extra_info['min_rate_low_cvs'],
            extra_info['max_rate_low_cvs'], extra_info['max_probing_rate']))
            logging.info(pre_onoff_test_str)
            if verbose:
                print table_to_print
                print table2
                table2_txt = table2.get_string()
                table_txt = table_to_print.get_string()
            return rtypes.irregular_onoff, onoff_params_final, irregular, extra_info

################################################################################
##################### t r a c e    a n a l y s i s #############################
################################################################################

def sort_list_of_trace_filepaths(files):
    files = sorted(files, key=lambda f: (str(get_var_from_filename('trace', f)),
                                            int(get_var_from_filename('run', f)),
                                            int(get_var_from_filename('ttl', f)),
                                            int(get_var_from_filename('payload', f)),
                                            int(get_var_from_filename('rate', f))                        
                                                    ))
    return files


def get_var_from_filename(name, filename):
    if filename[-5:] == '.pcap':
        filename = filename[:-5]
    ind = int(filename.split('_').index(name) + 1)
    value = filename.split('_')[ind]
    return value


def get_experiment_input_info_from_filename(trace_name):
    info = dict()
    #from the file name, take the _-separated value after the keyword 'rate'
    info['expected_rate'] = int(get_var_from_filename('rate', trace_name))
    info['initial_probes_num'] = int(get_var_from_filename('probes', trace_name))
    info['protocol'] = str(get_var_from_filename('trace', trace_name))
    if info['protocol'] != 'ping':
        info['protocol'] = info['protocol'].upper()
    if 'run' in trace_name:
        info['run'] = int(get_var_from_filename('run', trace_name).split('.pcap')[0])#remove pcap ending
    if 'duration' in trace_name:
        info['duration'] = int(float(get_var_from_filename('duration', trace_name)))
    info['ttl'] = int(get_var_from_filename('ttl', trace_name))
    return info


def get_sending_rate_from_probes_timestamps(probes_timestamps):
    probes_timestamps = sorted(probes_timestamps)
    if len(probes_timestamps)==1: #avoid division by 0
        return 0
    return round(float(len(probes_timestamps)) / (probes_timestamps[-1] - probes_timestamps[0]), 0)


def get_actual_duration_from_probes_timestamps(probes_timestamps):
    return max(probes_timestamps) - min(probes_timestamps)


def get_loss_rate(pairs):
    unanswered = [pp for pp in pairs if not pp[1]]
    loss_rate = float(len(unanswered)) / len(pairs)
    return loss_rate


def extract_data_from_bursts(post_info, v=''):  #v stands for variant
    filtered_ans_bursts = 'filtered_ans_bursts' + v
    filtered_unans_bursts = 'filtered_unans_bursts' + v
    IBT = 'IBT' + v
    IBT_avg = 'IBT_avg' + v
    IBT_std = 'IBT_std' + v
    IBT_variation = 'IBT_variation' + v
    ans_burst_size_variation = 'ans_burst_size_variation' + v
    unans_burst_size_variation = 'unans_burst_size_variation' + v
    ans_burst_size_avg = 'ans_burst_size_avg' + v
    unans_burst_size_avg = 'unans_burst_size_avg' + v
    ans_burst_size_std = 'ans_burst_size_std' + v
    unans_burst_size_std = 'unans_burst_size_std' + v
    avg_inter_packet_time = 'avg_inter_packet_time' + v
    min_inter_packet_time= 'min_inter_packet_time' + v 
    max_inter_packet_time = 'max_inter_packet_time' + v
    median_inter_packet_time = 'median_inter_packet_time' + v
    cov_inter_packet_time = 'cov_inter_packet_time' + v
    variance_inter_packet_time = 'variance_inter_packet_time' + v
    # compute bursts variation
    if post_info[filtered_ans_bursts] and post_info[filtered_unans_bursts] and post_info[IBT]:
        # compute coefficients of variation for ans bursts size, unans bursts size, IBT
        # ans burst size variation
        post_info[ans_burst_size_variation] = None
        all_ans_burst_sizes = [burst['size'] for burst in post_info[filtered_ans_bursts]]
        if len(all_ans_burst_sizes) > 1:
            post_info[ans_burst_size_variation] = scipy.stats.variation(all_ans_burst_sizes)
        # unans burst size variation
        post_info[unans_burst_size_variation] = None
        all_unans_burst_sizes = [burst['size'] for burst in post_info[filtered_unans_bursts]]
        if len(all_unans_burst_sizes) > 1:
            post_info[unans_burst_size_variation] = scipy.stats.variation(all_unans_burst_sizes)
        # IBT variation
        post_info[IBT_variation] = None
        if len(post_info[IBT]) > 1:
            post_info[IBT_variation] = scipy.stats.variation(post_info[IBT])
        # compute mean ans bursts size, unans bursts size, IBT
        post_info[ans_burst_size_avg] = np.mean([burst['size'] for burst in post_info[filtered_ans_bursts]])
        post_info[unans_burst_size_avg] = np.mean([burst['size'] for burst in post_info[filtered_unans_bursts]])        
        post_info[IBT_avg] = np.mean(post_info[IBT])
        # compute std for all the above
        post_info[ans_burst_size_std] = np.std([burst['size'] for burst in post_info[filtered_ans_bursts]])
        post_info[unans_burst_size_std] = np.std([burst['size'] for burst in post_info[filtered_unans_bursts]])
        post_info[IBT_std] = np.std(post_info[IBT])
        
        #save the overall average/min/max/median inter-PACKET time inside an answered burst
        averages = [  burst['avg_inter_packet_time']
                      for burst in post_info[filtered_ans_bursts]
                      if burst['avg_inter_packet_time'] is not None]
        post_info[avg_inter_packet_time] = np.mean(averages) if averages else None
        minimums = [burst['min_inter_packet_time']
                    for burst in post_info[filtered_ans_bursts]
                    if burst['min_inter_packet_time'] is not None]
        post_info[min_inter_packet_time] = min(minimums) if minimums else None
        maximums = [  burst['max_inter_packet_time']
                      for burst in post_info[filtered_ans_bursts]
                      if burst['max_inter_packet_time'] is not None]
        post_info[max_inter_packet_time] = max(maximums) if maximums else None
        all_inter_packet_times = [val for burst in post_info[filtered_ans_bursts]
                                      for val in burst['inter_packet_times']
                                      if val is not None]
        post_info[median_inter_packet_time] = np.median(all_inter_packet_times) if all_inter_packet_times else None
        post_info[cov_inter_packet_time] = scipy.stats.variation(all_inter_packet_times) if all_inter_packet_times else None
        post_info[variance_inter_packet_time] = np.var(all_inter_packet_times) if all_inter_packet_times else None
    else:
        post_info[ans_burst_size_variation] = post_info[unans_burst_size_variation] = post_info[IBT_variation] = None
        post_info[ans_burst_size_avg] = post_info[unans_burst_size_avg] = post_info[IBT_avg] = None
        post_info[ans_burst_size_std] = post_info[unans_burst_size_std] = post_info[IBT_std] = None
        post_info[avg_inter_packet_time] = post_info[min_inter_packet_time] = \
                post_info[max_inter_packet_time] = post_info[median_inter_packet_time] =\
                post_info[cov_inter_packet_time] = post_info[variance_inter_packet_time] = None
    logging.info("\t- Inter-packet time for answered bursts only:"
                "\n\t\taverage: %s"
                "\n\t\tmin: %s"
                "\n\t\tmax: %s"
                "\n\t\tmedian: %s"
                "\n\t\tvariance %s"
                "\n\t\tCoV: %s" % (post_info[avg_inter_packet_time],
                                   post_info[min_inter_packet_time],
                                   post_info[max_inter_packet_time],
                                   post_info[median_inter_packet_time],
                                   post_info[variance_inter_packet_time],
                                   post_info[cov_inter_packet_time])
                )
    return post_info


def arrange_by_burst(post_info, variants, period_starts_with_ans=True):
    """
    variants is a list like [None, 1,2,3] where:
    - None specifies that I do not want to allow any unanswered probes to be disregarded (same as 0!!!)
    - 1 specifies that I want bursts of 1 unanswered probes to be disregarded
    - 2 specifies that I wanted bursts of 2 unanswered probes to be disregarded
    - ecc
    """
    for var in variants:
        # v is the extra string to add to dictionary keys for each variant used
        # var is the allowed gap in answered probes
        if var is None:
            #v = ''
            continue
        else:
            v = '_gaps_%s' % var
        logging.info("\n*****************************************" * 4)
        logging.info("variant =   %s" % v)
        logging.info("*****************************************\n" * 4) 
        
        post_info['ans_bursts' + v], post_info['unans_bursts' + v]  = extract_bursts_from_timeseries(
                                                                            post_info['full_timeseries'],
                                                                            tolerate_gaps_of=var)
        #Filter out possible partial periods: the first and the last one
        logging.info('\t - retrieving data: bursts extracted')
        post_info['filtered_ans_bursts' + v], post_info['filtered_unans_bursts' + v], \
                removed_last = filter_bursts(post_info['ans_bursts' + v],
                                             post_info['unans_bursts' + v],
                                             period_starts_with_ans=period_starts_with_ans)
        logging.info( '\t- retrieving data: bursts filtered')
        post_info['IBT' + v] = get_IBT_from_bursts(post_info['filtered_ans_bursts' + v],
                                                    post_info['filtered_unans_bursts' + v],
                                                    period_starts_with_ans=period_starts_with_ans,
                                                    removed_last=removed_last)
        logging.info('\t[%s] - retrieving data: IBT')
        # store coeffient of variation, mean and std for ans burst size, unans burst size and IBT
        post_info = extract_data_from_bursts(post_info, v=v) 
        logging.info('\t=> ans burst variation: %s, unans burst variation: %s, '
                'periods variation: %s' % (post_info['ans_burst_size_variation' + v],
                                            post_info['unans_burst_size_variation' + v],
                                            post_info['IBT_variation' + v]))
    return post_info



def get_experiment_post_data(trace, probes_protocol, replies_icmp_type, ttl, gaps=4):
    post_info = dict()
    probes = get_probes(trace, probes_protocol)
    if not probes:
        logging.info("\t =>>>>>> No PROBES found!!!!! <<<<<<<<")
        return None

    replies = get_replies(trace, replies_icmp_type) #time-exceeded
    logging.info('\t - retrieving data: trace arranged into probes and replies')
    post_info['router_mac_addr'] = post_info['router_vendor'] = None
    post_info['hostname'] = probes[0][IP].src
    if not replies:
        logging.info("\t ........No replies found!!!!!........" )
        post_info['replies_timestamps'] = []
        post_info['answering_rate'] = 0
        post_info['replies_interpacket_series'] = []
        post_info['router'] = None
    else:
        post_info['replies_timestamps'] = get_timestamps(replies)
        post_info['answering_rate'] = get_sending_rate_from_probes_timestamps(post_info['replies_timestamps'])
        post_info['replies_interpacket_series'] = get_inter_packet_interval_series(post_info['replies_timestamps'])
        post_info['router'] = replies[0][IP].src 
        post_info['probes_ttl'] = list(set([pkt[IP].ttl for pkt in probes]))
        post_info['replies_ttl'] = list(set([pkt[IP].ttl for pkt in replies]))
        if ttl == 1:
            post_info['router_mac_addr'] = replies[0][Ether].src
            post_info['router_vendor'] = maclookup.lookup_mac(post_info['router_mac_addr'])
            
    post_info['replies_interpacket_variation'] = scipy.stats.variation(post_info['replies_interpacket_series'])
    logging.info('\t-replies interpacket variation: %s ' % post_info['replies_interpacket_variation'])
    logging.info('probes protocol: ', probes_protocol)
    replies_protocol = 'ping' if replies_icmp_type==0 else 'icmp'
    pairs = match_probes(probes, replies, probes_protocol, replies_protocol)
    logging.info('\t - retrieving data: probes and replies matched!')
    post_info['probes_timestamps'] = get_timestamps(probes)
    post_info['probes_interpacket_series'] = sorted(get_inter_packet_interval_series(
                                                        post_info['probes_timestamps']))
    post_info['probes_interpacket_variation'] = scipy.stats.variation(post_info['probes_interpacket_series'])
    logging.info('\t- probes interpacket variation: %s ' % post_info['probes_interpacket_variation'])
    post_info['avg_probes_interpacket_time'] = np.mean(post_info['probes_interpacket_series'])
    logging.info('\t- average inter-packet time for probes : %s ' % post_info['avg_probes_interpacket_time'])
    post_info['min_probes_interpacket_time'] = min(post_info['probes_interpacket_series'])
    logging.info('\t- minimum inter-packet time for probes : %s ' % post_info['min_probes_interpacket_time'])
    post_info['max_probes_interpacket_time'] = max(post_info['probes_interpacket_series'])
    logging.info('\t- max inter-packet time for probes : %s ' % post_info['max_probes_interpacket_time'])
    post_info['median_probes_interpacket_time'] = np.median(post_info['probes_interpacket_series'])
    logging.info('\t- median inter-packet time for probes : %s ' % post_info['median_probes_interpacket_time'])
    post_info['variance_probes_interpacket_time'] = np.var(post_info['probes_interpacket_series'])
    logging.info('\t- max inter-packet time for probes : %s ' % post_info['variance_probes_interpacket_time'])
    # get actual sending rate
    post_info['actual_rate'] = get_sending_rate_from_probes_timestamps(post_info['probes_timestamps'])
    post_info['actual_duration'] = get_actual_duration_from_probes_timestamps(post_info['probes_timestamps'])
    post_info['loss_rate'] = get_loss_rate(pairs)
    post_info['timeseries'] = get_timeseries(pairs)
    post_info['full_timeseries'] = get_full_timeseries(pairs)
    logging.info('\t- retrieving data: got all timeseries')
    # extract bursts from timeseries
    post_info = arrange_by_burst(post_info, variants=[gaps])
    post_info['rtt_variation'] = None
    rtts = [rtt for rtt in post_info['timeseries'] if rtt != 'L']
    if len(rtts) > 1:
        post_info['rtt_variation'] = scipy.stats.variation(rtts)
    post_info['rtt_avg'] = post_info['rtt_std'] = post_info['rtt_max'] = post_info['rtt_min'] = None
    post_info['rtt_median'] = None
    if rtts:
        post_info['rtt_avg'] = np.mean(rtts)
        post_info['rtt_std'] = np.std(rtts)
        post_info['rtt_max'] = max(rtts)
        post_info['rtt_min'] = min(rtts)
        post_info['rtt_median'] = np.median(rtts)
    logging.info("\t- RTT variation: %s" % post_info['rtt_variation'])
    logging.info('\t - retrieving data: variations computed')
    return post_info


# use this to group answered bursts
def group_runs(li,tolerance=2):
    """ it groups a sorted list of integers into sublists of consecutive numbers and 
    tolerates a gap specified by tolerance before creating a new sublist
    
    Use this when grouping a timeseries of integers corresponding to the position a 
    packet in a timeseries. 
    
    Use it for the timeseries of answered probes: e.g. in order to tolerate single 
    unanswered probes (single losses), you have to tolerate a gap of 1 packet between two
    consecutive answered probes, which translates into tolerance=2 in the expression
    x - last > tolerance
    
    print list(group_runs(my_list))

    """
    out = []
    last = li[0]
    for x in li:
        if x - last > tolerance:
            yield out
            out = []
        out.append(x)
        last = x
    yield out
    

# use this to group  UNanswered bursts
def group_runs_unans(li,tolerance=1, minoutsize=2):
    """ it groups a sorted list of integers into sublists of 
    at least two consecutive numbers.
    
    Use this when grouping a timeseries of integers corresponding to the position a 
    packet in a timeseries. 
    
    Use it for the timeseries of unanswered probes. For example, if you don't want to allow
    single unanswered probes to be considered, you should:
    - set minoutsize to (for instance) 2: single losses don't form a new burst
    - always set tolerance to 1: single answered probes ARE allowed. (single unanswered probes are not!)
    
    print list(group_runs_unans(my_list))

    """
    out = []
    last = li[0]
    for x in li:
        if x - last > tolerance:
            if len(out) >= minoutsize:
                yield out
            out = []
        out.append(x)
        last = x
    if len(out) >= minoutsize:  #left out erroneously in previous version
        yield out


def extract_all_routers(analyzed_traces):
    ids = sorted(list(set([get_router_id(t) for t in analyzed_traces])))
    if None in ids:
        ids.remove(None)
    return ids


def extract_bursts_from_timeseries(full_timeseries, tolerate_gaps_of=0):
    list_of_bursts = []
    list_of_silence_periods = []
    tmp_burst = []
    IBT = [] #inter-arrival times, or rather period length
    #process the first element

    indices_of_answered_probes = [i for i, el in enumerate(full_timeseries) if el['reply']]
    indices_of_unanswered_probes = [i for i, el in enumerate(full_timeseries) if not el['reply']]

    answered_bursts_indices = []
    unanswered_bursts_indices = []
    if tolerate_gaps_of is None:
        # now group consecutive indices:
        # answered burst indices
        # http://stackoverflow.com/questions/2154249/identify-groups-of-continuous-numbers-in-a-list
        for k, g in itertools.groupby(enumerate(indices_of_answered_probes), lambda (i,x):i-x):
            group = map(operator.itemgetter(1), g)
            answered_bursts_indices.append(group)
        # unanswered burst indices
        for k, g in itertools.groupby(enumerate(indices_of_unanswered_probes), lambda (i,x):i-x):
            group = map(operator.itemgetter(1), g)
            unanswered_bursts_indices.append(group)
    else:
        if indices_of_answered_probes:
            answered_bursts_indices = list(group_runs(indices_of_answered_probes,
                                                    tolerance=tolerate_gaps_of + 1))
        if indices_of_unanswered_probes:
            unanswered_bursts_indices = list(group_runs_unans(indices_of_unanswered_probes,
                                                                tolerance=1,
                                                                minoutsize=tolerate_gaps_of + 1))

    # a period starts with the first answered probe
    # it ends with last unanswered probe of the next unanswered burst #not really enforced here!
    answered_bursts = []
    ans_shortened_bursts = []
    for burst_indices in answered_bursts_indices:
        burst = [full_timeseries[i] for i in burst_indices]
        inter_packet_times_this_burst = [burst[p_index]['reply']['timestamp'] - burst[p_index-1]['reply']['timestamp']
                                        for p_index in range(1, len(burst))]
        avg_inter_packet_time = min_inter_packet_time = max_inter_packet_time = median_inter_packet_time = None
        if inter_packet_times_this_burst:
            avg_inter_packet_time = np.mean(inter_packet_times_this_burst)
            min_inter_packet_time = min(inter_packet_times_this_burst)
            max_inter_packet_time = max(inter_packet_times_this_burst)
            median_inter_packet_time = np.median(inter_packet_times_this_burst)
        answered_bursts.append({'burst': burst,
                                'rtts': [p['rtt'] for p in burst],
                                'size': len(burst),
                                'timelen': burst[-1]['probe']['timestamp'] - burst[0]['probe']['timestamp'],
                                'indices': burst_indices,
                                'timestamps': [p['probe']['timestamp'] for p in burst],
                                'inter_packet_times': inter_packet_times_this_burst,
                                'avg_inter_packet_time': avg_inter_packet_time,
                                'min_inter_packet_time': min_inter_packet_time,
                                'max_inter_packet_time': max_inter_packet_time,
                                'median_inter_packet_time': median_inter_packet_time                                
                                })
        ans_shortened_bursts.append((burst_indices[0], burst_indices[-1]))
    unanswered_bursts = []
    unans_shortened_bursts = []
    for burst_indices in unanswered_bursts_indices:
        burst = [full_timeseries[i] for i in burst_indices]
        unanswered_bursts.append({'burst': burst,
                                'size': len(burst),
                                'timelen': burst[-1]['probe']['timestamp'] - burst[0]['probe']['timestamp'],
                                'indices': burst_indices,
                                'timestamps': [p['probe']['timestamp'] for p in burst]})
        unans_shortened_bursts.append((burst_indices[0], burst_indices[-1]))
    logging.info('\tunanswered bursts: %s' % unans_shortened_bursts)
    logging.info( '\tanswered bursts: %s' % ans_shortened_bursts)
    logging.info('\t-> unanswered burst lengths: %s' % [burst['size'] for burst in unanswered_bursts])
    logging.info('\t-> answered burst lengths: %s' % [burst['size'] for burst in answered_bursts])
    return answered_bursts, unanswered_bursts



def filter_bursts(answered_bursts, unanswered_bursts, period_starts_with_ans=True):
    #remove first and last period
    # a period is unans + ans
    if len(answered_bursts) + len(unanswered_bursts) <= 3:
        return [], [], [] #nothing left after filtering. Too few burst episodes

    ############################################################################
    ########################### Removing FIRST period ##########################
    ############################################################################
    first_ans = answered_bursts[0]
    first_unans = unanswered_bursts[0]
    # if first ans happened before first unans, make sure the router's actual first period happens
    # during your experiment: truncate first two bursts in  ans, first one in unans
    #first two bursts: ans + unans
    if first_ans['burst'][0]['probe']['timestamp'] < first_unans['burst'][0]['probe']['timestamp']:
        if period_starts_with_ans:
            #a period is ans+unans, so let's remove the first occurence of ans and unans [first ans might be incomplete]
            removed = (answered_bursts[0], unanswered_bursts[0])
            answered_bursts = answered_bursts[1:]
            unanswered_bursts = unanswered_bursts[1:]
            logging.info('\t\t[%s] - period_starts_with_ans: %s - filtering out FIRST period: '
                    'removed first ans burst (%s-%s),'
                    'first unans burst (%s-%s)' % (
                                    get_current_time(), period_starts_with_ans,
                                    removed[0]['indices'][0], removed[0]['indices'][-1],
                                    removed[1]['indices'][0], removed[1]['indices'][-1]))
        else:
            #a period is unans+ans
            removed = (answered_bursts[0], unanswered_bursts[0], answered_bursts[1])
            answered_bursts = answered_bursts[2:]
            unanswered_bursts = unanswered_bursts[1:]
            logging.info('\t\t[%s] - period_starts_with_ans: %s - filtering out FIRST period:'
                    ' removed first ans burst (%s-%s),'
                    'first unans burst (%s-%s), second ans burst (%s-%s)' % (
                                    get_current_time(), period_starts_with_ans,
                                    removed[0]['indices'][0], removed[0]['indices'][-1],
                                    removed[1]['indices'][0], removed[1]['indices'][-1],
                                    removed[2]['indices'][0], removed[2]['indices'][-1]))
    else: #first two bursts: unans + ans
        if period_starts_with_ans:
            removed = (unanswered_bursts[0],)
            unanswered_bursts = unanswered_bursts[1:]
            logging.info('\t\t[%s] - period_starts_with_ans: %s - filtering out FIRST period: '
                    'removed first unans burst (%s-%s)' % (
                                    get_current_time(), period_starts_with_ans,
                                    removed[0]['indices'][0], removed[0]['indices'][-1]))
        else: #if first unans happened before, truncate unans and ans (first period)
            removed = (unanswered_bursts[0], answered_bursts[0])
            unanswered_bursts = unanswered_bursts[1:]
            answered_bursts = answered_bursts[1:]
            logging.info('\t\t[%s] - period_starts_with_ans: %s - filtering out FIRST period:'
                    ' removed first ans burst(%s-%s) AND first unans burst (%s-%s)' % (
                                    get_current_time(), period_starts_with_ans,
                                    removed[0]['indices'][0], removed[0]['indices'][-1],
                                    removed[1]['indices'][0], removed[1]['indices'][-1]))
    ############################################################################
    ########################### Removing LAST period ###########################
    ############################################################################
    #Check beforehand if you'll be left with nothing:
    if len(answered_bursts) + len(unanswered_bursts) <= 2:
        return [], [], []
    removed = []
    last_ans = answered_bursts[-1]
    last_unans = unanswered_bursts[-1]
    # last two bursts in the order: ans + unans
    if last_ans['indices'][0] < last_unans['indices'][0]:
        if period_starts_with_ans:
            removed = (answered_bursts[-1], unanswered_bursts[-1])
            answered_bursts = answered_bursts[:-1]
            unanswered_bursts = unanswered_bursts[:-1]
            logging.info('\t\t[%s] - period_starts_with_ans: %s - filtering out LAST period: '
                    'removed last unans burst (%s-%s) AND last ans burst (%s-%s)' % (
                                    get_current_time(), period_starts_with_ans,
                                    removed[0]['indices'][0], removed[0]['indices'][-1],
                                    removed[1]['indices'][0], removed[1]['indices'][-1]))
        else:    #if last ans happened before last unans, truncate only unans (last period)
            removed = (unanswered_bursts[-1],)
            unanswered_bursts = unanswered_bursts[:-1]
            logging.info('\t\t[%s] - period_starts_with_ans: %s - filtering out LAST period: '
                    'removed last unans burst (%s-%s)' % (
                                    get_current_time(), period_starts_with_ans,
                                    removed[0]['indices'][0],removed[0]['indices'][-1]))
    else:         # last two bursts in the order: unans + ans
        if period_starts_with_ans:
            removed = (answered_bursts[-1],)
            answered_bursts = answered_bursts[:-1]
            logging.info('\t\t[%s] - period_starts_with_ans: %s - filtering out LAST period:'
                    ' removed last unans burst (%s-%s)' % (
                                    get_current_time(), period_starts_with_ans,
                                    removed[0]['indices'][0],removed[0]['indices'][-1]))
        else:
            #if last unans happened before last ans
            removed = (unanswered_bursts[-1], answered_bursts[-1])
            answered_bursts = answered_bursts[:-1]
            unanswered_bursts = unanswered_bursts[:-1]
            logging.info('\t\t[%s] - period_starts_with_ans: %s - filtering out LAST period: '
                    'removed last unans burst (%s-%s) AND last ans burst (%s-%s)' % (
                                    get_current_time(), period_starts_with_ans,
                                    removed[0]['indices'][0], removed[0]['indices'][-1],
                                    removed[1]['indices'][0], removed[1]['indices'][-1]))
    #when period starts with ans, a removed last period will be either ans or ans+unans
    return answered_bursts, unanswered_bursts, removed



def get_IBT_from_bursts(ans_bursts, unans_bursts, period_starts_with_ans=True,
                        removed_last=None):
#    unanswered_bursts_indices = [b['indices'] for b in unans_bursts]
#    answered_bursts_indices = [b['indices'] for b in ans_bursts]
    # Inter Arrival times for unanswered bursts
    if len(ans_bursts) + len(unans_bursts) < 2:
        return None
    IBT = []
    # Check whether you start with a partial period or not
    # If you do, the index of ans_bursts will be that of unans_bursts + 1, inside the same period
    # If you filtered first and last periods before doing this, the index will always be the same
    first_unans_probe = unans_bursts[0]['burst'][0]
    first_ans_probe = ans_bursts[0]['burst'][0]
     #Between ans and unans bursts, for any given period
    if period_starts_with_ans:
        unans_index_offset = 0
        if first_ans_probe['probe']['timestamp'] > first_unans_probe['probe']['timestamp']:
            unans_index_offset = 1
        smaller_len = min(len(ans_bursts), len(unans_bursts))
        for i in xrange(smaller_len): # because you want to avoid any IndexErrors
            first_ans_probe = ans_bursts[i]['burst'][0]
            logging.info("\tfirst probe: %s" % ans_bursts[i]['indices'][0])
            if i < smaller_len - 1:
                next_ans_burst_first_probe = ans_bursts[i+1]['burst'][0]
                logging.info("\tfirst probe of next burst: %s" % ans_bursts[i+1]['indices'][0])
            else:
                next_ans_burst_first_probe = removed_last[0]['burst'][0]
                logging.info("\tlast probe (rm): %s" % removed_last[0]['indices'][0])
            ibt = next_ans_burst_first_probe['probe']['timestamp'] - first_ans_probe['probe']['timestamp']
            logging.info("\t\t---> ibt = %s" % ibt)
            IBT.append(ibt)
    else:   
        ans_index_offset = 0
        if first_unans_probe['probe']['timestamp'] > first_ans_probe['probe']['timestamp']:
            ans_index_offset = 1
        smaller_len = min(len(ans_bursts), len(unans_bursts))
        for i in xrange(smaller_len): # because you want to avoid any IndexErrors
            first_unans_probe = unans_bursts[i]['burst'][0]
            logging.info("\tfirst probe: %s" % unans_bursts[i]['indices'][0])
            last_ans_probe = ans_bursts[i+ans_index_offset]['burst'][-1]
            logging.info("\tlast probe: %s" % ans_bursts[i+ans_index_offset]['indices'][-1])
            ibt = last_ans_probe['probe']['timestamp'] - first_unans_probe['probe']['timestamp']
            logging.info("\t\t---> ibt = %s" % ibt)
            IBT.append(ibt)
    #if all probes have been answered or none has, let's define a period as the length of the experiment
    # otherwise IBT would be empty and its variation would be nan
    if not IBT:
        IBT.append(full_timeseries[-1]['probe']['timestamp'] - full_timeseries[0]['probe']['timestamp'])
        logging.info('\tImposing IBT = %s' % IBT)
    logging.info('\t-> periods: %s' % IBT)
    return IBT



def get_bursts_and_IBT_variation(answered_bursts, unanswered_bursts, IBT):
    answered_bursts_variation = scipy.stats.variation([burst['size'] for burst in answered_bursts])
    unanswered_bursts_variation = scipy.stats.variation([burst['size'] for burst in unanswered_bursts])
    IBT_variation = scipy.stats.variation(IBT)
    logging.info('\t=> burst variation: %s, periods variation: %s' % (
                                unanswered_burst_variation, IBT_variation))
    return answered_burst_variation, unanswered_burst_variation, IBT_variation


def extract_available_burst_defs(trace_info):
    """
    Given a trace_info structure, it returns all the burst variants used in the analysis
    """
    burst_defs_available = [k.split('IBT_variation')[1] for k in trace_info.keys()
                        if 'IBT_variation' in k]
    burst_defs_available = [b for b in burst_defs_available if b]
    burst_defs_available = sorted(list(set(burst_defs_available)),
                                key=lambda x: (int(x.split('_gaps_')[-1])))
    return burst_defs_available



def verify_actually_sent_probes(trace_info):
    if trace_info['initial_probes_num'] != len(trace_info['probes_timestamps']):
        logging.info('\t- wanted to send %s packets, but only captured %s probes'
                '' % (trace_info['initial_probes_num'],
                    len(trace_info['probes_timestamps'])))
    return


def remove_nonessential_data(trace_info):
    variants = extract_available_burst_defs(trace_info)
    # for campaign 2 you also have an extra definition: "" . For next campaigns, 
    # it will be replaced by gaps_0
    if 'ans_bursts' in trace_info.keys():
        variants.append('')
    # fields to remove completely
    fields_to_remove = ['full_timeseries',
                         'replies_timestamps',
                         'probes_interpacket_series',
                         'timeseries',
                         'replies_interpacket_series',
                         'probes_timestamps']
    for v in variants:
        fields_to_remove.append('IBT' + v)
    for k in fields_to_remove:
        if k in trace_info:
            trace_info.pop(k, None)
    # fields to reduce
    fields_to_reduce = ['ans_bursts', 'filtered_ans_bursts', 'unans_bursts',
                        'filtered_unans_bursts']
    fields_to_reduce = [f + v for f in fields_to_reduce for v in variants]
    more_fields_to_reduce = []
    burst_fields = ['indices', 'timestamps', 'burst', 'rtts', 'inter_packet_times']
    for k in fields_to_reduce:
        for burst in trace_info[k]:
            for bf in burst_fields:
                if bf in burst:
                    burst.pop(bf)
    return trace_info


def load_trace(trace_filepath):
    trace = rdpcap(trace_filepath)
    return trace        


def process_pcap_trace(filepath, verbose=False, gaps=4):
    replies_icmp_type = 11
    # if file is empty, continue to next one
    if not os.path.getsize(filepath):
        logging.warning("\t empty pcap file! What happened?")
        return None
    trace_info = get_experiment_input_info_from_filename(os.path.basename(filepath))          
    #load pcap file
    trace = load_trace(filepath)
    if not trace: #file is empty
        logging.warning("=>>>>>> EMPTY pcap file found!!!!! <<<<<<<<")
        return None
    # analyze trace
    logging.info('\t - retrieving data: started')
    post_info = get_experiment_post_data(trace, probes_protocol=trace_info['protocol'],
                                        replies_icmp_type=replies_icmp_type,
                                        ttl=trace_info['ttl'], gaps=gaps)
    if not post_info:
        return None
    trace_info = dict(trace_info.items() + post_info.items())
    verify_actually_sent_probes(trace_info)
    logging.info("\t- wanted rate: %s, measured rate: %s; duration: %.2f" % (
                                                        trace_info['expected_rate'],
                                                        trace_info['actual_rate'],
                                                        trace_info['actual_duration']))
    logging.info("\t- answering rate: %s" % trace_info['answering_rate'])
    trace_info = remove_nonessential_data(trace_info)
    return trace_info
    
    
    

def process_pcap_traces_in_folder(traces_parent_folder, gaps=4):
    """Given a folder with pcap traces created by the probing experiment,
    it processes them and returns the details of each experiment
    
    Args:
        traces_parent_folder: folder with pcap traces to analyze
        
    Returns:
        experiment details for each trace in the input folder

    """
    trace_info_list = []
    subfolders = [el for el in os.walk(traces_parent_folder)]
    #traverse subfolders, take traces and analyze them
    for root, dirs, files in subfolders[1:]:
        if files:
            files = sort_list_of_trace_filepaths(files)
        for filename in files:
            if not filename.startswith('trace'):
                continue
            filepath = os.path.join(root, filename)
            logging.info('---------------------------------------------------------')
            logging.info(filepath)
            trace_info = process_pcap_trace(filepath, gaps=gaps)
            if trace_info is None:
                continue
            trace_info_list.append(trace_info)
    trace_info_list = add_median_rates_to_traces(trace_info_list)
    return trace_info_list
    
    
def process_pcap_traces(pcap_traces_paths, gaps=4):
    """Given a list of paths of pcap traces created by the probing experiment,
    it processes them and returns the details of each experiment
    
    Args:
        traces_parent_folder: folder with pcap traces to analyze
        
    Returns:
        experiment details for each trace in the input folder

    """
    trace_info_list = []
    #traverse subfolders, take traces and analyze them
    for trace_path in pcap_traces_paths:
        trace_info = process_pcap_trace(trace_path, gaps=gaps)
        if trace_info is None:
            continue
        trace_info_list.append(trace_info)
    return trace_info_list


def load_processed_traces(results_parent_folder):
    #Here I assume the folder hierarchy is:
    # results_parent_folder/host_parent_folder/traces_files
    subfolders = [el for el in os.walk(results_parent_folder)]
    all_analyzed_traces = []
    for root, dirs, files in subfolders[1:]:
        for filename in files:
            filepath = os.path.join(root, filename)
            #TODO here you could look for specific files starting with a pattern ('processed' etc)
            all_analyzed_traces.append(pickle.load(open(filepath, "rb" )))
    return all_analyzed_traces


def add_median_rates_to_traces(all_analyzed_traces):
    all_analyzed_traces = sorted(all_analyzed_traces,
                                key=lambda a_trace: (a_trace['hostname'],
                                                    int(a_trace['ttl']),
                                                    int(a_trace['run']),
                                                    int(a_trace['expected_rate'])))
    expected_rates = sorted(list(set([trace['expected_rate'] for trace in all_analyzed_traces])))
    median_rates = []
    for r in expected_rates:
        actual_rates_at_rate_r = [t['actual_rate'] for t in all_analyzed_traces
                                                    if t['expected_rate'] == r]
        median_actual_rate = int(np.median(actual_rates_at_rate_r))
        median_rates.append(median_actual_rate)
    for t in all_analyzed_traces:
        t['rounded_up_rate'] = round_up_value_to_closest_in_a_list(t['actual_rate'], median_rates)
    return all_analyzed_traces


def analyze_traces(processed_traces, gaps=4, verbose=False, fp_dict=None):
    burst_def = get_corresponding_burst_def(processed_traces[0], gaps)
    routers_by_ttl = classify_all_routers(processed_traces, v=burst_def, verbose=verbose, fp_dict=fp_dict)
    return routers_by_ttl


def get_corresponding_burst_def(a_trace, gaps=4):
    burst_defs_available = extract_available_burst_defs(a_trace)
    if '_gaps_' + str(gaps) in burst_defs_available:
        burst_def = '_gaps_' + str(gaps)
    else:
        logging.info("results with tolerated gaps of %s answered probes not found" % gaps)
        return
    return burst_def


def create_icmp_analysis_parser():
    parser = argparse.ArgumentParser(description="Analyze traces")
    parser = add_icmp_analysis_parser(parser)
    return parser


def add_icmp_analysis_parser(parser, hide_args=False):
    """Given an argparse parser, it adds all the arguments needed for the experiment
    analysis.
    
    Args:
        parser: an argparse parser
    Returns:
        a parser with arguments for the analysis
    
    """
    parser.add_argument("results_folder", type=str, help="Path to the folder with the pcap traces")
    parser.add_argument("--verbose", action="store_true",
                        help="verbose text output")
    return parser
    
    
def parse_args(use_given_args=False, given_args=None):
    parser = create_icmp_analysis_parser()
    if use_given_args:
        args = parser.parse_args(given_args)
    else:
        args = parser.parse_args()
    return args


def main_analysis(args):
    global verbose
    verbose = True
    global allowed_noise
    allowed_noise = 0.0
    gaps = 4
    traces_parent_folder = args.results_folder.rstrip('/')
    all_analyzed_traces = process_pcap_traces_in_folder(traces_parent_folder, gaps=gaps)
    analyze_traces(all_analyzed_traces)
    return


if __name__ == '__main__':
    #collect command line arguments
    args = parse_args()
    status = main_analysis(args)
    sys.exit(status)
