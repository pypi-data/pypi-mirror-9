#!/usr/bin/env python
import sys, time, subprocess, math, pickle
import sys

#sys.path.append('/var/lib/virtdc/vmonere/host')
#sys.path.append('/var/lib/virtdc/simulation')

#from simulate_google_data import simulate_google_data
#==============================================================================
# Variables
#==============================================================================

# Some descriptive variables
#name                = "virtdc"
#version             = "0.1.0"
#long_description    = """virtdc is a set of API's/tools written to create virtual machines for cloud users efficiently."""
#url                 = "https://github.com/dineshappavoo/virtdc"
#license             = ""

#==============================================================================


def config_domain(file_format, file_name):
    print "In Config domain"
    print file_name
    print file_format
def get_host_name(vm_id):
    pass
def get_ip(vmid):
    pass
def get_domain_object(vm_id):
    pass

def list_host_and_domain():
    pass
def list_host_domain_information():
    pass
def show_domain_info(vm_id):
    pass

def show_host_info(host_name):
    pass

def force_migrate(vmid, source_host, dest_host):
    pass
def terminate_guest(host_name,vmid):
    pass
def load_balance():
    pass
def consolidate():
	pass
def monitorgraph():
	pass
def simulate_data():
    pass

if __name__ == "__main__":
   # stuff only to run when not called via 'import' here
   get_host_name('Test')
