===========
Icmp Tool
===========

Icmp Tool provides a straight-forward way to characterize the responsiveness of routers close to you to TTL-limited probes.
The tool is based on code we used for a large scale campaign on PlanetLab: http://www-sop.inria.fr/members/Chadi.Barakat/ICC2015.pdf
Typical usage looks like this::

    #!/usr/bin/env python

    from icmptool import icmp_tool

    routers_by_hop = icmp_tool(dest='8.8.8.8', ttls=[1,2,3,4], min_rate=1, max_rate=500, n_of_rates=5, duration=8):
    
By doing that, we probed routers at hops 1, 2, 3, 4 on the path to 8.8.8.8, at 5 exponentially-spaced probing rates between 1 pps and 500 pps, for 8 seconds each time.
routers_by_hop will now contain at key i details of the responsiveness of the router on hop i.

Alternatively, icmp_tool.py can be used as a standalone script by calling it from the shell. The above example simply becomes::

    $ python icmptool.py --dest 8.8.8.8 --ttls 1 2 3 4 --min_rate 1 --max_rate 500 --n_of_rates 5 --duration 8

