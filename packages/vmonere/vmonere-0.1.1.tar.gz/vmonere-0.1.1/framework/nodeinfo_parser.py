#!/usr/bin/env python

import yaml

def parse_node_info():
    with open('/Users/Dany/Documents/vmonere/framework/nodeinfo.yaml', 'r') as f:
        doc = yaml.load(f)
    
    print doc

    txt = doc["nodesa"]
    print txt

if __name__ == "__main__":
   # stuff only to run when not called via 'import' here
   parse_node_info()

#======================================================================
#			FOR TESTING
#======================================================================
#Function calls - follow the same order to call
#GetNodeDict()




