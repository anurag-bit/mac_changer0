import unittest
import re
from unittest.mock import patch, MagicMock, call # Added call for checking call order/args

# Attempt to import core functions.
try:
    from mac_changer.core import (
        generate_random_mac,
        set_mac,
        get_current_mac,
        MAC_ADDRESS_REGEX as CORE_MAC_REGEX
    )
except ImportError:
    import sys
    import os
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from mac_changer.core import (
        generate_random_mac,
        set_mac,
        get_current_mac,
        MAC_ADDRESS_REGEX as CORE_MAC_REGEX
    )
import subprocess # For CalledProcessError

# Regex for validating MAC address format in tests (stricter, only colons)
MAC_REGEX_VALIDATOR = re.compile(r"^([0-9a-fA-F]{2}:){5}([0-9a-fA-F]{2})$")

class TestMacGeneration(unittest.TestCase):
    """
    Tests for the MAC address generation capabilities.
    """
    def test_generate_random_mac_format(self):
        """
        Test if generated MAC addresses are in the correct format and are unicast.
        """
        for _ in range(100):
            mac = generate_random_mac()
            self.assertIsNotNone(mac, "Generated MAC should not be None")
            self.assertTrue(MAC_REGEX_VALIDATOR.match(mac), 
                            f"Generated MAC '{mac}' is not in XX:XX:XX:XX:XX:XX format.")
            first_octet_int = int(mac.split(':')[0], 16)
            self.assertEqual(first_octet_int & 1, 0,
                             f"Generated MAC '{mac}' is not a unicast address.")

    def test_generate_random_mac_uniqueness(self):
        """
        Test if generated MAC addresses are reasonably unique.
        """
        num_macs_to_generate = 100
        mac_list = [generate_random_mac() for _ in range(num_macs_to_generate)]
        self.assertEqual(len(set(mac_list)), num_macs_to_generate,
                         "Generated MAC addresses should be unique for a small sample.")

class TestMacValidation(unittest.TestCase):
    """
    Tests the MAC address validation logic used within set_mac.
    Relies on mocking out parts of set_mac that perform actions.
    """
    @patch('mac_changer.core.subprocess.run') # Mock subprocess.run
    @patch('mac_changer.core.get_current_mac') # Mock get_current_mac
    def test_mac_validation_in_set_mac(self, mock_get_current_mac, mock_subprocess_run):
        """
        Test set_mac's internal MAC validation.
        """
        # Configure mocks to simulate a successful environment for valid MACs
        mock_get_current_mac.return_value = "00:00:00:00:00:00" # Dummy current MAC
        mock_subprocess_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

        # Valid MACs (should pass validation step and proceed)
        valid_macs = ["00:1A:2B:3C:4D:5E", "aa:bb:cc:dd:ee:ff", "00-1A-2B-3C-4D-5E"]
        for mac in valid_macs:
            # If validation passes, set_mac should return True (given mocks are positive)
            # or False if verification fails (which we also mock via get_current_mac side_effect if needed)
            # For this specific test, we are focused on the initial validation regex.
            # We assume if it passes validation, it would attempt to change.
            # The CORE_MAC_REGEX is what set_mac uses.
            self.assertTrue(CORE_MAC_REGEX.match(mac), f"MAC {mac} should be considered valid by CORE_MAC_REGEX")
            # We expect set_mac to return True if validation and subsequent (mocked) operations pass
            # For the last valid MAC, set up get_current_mac to simulate successful change for verification
            if mac == valid_macs[-1]:
                 mock_get_current_mac.side_effect = ["00:00:00:00:00:00", mac.replace('-',':')]
            else:
                 mock_get_current_mac.side_effect = ["00:00:00:00:00:00", "00:1A:2B:3C:4D:5E"] # Default success for others

            self.assertTrue(set_mac("eth0", mac), f"set_mac should succeed for valid MAC: {mac}")


        # Invalid MACs (should be caught by validation and cause set_mac to return False)
        invalid_macs = [
            "00:1A:2B:3C:4D:5Z",  # invalid hex char
            "00:1A:2B:3C:4D",     # too short
            "00:1A:2B:3C:4D:5E:6F",# too long
            "Hello:World:Of:Macs:FF:00", # non-hex
            "00_1A_2B_3C_4D_5E"   # invalid separator
        ]
        for mac in invalid_macs:
            self.assertFalse(CORE_MAC_REGEX.match(mac) and not set_mac("eth0", mac), f"MAC {mac} is invalid but was not caught or set_mac did not return False.")
            self.assertFalse(set_mac("eth0", mac), f"set_mac should return False for invalid MAC: {mac}")


