#!/usr/bin/env python

import optparse
import subprocess
from optparse import OptionParser


def get_arguments():
	parser: OptionParser = optparse.OptionParser()

	parser.add_option("-i", "--interface", dest="interface", help="interface to change mac address for")
	parser.add_option("-m", "--mac", dest="new_mac", help=" change mac address to")
	return parser.parse_args()


def change_mac(interface, new_mac):
	print("[+] Changing The Mac address for {0} to {1}".format(interface, new_mac))

	subprocess.call(["ifconfig", interface, "down"])
	subprocess.call(["ifconfig", interface, "hw", "ether", new_mac])
	subprocess.call(["ifconfig", interface, "up"])


(options, arguments) = get_arguments()
change_mac(options.interface, options.new_mac)
