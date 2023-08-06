#!/usr/bin/env python

import argparse
import collections
import logging # line below suppresses "No route found for IPv6 destination" warning from scapy
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)
import os
import pickle
import socket
import sys
import time
import signal
import subprocess


from scapy.all import *


conf.L3socket=L3RawSocket


class icmp_type:
    echo_request = 8
    echo_reply = 0
    time_exceeded = 11

possible_ttls=[32, 64, 128, 255]
# Possible traces:
# ICMP echo-requests & echo-replies
# ICMP echo-requests with forged TTL
# TCP SYN triggering TCP RST
# TCP SYN with forged TTL
# UDP (not for now)
            

def create_trace_filename(protocol, n_of_packets, duration, ttl, rate, payload_size, run, prefix=''):
    """Given the probing parameters of the experiment, it returns a string to be used
    as the filename of a pcap trace.
    
    """
    return '%strace_%s_probes_%s_duration_%s_ttl_%s_rate_%s_payload_%s_run_%s.pcap' % (prefix, protocol,
                                                n_of_packets, duration, ttl, rate, payload_size, run)


def get_my_address2(interface): #interface not necessary, but compatible with the second version below
    """Returns IP address of the local machine by initiating a TCP connection to
    google http server. Careful, in this approach the interface is the default
    one in the system.
    
    
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("www.google.com", 80))
    my_address = (s.getsockname()[0])
    s.close()
    return my_address
    
    
#use this version if you have no access to the internet (isolated setup)
def get_my_address(interface):
    """Given a network interface, it returns the IP address associated to it.
    Args:
        interface: network interface name
    Returns:
        IP address of the input interface
    
    """
    import netifaces
    if interface not in netifaces.interfaces():
        return ''
    else:
        # choose IPv4 (AF_INET)
        return netifaces.ifaddresses(interface)[netifaces.AF_INET][0]['addr']
        
    
def send_a_trace_and_dump_traffic(protocol, n_of_packets, rate, ttl, dest_addr,
                                  payload_size, duration, run=0, traces_folder='',
                                  interface='eth0', verbose=False, prefix=''):
    """It sends probes to the router at the given hop, dumps the trace containing
    probes and ICMP replies and returns the filename of this trace.
    
    Args:
        protocol: protocol of the probes. Choise is between icmp, tcp and udp. 
                  Specify ping to use the ping tool directly.
        n_of_packets: number of probes to send
        rate: probing rate, in packets per second
        ttl: hop to test
        dest_addr: IP destination of the probes
        payload_size: payload size for the probes
        run: number of the current run, just to create corresponding trace filename
        traces_folder: name of the folder where to store the traces
        interface: network interface, default is eth0
        verbose: if True, it prints the number of packets sent and trace location
    Returns:
        filename of the trace
    
    """
    # ********************************************
    # 0. set tcpdump filters and other parameters
    # ********************************************
    my_address = get_my_address(interface)
    addr_dict = {'dest': dest_addr, 'me': my_address}
    if protocol == 'icmp' or protocol == 'ping':
        bpf_filter = 'icmp and host %(me)s' % addr_dict
    elif protocol == 'udp':
        bpf_filter = ('(udp and dst %(dest)s and src %(me)s and ip[8] < 20 ) or '
                     ' (icmp and dst %(me)s )' % addr_dict)
    elif protocol == 'tcp' and ttl < 64: #even a lower value
        bpf_filter = '(tcp and dst %(dest)s and src %(me)s and ip[8] < 20 ) or (icmp and dst %(me)s )' % addr_dict
    elif protocol == 'tcp' and ttl >= 64:
        bpf_filter = 'tcp and host %(me)s and host %(dest)s' % addr_dict
    probes_spacing = 1.0 / rate
    #############################################################################
    # 1. run tcpdump
    #############################################################################
    # IMPORTANT: make all traces end with '.pcap', because that's how I find them later with NEPI
    dumped_packets_file = create_trace_filename(protocol, n_of_packets, duration,
                                                ttl, rate, payload_size, run, prefix=prefix)
    if traces_folder:
        if not os.path.exists(traces_folder):
            os.makedirs(traces_folder) #parent results folder
        if not os.path.exists(os.path.join(traces_folder, my_address)):
            os.makedirs(os.path.join(traces_folder, my_address)) #parent results folder
        dumped_packets_file = os.path.join(traces_folder, my_address, dumped_packets_file)
        
    # I need full UDP probes in order to recompute the checksum when matching them
    if protocol != 'udp':
        tcpdump_process = subprocess.Popen(['sudo', '/usr/sbin/tcpdump',
                        '-w', dumped_packets_file,
                        '-n', '-s', '96', '-i', interface,
                        bpf_filter],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE)
    else:
        tcpdump_process = subprocess.Popen(['sudo', '/usr/sbin/tcpdump',
                        '-w', dumped_packets_file,
                        '-n',  '-i', interface, bpf_filter],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE)
                        
    #############################################################################
    # 2. send packets depending on the probes' protocol
    #############################################################################
    if protocol.lower() == 'ping':
        ping_command = "sudo ping -i %s -c %s -t %s %s" % (1.0 / rate, n_of_packets, ttl, dest_addr)

        ping_process = subprocess.Popen(ping_command.split(),
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
        ping_process.communicate()
        print '\t\t- ', ping_command
        
    elif protocol.lower() == 'icmp':
        #create UDP socket and send messages
        #icmp_id = random.randint(0, 65535)
        s_icmp = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
        val_max = 65535 # 8 bits
        if n_of_packets > val_max:
            icmp_id_list = [val / (val_max+1) for val in range(val_max+1, n_of_packets)] + [0]
        else:
	        icmp_id_list = [0]
        icmp_id_list = list(set(icmp_id_list))
        for icmp_id in icmp_id_list:
            s_icmp.bind(('', icmp_id))
        # By default, packets sent on a raw socket include the TCP/UDP/ICMP header but not the IP header. 
        # To send packets that include the IP header, the IP_HDRINCL socket option must be set on the socket. 
        # This call will succeed only after a successful bind:
        s_icmp.setsockopt(socket.SOL_IP, socket.IP_HDRINCL, 1) #IMPORTANT!
        icmp_packets = []
        # create n_of_packets echo requests
        for i in range(n_of_packets):
            if i > val_max:
                icmp_id = i / (val_max+1)
            else:
                icmp_id = 0
            p = IP(dst=dest_addr, ttl=ttl) / ICMP(type="echo-request", id=icmp_id, seq=i%(val_max+1)) / os.urandom(payload_size)
            #transform all packets to strings b2174efore sending them them through a socket
            icmp_packets.append([str(p[IP]), icmp_id])
        c = 0
        for p in icmp_packets:
            sent_bytes = s_icmp.sendto(p[0], (dest_addr, p[1]))
            if sent_bytes:
                c += 1
            time.sleep(probes_spacing)
        s_icmp.close()
        logging.info("\t\t- %s ICMP packets sent" % c)
        
    elif protocol.lower() == 'tcp':
        tcp_local_port = random.randint(1025, 65535)
        tcp_dest_port = random.randint(1025, 65535)
        s_tcp = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
        s_tcp.bind(('', tcp_local_port))
        s_tcp.setsockopt(socket.SOL_IP, socket.IP_HDRINCL, 1) #IMPORTANT!
        tcp_packets = []
        seq_val = 0
        for i in range(n_of_packets):
            p = IP(ttl=ttl, dst=dest_addr) / TCP(sport=tcp_local_port, dport=tcp_dest_port, seq=seq_val + i) / os.urandom(payload_size)
            p = p.__class__(str(p))
            tcp_packets.append(str(p[IP]))
        c = 0
        for p in tcp_packets:
            sent_bytes = s_tcp.sendto(p, (dest_addr, tcp_dest_port))
            if sent_bytes:
                c += 1
            time.sleep(probes_spacing) #No problem here when sending bursts of messages. I receive all replies
        s_tcp.close()
        logging.info("\t\t- %s TCP packets sent" % c)
        
    elif protocol.lower() == 'udp':
        udp_local_port = random.randint(1025, 65535)
        udp_dest_port = random.randint(1025, 65535)
        s_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        s_udp.bind(('', udp_local_port))
        s_udp.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, ttl)
        udp_packets = [] #actually only udp payloads
        for i in range(n_of_packets):
            counter_str = str(i) + '_'
            additional_payload = ''
            if payload_size:
                additional_payload = os.urandom(payload_size - len(counter_str))
            udp_packets.append(counter_str + additional_payload)
        c = 0
        for p in udp_packets:
            # probe ID is inside the UPD payload 
            sent_bytes = s_udp.sendto(p, (dest_addr, udp_dest_port))
            if sent_bytes:
                c += 1
            time.sleep(probes_spacing)
        s_udp.close()
        logging.info("\t\t- %s UDP packets sent" % c)
            
    #############################################################################
    # 3. kill tcpdump
    #############################################################################
    time.sleep(5) #Initially I put 3 seconds here, use 3 minutes for 'slow' routers
    os.kill(tcpdump_process.pid, signal.SIGTERM)
    tcpdump_out, tcpdump_err =  tcpdump_process.communicate()
    tcpdump_returncode = tcpdump_process.returncode
    if tcpdump_returncode: # if non-zero
        print tcpdump_out
        print tcpdump_err
    time.sleep(0.5)
    logging.info("\t\t-> packets saved on %s" % dumped_packets_file)
    return dumped_packets_file


def create_prober_parser():
    """Creates an argparse parser for the probing experiment.
    
    Returns:
        Parser
    """
    parser = argparse.ArgumentParser(description="Send probes")
    parser = add_prober_parser(parser)
    return parser
    
    
def add_prober_parser(parser):
    """ Given an argparse parser, it adds the arguments necessary for probing experiment. 
    
    Args:
        parser: argparse parser
    Returns:
        parser with added arguments
    """
    parser.add_argument("--ttls", nargs='+', type=int, help="TTLs to target. "
                        "Default is 1.",default=[1])
    parser.add_argument("-d", "--duration", type=float, help="Length of the experiment "
                        "in seconds. Default is 1.", default=1.0)
    parser.add_argument("--runs", type=int, help="Number of runs. Default is 1.", default=1)
    parser.add_argument("--rate_min", type=int, help="minimum rate in pps. Default is 100.", default=100)
    parser.add_argument("--rate_max", type=int, help="maximum rate in pps. Default is 500.", default=500)
    parser.add_argument("--n_of_rates", type=int, help="Number of exponentially-spaced rates to choose from "
                        "the range [rate_min, rate_max] . Default is 1: only rate_min.", default=1)
    parser.add_argument("-p", "--protocols", type=str, default=['icmp'], nargs='+',
                        help="Protocol(s) to use for the probes. Choice is between icmp, "
                        "ping (use directly ping utility), tcp and udp.",
                        choices=['icmp', 'ping', 'tcp', 'udp']
                        )
    parser.add_argument("--payload_sizes", nargs='+', type=int,
                        help="Sizes of (randomly choseen) probes payload."
                        "Default is 0", default=[0])
    parser.add_argument("--dest", type=str, help="Destination of the probes. "
                        "Default is 8.8.8.8.", 
                        default="8.8.8.8")
    parser.add_argument("--dest_IP", type=str, help="IP address destination of the probes (avoid reverse DNS).")                        
    parser.add_argument("-i", "--interface", type=str, help="Network interface to use."
                        " Default is eth0.", default='eth0')
    parser.add_argument("--fingerprint", action="store_true",
                        help="fingerprint routers found at the specified ttls.")

    return parser
    
    
def process_parameters(args):
    """Given a parsed parser, it stores the values in a dictionary. 
    
    Args:
        args: parsed args from an argparse parser instance
    Returns:
        dictionary with the experiment parameters
    
    """

    duration = args.duration #seconds
    runs = args.runs
    ttls = args.ttls
    n_of_rates = args.n_of_rates
    rate_min = args.rate_min
    rate_max = args.rate_max
    protocols = args.protocols
    destination = args.dest 
    payload_sizes = args.payload_sizes #[0]
    interface = args.interface
    dest_IP = args.dest_IP
    exp_parameters = {'duration': duration, 'runs': runs, 'ttls': ttls,
                      'n_of_rates': n_of_rates,
                      'rate_min': rate_min, 'rate_max': rate_max, 'protocols': protocols,
                      'dest': destination, 'payload_sizes': payload_sizes,
                      'interface': interface, 'dest_IP': dest_IP,
                      'fingerprint': args.fingerprint}
    return exp_parameters
        

def main(probing_parameters):
    if probing_parameters['fingerprint']:
        return fingerprint_tool(**probing_parameters)
    else:
        return probing_tool(**probing_parameters)


def closest_value_in_list(value, a_list):
    """Given a value and a list of values, it returns the element in the list that
    is the closest to the input value.
    """
    return min(a_list, key=lambda x: abs(x - value)) #key is the ordering function


def separate_probes_from_replies(trace_path, reply_type=icmp_type.echo_reply):
    """Given the path of a packet trace containing probes and corresponding ICMP replies,
    it loads the trace and separates probes from replies.
    
    Args:
        trace_path: filepath of the packet trace
        reply_type: icmp type of the expected responses. Default is echo_reply. 
    
    Returns:
        list of probes, list of replies
    
    """
    trace = rdpcap(trace_path)
    probes = [i for i in trace if ICMP in i and i[ICMP].type==icmp_type.echo_request]
    replies = [i for i in trace if ICMP in i and i[ICMP].type==reply_type]
    return probes, replies
    
    
def get_time_exceeded_ttl(ttl, dest='8.8.8.8', fingerprint_folder='fingerprint', interface='eth0'):
    """Given a TTL value and an IP destination, it probes for 6 seconds at 1pps the router(s) 
    at that hop with TTL-limited ICMP probes in order to obtain the TTL value of the replies.
    If different router IPs or different TTL values are observed, there probably is 
    a load balancer generating more than one path to this hop and no value is returned.
    
    Args:
        ttl: ttl-value of the probes that will be sent. Put differently, the hop to test.
        dest: destination for the probes to send. IP address or name. Default is 8.8.8.8.
        fingerprint_folder: path of the folder where to store the traces. Default is 'fingerprint'.
        interface: name of the network interface to use. Default is eth0.
    Returns:
        TTL value of the replies, IP address of the responding router
    
    """
    # send 6 ttl-limited pings at 1pps
    trace_path = probing_tool(duration=6.0, runs=1, ttls=[ttl], n_of_rates=1, rate_min=1, 
                                protocols=['icmp'], dest=dest, traces_folder='fingerprint',
                                fingerprint=True, interface=interface, prefix='fp')[0]
    probes, replies = separate_probes_from_replies(trace_path, reply_type=icmp_type.time_exceeded)
    if probes == -1:
        return -1, None #no trace
    if not replies:
        return -2, None #no replies
    replies_sources = list(set([i[IP].src for i in replies]))
    if len(replies_sources) > 1:
        #path to same destination diverges!! load balancer! nothing to do
        return -3, None #load balancer
    target_router = replies_sources[0] #IP
    replies_ttl = list(set([i[IP].ttl for i in replies]))
    if len(replies_ttl) > 1:
        logging.info("two paths of different length(%s) to the same hop." % replies_ttl)
        return -4, target_router #load balancer2
    #all replies have the same IP source
    time_exceeded_ttl = replies_ttl[0]
    return time_exceeded_ttl, target_router
    
    
def get_echo_reply_original_ttl(target_router, fingerprint_folder='fingerprint', interface='eth0'):
    """Given an IP destination, it probes for 6 seconds at 1pps the destination
    with ICMP echo request probes in order to obtain the TTL value of the replies.
    If different IPs or different TTL values are observed, there probably is 
    a load balancer generating more than one path to this destination and no value is returned.
    
    Args:
        dest: destination for the ICMP echo-request probes. Provide IP address or name.
        fingerprint_folder: path of the folder where to store the traces. Default is 'fingerprint'.
        interface: name of the network interface to use. Default is eth0.
    Returns:
        TTL value of the echo-request replies
    """

    trace_path = probing_tool(duration=6.0, runs=1, ttls=[64], n_of_rates=1, rate_min=1, 
                            protocols=['icmp'], dest=target_router, 
                            traces_folder=fingerprint_folder, fingerprint=True, interface=interface, prefix='fp_')[0]
    probes, replies = separate_probes_from_replies(trace_path, reply_type=icmp_type.echo_reply)
    if probes == -1:
        logging.info("no trace for ping probes")
        return -1 #no trace
    if not replies:
        return -2 #no replies
    replies_sources = list(set([i[IP].src for i in replies]))
    if len(replies_sources) > 1:
        #path to same destination diverges!! load balancer! nothing to do
        return -3 #load balancer
    replies_ttl = list(set([i[IP].ttl for i in replies]))
    if len(replies_ttl) > 1:
        logging.info("two paths of different length(%s) to the same hop." % replies_ttl)
        return -4 #load_balancer2
    #all replies have the same IP source
    ping_ttl = replies_ttl[0]
    return ping_ttl
        
        
def get_fingerprint_signature(ttl, dest='8.8.8.8',
                             fingerprint_folder='fingerprint', interface='eth0'):
    """Given a TTL (hop to test) and a destination, it probes the router(s) at the 
    specified hop in order to fingerprint it. It sends a TTL-limited and echo-reply probes
    and returns the TTL value of the responses.
    
    Args:
        ttl: hop to test
        dest: destination for the probes. IP address or name. Default is '8.8.8.8'.
        fingerprint_folder: folder where to store the traces.
        interface: name of the network interface to use. Default is eth0.
    Returns:
        a 2-element tuple containing the TTL signature of the node in the form
        (time_exceeded_ttl, ping_ttl) and a dictionary with details about the
        router (address and errors, if there are any)
    
    
    """
    ########################################################################
    # step 1. sent ttl-limited probes and record the ttl value of the reply#
    ########################################################################
    hop_info = {}
    time_exceeded_ttl, target_router = get_time_exceeded_ttl(ttl, dest=dest, 
                                            fingerprint_folder=fingerprint_folder,
                                            interface=interface)
    hop_info['router'] = target_router
    # deal with errors
    if time_exceeded_ttl < 0:
        if time_exceeded_ttl == -1:
            logging.warning("no trace for ttl-limited probes")
            err = 'err'
        elif time_exceeded_ttl == -2:
            err = 'no_traceroute'
        elif time_exceeded_ttl == -3:
            err = 'load_balancer'
        elif time_exceeded_ttl == -4:
            err = 'load_balancer2'
        hop_info['error'] = err
        return (-1,), hop_info
    hop_info['time_exceeded_ttl'] = time_exceeded_ttl
    # -1 because ttl is decremented before the packet is forwarded
    # e.g. if the reply was sent from hop 1, the ttl is not decremented
    original_time_exceeded_ttl = closest_value_in_list(time_exceeded_ttl + ttl - 1, possible_ttls)
    #############################################
    # step 2. PING the router found above
    #############################################
    echo_reply_ttl = get_echo_reply_original_ttl(target_router, fingerprint_folder=fingerprint_folder,
                                                 interface=interface)
    # deal with errors
    if echo_reply_ttl < 0:
        if echo_reply_ttl == -1:
            logging.info("no trace for ping probes")
            err = 'error'
        elif echo_reply_ttl == -2:
            err = 'no_ping'
        elif echo_reply_ttl == -3:
            err = 'load_balancer_ping'
        elif echo_reply_ttl == -4:
            err = 'load_balancer2_ping'
        hop_info['error'] = err
        return (original_time_exceeded_ttl, -1), hop_info
    hop_info['echo_reply_ttl'] = echo_reply_ttl
    # -1 because ttl is decremented before the packet is forwarded
    # e.g. if the reply was sent from hop 1, the ttl is not decremented
    original_echo_reply_ttl = closest_value_in_list(echo_reply_ttl + ttl - 1, possible_ttls)
    return (original_time_exceeded_ttl, original_echo_reply_ttl), hop_info
        
        
def fingerprint_tool(ttls=[1], dest='8.8.8.8', interface='eth0',
                     **extras):
    """Given a list of hops, an IP destination and an interface to use, it fingerprints
       the routers encountered at each hop.
       Based on http://orbi.ulg.ac.be/bitstream/2268/154575/1/imc055-vanaubel.pdf
       
    Args:
        ttls: list of hops to test. Default is [1].
        dest: destination for the probes. IP address or name. Default is '8.8.8.8'.
        interface: network interface to use. Default is 'eth0'.
    Returns:
        dictionary with fingerprinting results stored by hop number.
    
    """
    fingerprint_folder = 'fingerprint'
    
    signatures = { (255, 255): 'cisco',
                    (255, None): 'undefined',
                    (255, 64): 'juniper_junos',
                    (64, 64): 'linux_and_others',
                    (64, None): 'undefined',
                    (128, 128): 'juniper_junosE',
                    (128, None): 'undefined'   
                 }
    signatures = collections.defaultdict(lambda: 'not_found', signatures)
    #treat each hop separately
    hops = {}
    for ttl in ttls:
        hops[ttl] = {'ping_trace': None,
                     'time_exceeded_ttl': None,
                     'echo_reply_ttl': None,
                     'signature': None,
                     'original_time_exceeded_ttl': None,
                     'original_echo_reply_ttl': None,
                     'router': None,
                     'router_brand': None
                    }
        print "- Fingerprinting router at hop %s..." % ttl
        router_sign, info = get_fingerprint_signature(ttl, dest=dest, fingerprint_folder=fingerprint_folder, 
                                                      interface=interface)
        hops[ttl]['signature'] = router_sign
        if 'router' in info:
            hops[ttl]['router'] = info['router']
        if 'time_exceeded_ttl' in info:
            hops[ttl]['time_exceeded_ttl'] = info['time_exceeded_ttl']
        if 'echo_reply_ttl' in info:
            hops[ttl]['echo_reply_ttl'] = info['echo_reply_ttl']
        if 'error' in info:
            hops[ttl]['router_brand'] = hops[ttl]['error'] = info['error']
        else:
            hops[ttl]['router_brand'] = signatures[router_sign]
        print "\t- <time-exceeded ttl: %s; echo-reply ttl: %s>" % (hops[ttl]['time_exceeded_ttl'], hops[ttl]['echo_reply_ttl'])
        print '\t=> ', info['router'], router_sign, hops[ttl]['router_brand']
    
    #now pack everything into a dictionary with the hostname and pickle it
    routers = {}
    for h in hops:
        if 'router' in hops[h] and hops[h]['router'] is not None:
            r = hops[h]['router']
            routers[r] = {'pl_host': socket.gethostname(),
                          'hop': h,
                          'signature': hops[h]['signature'],
                          'time_exceeded_ttl': hops[h]['time_exceeded_ttl'],
                          'echo_reply_ttl': hops[h]['echo_reply_ttl'],
                          'router_brand': hops[h]['router_brand']}
            routers[r]['error'] = hops[h]['error'] if 'error' in hops[h] else None
    if False:
        filename = 'fingerprint_' + socket.gethostname() + '.pickle'
        pickle.dump(routers, open(os.path.join(fingerprint_folder, filename), 'w'))
        print '\t- saved in %s' % os.path.join(fingerprint_folder, filename)
    return hops, routers
    
    
    
def probing_tool(duration=10.0, runs=1, ttls=[1], n_of_rates=1, rate_min=100, rate_max=500,
                protocols=['icmp'], dest='8.8.8.8', dest_IP='', payload_sizes=[0],
                traces_folder='', interface='eth0', verbose=False, fingerprint=False, 
                prefix='', **extras):
    
    if not dest_IP:
        dest_IP = socket.gethostbyname(dest)
    if n_of_rates == 1:
        rates=[rate_min]
    else:
        gamma = (rate_max / float(rate_min)) ** (1.0 / (n_of_rates-1))
        rates = [int(rate_min * gamma**i) for i in range(n_of_rates)]
#        rates.append(1)
#        rates.append(20)
    traces_paths = {}
    random.shuffle(rates)
    random.shuffle(ttls)
    if fingerprint or True:
        traces_location = []
    for a_protocol in protocols:
        for run in range(runs):
            for a_rate in rates:
                #fixed experiment duration: 'duration' seconds. Number of packets will depend on this
                n_of_packets = int(a_rate * duration)
                for p_size in payload_sizes:
                    for attl in ttls:
                        print ("\t+ Sending %s %s probes with ttl=%s and payload_size=%s "
                                "at %s pps [run %s]" % (n_of_packets, a_protocol,
                                                        attl, p_size, a_rate, run))
                        trace_path = send_a_trace_and_dump_traffic(a_protocol, n_of_packets, a_rate,
                                                        attl, dest_IP, p_size,
                                                        duration, run, traces_folder=traces_folder,
                                                        verbose=verbose, interface=interface,
                                                        prefix=prefix)
                        if fingerprint or True:
                            traces_location.append(trace_path)
                        time.sleep(3)
    if fingerprint:
        return traces_location   
    logging.info(traces_location)
    return traces_location 


if __name__ == '__main__':
    parser = create_prober_parser()
    args = parser.parse_args()
    probing_parameters = process_parameters(args)
    probing_parameters['verbose'] = True
    status = main(probing_parameters)
    sys.exit(status)
