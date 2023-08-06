===========
Icmp Tool
===========

Icmp Tool provides a straight-forward way to characterize the responsiveness to TTL-limited probes of routers close to you.
The tool is based on code we used for a large scale campaign on PlanetLab. For details on how the router classification works,
refer to our paper "Characterizing ICMP Rate Limitation on Routers": http://goo.gl/cU004b
Typical usage looks like this::

    #!/usr/bin/env python

    from icmptool import icmptool

    routers_by_hop = icmptool(dest='8.8.8.8', ttls=[1,2,3], min_rate=1, max_rate=500, n_of_rates=5, duration=8)
    for hop in routers_by_hop:
        for router in routers_by_hop[hop]:
            print "router %s at hop %s is of type %s for the tested probing rates" % (
                                                    router, hop, routers_by_hop[hop][router]['rtype_description'])
            if 'fr-onoff' in routers_by_hop[hop][router]['rtype_str']:
                print("\tOn-off parameters are:\n\t\tBurst Size: "
                      "%s packets\n\t\tInter Burst Time: %s seconds"
                      "\n\t\t=> max answering rate %d pps " % (routers_by_hop[hop][router]['onoff_parameters']['bsize'],
                                                               routers_by_hop[hop][router]['onoff_parameters']['iat'],
                                                               routers_by_hop[hop][router]['onoff_parameters']['bsize']))
            elif 'fr-rl' in routers_by_hop[hop][router]['rtype_str']: #generically rate-limited
                print "\tMaximum answering rate is %s" % routers_by_hop[hop][router]['extra_info']['limited_ans_rate']


By doing that, we probed routers at hops 1, 2, 3 on the path to 8.8.8.8, at 5 exponentially-spaced probing rates between 1 pps and 500 pps, for 8 seconds each time.
routers_by_hop will now contain at key i details of the responsiveness of the router on hop i.

Alternatively, the script icmp_tool.py can be called from the shell to perform the same task. The above example simply becomes::

    $ ./icmp_tool.py --dest 8.8.8.8 --ttls 1 2 3 --min_rate 1 --max_rate 500 --n_of_rates 5 --duration 8
    
Icmp Tool sends TTL-limited probes at constant rate(s) to the routers at the specified hops
and by studying the timeseries of the received ICMP time-exceeded replies 
it determines the responsiveness of nearby routers to these probes. A responsive router typically 
shows 3 responsiveness phases in the following order::

    [fully-responsive]  [rate-limited] [irregular]

Depending on the chosen probing rates and on the configuration of the router,
not all phases might appear. The most common implementation
of rate limitation is with an on-off pattern, of which we provide the parameters:
burst size, period length and resulting answering rate. In some cases,
rate limitation is implemented with a maximum constant answering rate, but no such
pattern is observable. We call this a generically rate-limited router (rl).
The irregular phase, if any, might appear whether or not rate limitation has been configured.
After a certain threshold, the responsiveness of the router might simply not follow (any more) any pattern
and become less predictable.

The tool uses **tcpdump** to capture outgoing probes and incoming replies. It requires **sudo** privileges.
