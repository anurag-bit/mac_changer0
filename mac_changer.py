#!/usr/bin/env python
"""
mac_changer.py - Command-Line Interface for MAC Address Modification.

This script provides a command-line interface (CLI) to view or change the
MAC address of a network interface on Linux systems. It leverages the
`mac_changer.core` library for the actual MAC manipulation operations.

Key functionalities include displaying the current MAC address, setting a
user-defined MAC address, and setting a randomly generated MAC address.

Execution of this script for any operation that modifies network settings
(setting a specific or random MAC) requires `sudo` (root) privileges. This
is because such operations involve using the `ifconfig` command to alter
network interface properties. Viewing the MAC address might also require
`sudo` depending on system configuration, although it's less common.

Basic Usage Examples:
  To show the current MAC address of interface 'eth0':
    sudo python mac_changer.py -i eth0 -s

  To set a specific MAC address '00:11:22:33:44:55' for 'eth0':
    sudo python mac_changer.py -i eth0 -m 00:11:22:33:44:55

  To set a randomly generated MAC address for 'eth0':
    sudo python mac_changer.py -i eth0 -r

Refer to the help message (`-h` or `--help`) for a full list of options.
"""

import optparse
import re # Import re for MAC address validation
from optparse import OptionParser
from mac_changer.core import set_mac, get_current_mac, set_random_mac

# Regex for validating MAC address format (copied from core.py for CLI-side validation)
MAC_ADDRESS_REGEX_CLI = re.compile(r"^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$")

def get_arguments():
	"""
	Parses and returns command-line arguments supplied to the script.

	This function uses Python's `optparse` module to define and parse
	command-line options. It configures options for specifying the network
	interface, providing a new MAC address, requesting a random MAC address,
	or showing the current MAC address.

	The function's description and epilog provide users with context and
	examples on how to use the tool.

	Returns:
		tuple: A tuple containing two elements:
		    - options (optparse.Values): An object that holds the values of the
		      parsed command-line arguments (e.g., `options.interface`,
		      `options.new_mac`).
		    - parser (optparse.OptionParser): The `OptionParser` instance itself.
		      This can be useful for displaying help messages or errors.
	"""
	parser: OptionParser = optparse.OptionParser(
		description="MAC Address Changer Tool. Allows viewing and modification of network interface MAC addresses. Requires root privileges for modification.",
		epilog="Examples:\n"
		       "  Show MAC: sudo python mac_changer.py -i eth0 -s\n"
		       "  Set MAC:  sudo python mac_changer.py -i eth0 -m 00:AA:BB:CC:DD:EE\n"
		       "  Set Random MAC: sudo python mac_changer.py -i eth0 -r"
	)

	parser.add_option("-i", "--interface", dest="interface", help="Interface to target (e.g., eth0, wlan0). REQUIRED for most operations.")
	parser.add_option("-m", "--mac", dest="new_mac", help="New MAC address to set (e.g., 00:11:22:33:44:55 or 00-11-22-33-44-55).")
	parser.add_option("-r", "--random", dest="random", action="store_true", help="Set a random MAC address for the specified interface. Overrides -m if both are given.")
	parser.add_option("-s", "--show", dest="show", action="store_true", help="Show the current MAC address of the specified interface. Ignores -m and -r.")
	
	options, arguments = parser.parse_args() # The 'arguments' variable captures non-option arguments, not used in this script.
	return options, parser

if __name__ == "__main__":
    options, parser = get_arguments()

    # Priority of operations:
    # 1. If --show is present, just show MAC and exit.
    # 2. If --random is present, set random MAC.
    # 3. If --mac is present (and not --random), set specific MAC.
    # 4. Interface must always be specified for any action.
    # 5. If no action is specified, or only interface, print help.

    if not options.interface:
        if options.show or options.random or options.new_mac:
             print("[-] Error: An interface must be specified with -i or --interface for this operation.")
        parser.print_help()
        exit()

    if options.show:
        print(f"[+] Querying current MAC address for {options.interface}...")
        current_mac = get_current_mac(options.interface)
        if current_mac:
            print(f"    Current MAC for {options.interface}: {current_mac}")
        else:
            # get_current_mac in core.py already prints detailed errors
            print(f"[-] Failed to retrieve MAC address for {options.interface}. See errors above.")
    elif options.random:
        print(f"[+] Attempting to set a random MAC address for {options.interface}...")
        if set_random_mac(options.interface):
            print(f"[+] Successfully set a random MAC address for {options.interface}.")
        else:
            print(f"[!] Failed to set a random MAC address for {options.interface}. See errors above.")
    elif options.new_mac:
        # Validate MAC address format at CLI level
        if not MAC_ADDRESS_REGEX_CLI.match(options.new_mac):
            print(f"[!] Invalid MAC address format specified: '{options.new_mac}'.")
            print("    Please use format like XX:XX:XX:XX:XX:XX or XX-XX-XX-XX-XX-XX.")
            parser.print_help()
            exit()
        
        print(f"[+] Attempting to set MAC address for {options.interface} to {options.new_mac}...")
        if set_mac(options.interface, options.new_mac):
            # core.set_mac already prints a detailed success message
            pass # No need for another success message here, core function handles it.
        else:
            # core.set_mac already prints detailed error messages
            print(f"[!] Failed to set MAC address for {options.interface} to {options.new_mac}. See errors above.")
    else:
        # Neither --show, --random, nor --mac was specified, but -i might have been.
        print("[-] Error: No action specified (e.g., --show, --random, --mac <address>).")
        parser.print_help()
        exit()
