#!/usr/bin/env python
import argparse
import sys, os
#from VM_terminateGuest import vm_terminate_guest
from vmonere_command_line_utility import get_host_name, list_host_and_domain, show_domain_info, \
    show_host_info, force_migrate, terminate_guest, monitorgraph, list_host_domain_information, \
    load_balance, consolidate, get_ip

#API - vmonere command line tool

#==============================================================================
# Variables
#==============================================================================
# Some descriptive variables
#name                = "vmonere"
#version             = "0.1.0"
#long_description    = """vmonere - A cloud monitoring API to get the real time status."""
#url                 = "https://github.com/dcsolvere/vmonere"
#license             = "MIT"

#==============================================================================


def main(argv):
	
	parser = argparse.ArgumentParser(description="A cloud monitoring API to get the real time status", version='vmonere 0.1.0')
	
	subparsers = parser.add_subparsers(help='Grouped command', dest='subparser_name')

	adddomain_parser = subparsers.add_parser('adddomain',help='add new domain to vmonere')
	adddomain_parser.add_argument('host', action = 'store', help ='get the host name')
	adddomain_parser.add_argument('ipaddress', action = 'store', help ='get the ip address')

	removedomain_parser = subparsers.add_parser('removedomain',help='remove the deomain from vmonere')
	removedomain_parser.add_argument('host', action = 'store', help ='get the host name')

	list_parser = subparsers.add_parser('list',help='list existing domain')

	dominfo_parser = subparsers.add_parser('dominfo',help='domain information')
	dominfo_parser.add_argument('vmid', action = 'store', help ='get the domain id')

	hostinfo_parser = subparsers.add_parser('hostinfo',help='host information')
	hostinfo_parser.add_argument('hostname', action = 'store', help ='get the host')

	removehost_parser = subparsers.add_parser('removehost',help='remove host')
	removehost_parser.add_argument('hostname', action = 'store', help ='get the host')

	addhost_parser = subparsers.add_parser('addhost',help='add new host')
	addhost_parser.add_argument('hostname', action = 'store', help ='get the host')
	addhost_parser.add_argument('cpu', action = 'store', help ='get the cpu')
	addhost_parser.add_argument('memory', action = 'store', help ='get memory in KiB')
	addhost_parser.add_argument('io', action = 'store', help ='get the io in KiB')	

	getip_parser = subparsers.add_parser('getip',help='get domain ip')
	getip_parser.add_argument('host', action = 'store', help ='get the domain host name')

	#mail api configuration
	setsmtpserver_parser = subparsers.add_parser('setsmtpserver',help='set smtp server')
	setsmtpserver_parser.add_argument('serverip', action = 'store', help ='get the server ip')

	setfrommailaddress_parser = subparsers.add_parser('setfrommailaddress',help='set from mailaddress')
	setfrommailaddress_parser.add_argument('mailid', action = 'store', help ='get the from mail address')

	addsupportmail_parser = subparsers.add_parser('addsupportmail',help='add support mail address')
	addsupportmail_parser.add_argument('mailid', action = 'store', help ='get the mail address')

	monitorcpu_parser = subparsers.add_parser('monitorgraph',help='monitor domain usage')
	#monitorcpu_parser.add_argument('vmid', action = 'store', help ='get the domain id')

	args = parser.parse_args()

	if args.subparser_name == 'adddomain':
		#print 'Call add vmonere domain'
		host =args.host
		ipaddress = args.ipaddress
        #create_vm(vmid, cpu, memory, max_memory, io)
		
	elif args.subparser_name == 'removedomain':
		#print 'Call vmonere remove domain'
		host = args.host
		if vmonere_remove_domain is False:
			print 'The requested domain '+str(host) +' cannot be remove'
		else:
			print 'The requested domain '+str(host) +' removed successfully'
		
	elif args.subparser_name == 'list':
		#print 'Call vm_list'
		list_domain_information()
	elif args.subparser_name == 'dominfo':
		#print 'Call vm_dominfo'
		vmid = args.vmid
		show_domain_info(vmid)
	elif args.subparser_name == 'hostinfo':
		#print 'Call vm_hostinfo'
		host_name = args.hostname
		dom_info = show_host_info(host_name)
		if dom_info == False:
			print 'Host name not found/not configured to this cluster'
	# Python argparse Namespace of '-' will be converted to '_'
	elif args.subparser_name == 'removehost':
		print 'Call host_removehost'
	elif args.subparser_name == 'addhost':
		print 'Call vm_addhost'
		#Add entry to nodeinfo XML and then run Host_Info_Tracker.py
		#So from next new domain creation will consider this space
		
	elif args.subparser_name == 'monitorgraph':
		#print 'Call vm_monitorgraph'
		#vmid = args.vmid
		monitorgraph()
	elif args.subparser_name == 'getip':
		vmid = args.vmid
		ip_addr = get_ip(vmid)
		if ip_addr is None:
			print  'IP address not found'
		else:
			print ip_addr

	elif args.subparser_name == 'list':
		print 'Call vm_list'
	elif args.subparser_name == 'list':
		print 'Call vm_list'
	elif args.subparser_name == 'list':
		print 'Call vm_list'
	elif args.subparser_name == 'list':
		print 'Call vm_list'
	elif args.subparser_name == 'list':
		print 'Call vm_list'
	else:
		a=0


	#print args
	#print parser.parse_args(['terminate','Dinesh'])
	#print parser.parse_args(['create','Dinesh','1','64434','53445'])
	


if __name__ == "__main__":
	main(sys.argv[1:])