class TestGetCurrentMac(unittest.TestCase):
    """
    Tests for get_current_mac function, mocking subprocess calls.
    """
    @patch('mac_changer.core.subprocess.check_output')
    def test_get_current_mac_success(self, mock_check_output):
        """Test successful retrieval of MAC address."""
        sample_mac = "0A:1B:2C:3D:4E:5F"
        ifconfig_output = f"""
        eth0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
                inet 192.168.1.100  netmask 255.255.255.0  broadcast 192.168.1.255
                inet6 fe80::abc:def:ghi:jkl  prefixlen 64  scopeid 0x20<link>
                ether {sample_mac}  txqueuelen 1000  (Ethernet)
                RX packets 12345  bytes 6789012
                RX errors 0  dropped 0  overruns 0  frame 0
                TX packets 54321  bytes 1098765
                TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0
        """
        mock_check_output.return_value = ifconfig_output
        self.assertEqual(get_current_mac("eth0"), sample_mac.lower()) # MACs are often lowercased by tools

    @patch('mac_changer.core.subprocess.check_output')
    def test_get_current_mac_interface_not_found(self, mock_check_output):
        """Test when interface is not found (ifconfig raises error)."""
        mock_check_output.side_effect = subprocess.CalledProcessError(returncode=1, cmd="ifconfig eth1", output="eth1: error fetching interface information: Device not found")
        self.assertIsNone(get_current_mac("eth1"))

    @patch('mac_changer.core.subprocess.check_output')
    def test_get_current_mac_no_mac_in_output(self, mock_check_output):
        """Test ifconfig output that doesn't contain a MAC address."""
        ifconfig_output_no_mac = """
        lo: flags=73<UP,LOOPBACK,RUNNING>  mtu 65536
                inet 127.0.0.1  netmask 255.0.0.0
                loop  txqueuelen 1000  (Local Loopback)
        """
        mock_check_output.return_value = ifconfig_output_no_mac
        self.assertIsNone(get_current_mac("lo"))

    @patch('mac_changer.core.subprocess.check_output', side_effect=FileNotFoundError("ifconfig not found"))
    def test_get_current_mac_ifconfig_not_found(self, mock_check_output):
        """Test when ifconfig command itself is not found."""
        self.assertIsNone(get_current_mac("eth0"))


class TestSetMac(unittest.TestCase):
    """
    Tests for set_mac function, mocking subprocess and get_current_mac.
    """
    @patch('mac_changer.core.subprocess.run')
    @patch('mac_changer.core.get_current_mac')
    def test_set_mac_success(self, mock_get_current_mac, mock_subprocess_run):
        """Test successful MAC address change."""
        interface = "eth0"
        current_mac = "00:11:22:33:44:55"
        new_mac = "AA:BB:CC:DD:EE:FF"
        
        # Simulate get_current_mac: first call for initial check, second for verification
        mock_get_current_mac.side_effect = [current_mac, new_mac.lower()] # .lower() because our get_current_mac normalizes
        
        # Simulate successful subprocess.run calls
        mock_subprocess_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
        
        self.assertTrue(set_mac(interface, new_mac))
        
        # Check that get_current_mac was called twice
        self.assertEqual(mock_get_current_mac.call_count, 2)
        
        # Check subprocess.run calls
        expected_calls = [
            call(["ifconfig", interface, "down"], check=True, capture_output=True, text=True),
            call(["ifconfig", interface, "hw", "ether", new_mac.lower()], check=True, capture_output=True, text=True),
            call(["ifconfig", interface, "up"], check=True, capture_output=True, text=True)
        ]
        mock_subprocess_run.assert_has_calls(expected_calls, any_order=False)

    @patch('mac_changer.core.subprocess.run')
    @patch('mac_changer.core.get_current_mac')
    def test_set_mac_ifconfig_failure(self, mock_get_current_mac, mock_subprocess_run):
        """Test set_mac when an ifconfig command fails."""
        interface = "eth0"
        current_mac = "00:11:22:33:44:55"
        new_mac = "AA:BB:CC:DD:EE:FF"
        
        mock_get_current_mac.return_value = current_mac
        # Simulate failure of the 'hw ether' command
        mock_subprocess_run.side_effect = [
            MagicMock(returncode=0), # ifconfig down succeeds
            subprocess.CalledProcessError(returncode=1, cmd="ifconfig hw ether ...", stderr="Error setting MAC"), # hw ether fails
            MagicMock(returncode=0)  # ifconfig up (attempted cleanup)
        ]
        
        self.assertFalse(set_mac(interface, new_mac))
        mock_subprocess_run.assert_any_call(["ifconfig", interface, "up"], capture_output=True, text=True) # Check cleanup attempt

    @patch('mac_changer.core.subprocess.run')
    @patch('mac_changer.core.get_current_mac')
    def test_set_mac_invalid_interface(self, mock_get_current_mac, mock_subprocess_run):
        """Test set_mac when the initial get_current_mac returns None (interface problem)."""
        interface = "nonexistent_iface"
        new_mac = "AA:BB:CC:DD:EE:FF"
        
        mock_get_current_mac.return_value = None # Simulate interface not found or no MAC
        
        self.assertFalse(set_mac(interface, new_mac))
        mock_subprocess_run.assert_not_called() # No ifconfig commands should be run

    @patch('mac_changer.core.subprocess.run')
    @patch('mac_changer.core.get_current_mac')
    def test_set_mac_verification_failure(self, mock_get_current_mac, mock_subprocess_run):
        """Test set_mac when MAC address change cannot be verified."""
        interface = "eth0"
        current_mac = "00:11:22:33:44:55"
        new_mac_to_set = "AA:BB:CC:DD:EE:FF"
        mac_after_attempt = "00:11:22:33:44:55" # MAC remains unchanged
        
        mock_get_current_mac.side_effect = [current_mac, mac_after_attempt]
        mock_subprocess_run.return_value = MagicMock(returncode=0)
        
        self.assertFalse(set_mac(interface, new_mac_to_set))

    @patch('mac_changer.core.subprocess.run', side_effect=FileNotFoundError("ifconfig not found"))
    @patch('mac_changer.core.get_current_mac')
    def test_set_mac_ifconfig_not_found(self, mock_get_current_mac, mock_subprocess_run):
        """Test set_mac when ifconfig command itself is not found."""
        mock_get_current_mac.return_value = "00:11:22:33:44:55" # Assume get_current_mac could be called before the failing subprocess.run
        self.assertFalse(set_mac("eth0", "AA:BB:CC:DD:EE:FF"))


if __name__ == '__main__':
    unittest.main()
