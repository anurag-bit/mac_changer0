import subprocess
import re
import random

# Regex for validating MAC address format (accepts : and - as separators)
MAC_ADDRESS_REGEX = re.compile(r"^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$")

def set_mac(interface, new_mac):
	"""
	Sets the MAC address for a given network interface after validating the
	interface and MAC address format.

	This function uses external commands (`ifconfig`) which typically require
	root privileges to modify network interface settings. The process involves
	temporarily taking the interface down, applying the new MAC address, and
	then bringing the interface back up. It also includes a verification step
	to confirm if the MAC address was changed as expected.

	Args:
		interface (str): The name of the network interface (e.g., "eth0", "wlan0")
		                 for which the MAC address is to be changed.
		new_mac (str): The desired new MAC address. This should be in a standard
		               hexadecimal format, such as "XX:XX:XX:XX:XX:XX" or
		               "XX-XX-XX-XX-XX-XX".

	Returns:
		bool: Returns `True` if the MAC address was successfully changed and
		      verified. Returns `False` in several cases:
		      - The provided `new_mac` has an invalid format.
		      - The specified `interface` is not found or `ifconfig` fails to access it
		        (e.g., due to lack of permissions or non-existent interface).
		      - Any of the `ifconfig` commands (down, hw ether, up) fail.
		      - The MAC address change could not be verified after the attempt.
		      Detailed error messages are printed to standard output in case of failures.

	Note:
		This function directly executes system commands and relies on `ifconfig`.
		Error messages from these commands are captured and printed.
		It may not be portable to systems that do not use `ifconfig`.
	"""
	if not MAC_ADDRESS_REGEX.match(new_mac):
		print(f"[!] Invalid MAC address format: {new_mac}. Use XX:XX:XX:XX:XX:XX or XX-XX-XX-XX-XX-XX.")
		return False

	# Normalize MAC to use colons for ifconfig
	normalized_mac = new_mac.replace('-', ':')

	current_mac = get_current_mac(interface)
	if current_mac is None:
		# get_current_mac already prints an error, so no need to print another here.
		# It implies the interface might not exist or isn't readable.
		return False
	
	print(f"[+] Attempting to change MAC address for {interface} from {current_mac} to {normalized_mac}...")

	commands = [
		["ifconfig", interface, "down"],
		["ifconfig", interface, "hw", "ether", normalized_mac],
		["ifconfig", interface, "up"]
	]

	for cmd in commands:
		try:
			# Using subprocess.run for better control and error checking
			result = subprocess.run(cmd, check=True, capture_output=True, text=True)
			if result.returncode != 0: # Should be caught by check=True, but as a safeguard
				print(f"[!] Error executing '{' '.join(cmd)}'. Return code: {result.returncode}")
				print(f"    Stdout: {result.stdout.strip()}")
				print(f"    Stderr: {result.stderr.strip()}")
				return False
		except subprocess.CalledProcessError as e:
			print(f"[!] Error executing '{' '.join(e.cmd)}'. Return code: {e.returncode}")
			print(f"    Error message: {e.stderr.strip() if e.stderr else e.stdout.strip()}")
			# Attempt to bring the interface back up if 'down' succeeded but 'hw ether' or 'up' failed.
			if cmd[2] != "down": # if the failing command was not 'ifconfig down'
				print(f"    Attempting to bring interface {interface} back up...")
				subprocess.run(["ifconfig", interface, "up"], capture_output=True, text=True)
			return False
		except FileNotFoundError:
			print(f"[!] Error: The 'ifconfig' command was not found. Please ensure it is installed and in your PATH.")
			return False


	# Verify the MAC address was actually changed
	final_mac = get_current_mac(interface)
	if final_mac == normalized_mac:
		print(f"[+] MAC address for {interface} was successfully changed to {normalized_mac}")
		return True
	else:
		print(f"[!] Failed to change MAC address for {interface}. Current MAC is {final_mac}, expected {normalized_mac}.")
		return False


