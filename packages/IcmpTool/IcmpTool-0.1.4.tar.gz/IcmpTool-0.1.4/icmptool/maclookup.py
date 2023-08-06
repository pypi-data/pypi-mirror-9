#!/usr/bin/env python

import csv, sys

my_lookup_table = 'mac-addr-lookup-table.csv'

def convert_original_table():
    table = {}
    t  = []
    # list used in wireshark
    # http://anonsvn.wireshark.org/wireshark/trunk/manuf
    table_path = 'manuf-and-mac-addr.txt'
    with open(table_path, 'rb') as f:
        reader = csv.reader(f)
        for row in reader:
            oui = row[0].split('\t')[0] #get oui
            #get vendor name
            if '#' in row[0]:
                vendor = row[0].split('#')[1].lstrip(' ')
            else:
                vendor = row[0].split('\t')[1].lstrip(' ')
            table[oui] = vendor
    # write to a csv file for later use
    writer = csv.writer(open(my_lookup_table, 'wb'))
    for key, value in table.items():
        writer.writerow([key, value])
    return
    
    
def get_lookup_table():
    with open(my_lookup_table, 'rb') as f:
        reader = csv.reader(f)
        table = dict(x for x in reader)
    return table
    
    
def lookup_mac(macaddr):
    #letters are upper case in the table
    macaddr = macaddr.upper()
    table = get_lookup_table()
    #Organizationally Unique Identifier (OUI): first 3 bytes (brand) + 3 (brand-specific counter)
    oui = macaddr[:8]
#    print "oui: %s" % oui
    if oui in table:
        return table[oui]
    else:
        return None
    

def main():
    macaddr = str(sys.argv[1])
    print lookup_mac(macaddr)
    return

if __name__ == '__main__':
    status = main()
    sys.exit(status)