def get_current_mac(interface):
	"""
	Retrieves the current hardware (MAC) address for a specified network interface.

	This function parses the output of the `ifconfig <interface>` command to find
	the MAC address. The returned MAC address is normalized to use colons as
	separators (e.g., "00:11:22:aa:bb:cc").

	Args:
		interface (str): The name of the network interface (e.g., "eth0", "wlan0")
		                 from which to retrieve the MAC address.

	Returns:
		str or None: The current MAC address as a string if successfully found and parsed.
		             Returns `None` if:
		             - The `ifconfig` command fails (e.g., interface not found,
		               permissions error).
		             - The MAC address cannot be parsed from the `ifconfig` output.
		             - The `ifconfig` command itself is not found.
		             Detailed error messages are printed to standard output in case of failures.

	Note:
		This function depends on the `ifconfig` command and its output format.
		Changes in `ifconfig` or its unavailability can affect this function.
	"""
	try:
		# universal_newlines=True is equivalent to text=True
		ifconfig_result = subprocess.check_output(["ifconfig", interface], text=True, stderr=subprocess.STDOUT)
		# More robust regex to find MAC, typically after 'ether ' or 'HWaddr '
		mac_address_search_result = re.search(r"(?:ether|HWaddr)\s+((?:[0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2})", ifconfig_result, re.IGNORECASE)
		if mac_address_search_result:
			return mac_address_search_result.group(1).replace('-', ':') # Normalize to colons
		else:
			print(f"[!] Could not find MAC address for interface {interface} in ifconfig output.")
			return None
	except subprocess.CalledProcessError as e:
		print(f"[!] Error fetching details for interface {interface}. Command: '{' '.join(e.cmd)}'. Return code: {e.returncode}.")
		# Error messages for common issues
		if "No such device" in e.output or "not found" in e.output:
			print(f"    Error: Interface {interface} not found.")
		else:
			print(f"    Output: {e.output.strip()}")
		return None
	except FileNotFoundError:
		print(f"[!] Error: The 'ifconfig' command was not found. Please ensure it is installed and in your PATH.")
		return None


def generate_random_mac():
	"""
	Generates a cryptographically insecure, random MAC address.

	The generated MAC address is formatted as a standard unicast address
	(XX:XX:XX:XX:XX:XX). The first octet is modified to ensure the
	least significant bit is 0, preventing it from being a multicast address.
	The randomness is derived from Python's `random` module, which is not
	intended for cryptographic security.

	Returns:
		str: A randomly generated MAC address string (e.g., "0a:1b:2c:3d:4e:5f").
	"""
	mac_address = [
		random.randint(0x00, 0xff),
		random.randint(0x00, 0xff),
		random.randint(0x00, 0xff),
		random.randint(0x00, 0xff),
		random.randint(0x00, 0xff),
		random.randint(0x00, 0xff)
	]
	# Ensure the first byte's second hex digit is even (0, 2, 4, 6, 8, A, C, E)
	# This makes the first octet xx:.. where x is 0-F and the second x is 0,2,4,6,8,A,C,E
	mac_address[0] = (mac_address[0] & 0xFE) # Clears the LSB (multicast bit)
	# To make it more "random" while ensuring the second char is even, we can do this:
	first_byte_str = format(mac_address[0], '02x')
	if int(first_byte_str[1], 16) % 2 != 0:
		# If the second hex char is odd, make it even by subtracting 1 from its int value
		# This is a bit simplistic, a better way might be to pick from '02468ACE'
		new_second_char_val = int(first_byte_str[1], 16) -1
		first_byte_str = first_byte_str[0] + format(new_second_char_val, 'x')
		mac_address[0] = int(first_byte_str, 16)


	return ":".join(map(lambda x: format(x, '02x'), mac_address))


def set_random_mac(interface):
	"""
	Generates a random MAC address and attempts to set it for the specified
	network interface.

	This function utilizes `generate_random_mac()` to create a new MAC address
	and then calls `set_mac()` to apply it to the given interface.

	Args:
		interface (str): The name of the network interface (e.g., "eth0", "wlan0")
		                 for which a random MAC address will be set.
	
	Returns:
		bool: `True` if the random MAC address was successfully generated and applied
		      to the interface. `False` otherwise (e.g., if `set_mac` fails).
		      Refer to `set_mac()` for details on potential failure reasons.
	"""
	random_mac = generate_random_mac()
	print(f"[+] Generated random MAC for {interface}: {random_mac}")
	return set_mac(interface, random_mac)


def reset_to_original_mac(interface):
	"""
	Placeholder function intended for resetting the MAC address of an interface
	to its original, factory-set hardware value.

	Warning:
		This functionality is **not yet implemented**. Reliably determining and
		restoring the original MAC address across different systems, reboots,
		and hardware types is a complex task that is beyond the current
		capabilities of this script. Manual intervention or system-specific tools
		are typically required for this.

	Args:
		interface (str): The name of the network interface (e.g., "eth0", "wlan0")
		                 that would be targeted for MAC reset.
	"""
	print(f"[!] Resetting to original MAC is not yet implemented for interface {interface}.")
