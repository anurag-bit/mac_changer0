# MAC Address Changer

## Description
MAC Address Changer is a Python library and command-line tool designed for viewing and changing the MAC (Media Access Control) address of network interfaces on Linux systems. It provides functionalities to see the current MAC, set a user-defined MAC, or assign a randomly generated MAC address.

## Disclaimer
**Warning:** Modifying your MAC address can lead to network connectivity issues or be against the terms of service of some networks. Use this tool responsibly and ethically. Ensure you have authorization before changing the MAC address on any network or device you do not own.
**This tool requires `sudo` (root) privileges to modify network interface settings.**

## Features
*   View the current MAC address of a specified network interface.
*   Set a specific, user-defined MAC address for an interface.
*   Generate and set a random (unicast) MAC address for an interface.
*   Input validation for MAC address format.
*   Error handling for command execution and interface issues.

## Prerequisites
*   Python 3.x
*   `ifconfig` command-line utility (standard on many Linux distributions).
    *   Note: The tool's reliance on `ifconfig` currently limits its use to Linux systems where `ifconfig` is available and used for network configuration.

## Installation (from source / local usage)
1.  Clone the repository:
    ```bash
    git clone <repository_url>
    ```
    (Replace `<repository_url>` with the actual URL of your Git repository)

2.  Navigate to the project directory:
    ```bash
    cd mac_changer
    ```
    (Or your specific repository name)

## Command-Line Interface (CLI) Usage
The script must be run with `sudo` for operations that change the MAC address.

**Basic Syntax:**
```bash
sudo python mac_changer.py [options]
```

**Options:**
*   `-i INTERFACE`, `--interface INTERFACE`:
    *   Specify the network interface to target (e.g., `eth0`, `wlan0`). This option is required for all operations.
*   `-m MAC`, `--mac MAC`:
    *   Specify the new MAC address to set. Format can be `XX:XX:XX:XX:XX:XX` or `XX-XX-XX-XX-XX-XX`.
*   `-r`, `--random`:
    *   Generate and set a random MAC address for the specified interface. If both `-m` and `-r` are provided, `-r` usually takes precedence (as per current implementation logic).
*   `-s`, `--show`:
    *   Show the current MAC address of the specified interface. This option ignores `-m` and `-r`.
*   `-h`, `--help`:
    *   Show the help message detailing all options and exit.

**CLI Examples:**
*   Show the current MAC address of `eth0`:
    ```bash
    sudo python mac_changer.py -i eth0 -s
    ```
*   Set a specific MAC address for `eth0`:
    ```bash
    sudo python mac_changer.py -i eth0 -m 00:11:22:33:44:55
    ```
*   Set a random MAC address for `wlan0`:
    ```bash
    sudo python mac_changer.py -i wlan0 -r
    ```

## Library Usage (Python Code Example)
The core functionalities can be imported and used in other Python scripts. Ensure that any script using these functions to change MAC addresses is run with sufficient privileges (e.g., as root).

```python
from mac_changer import core
import os # For checking user privileges

if __name__ == "__main__":
    # Check for root privileges before attempting to change MAC
    if os.geteuid() != 0:
        print("Error: This script requires root privileges to change MAC addresses.")
        # exit(1) # Uncomment to exit if not root, depending on desired behavior

    interface = "eth0" # Replace with your target interface

    # Example: Get current MAC address
    print(f"Attempting to get current MAC for {interface}...")
    current_mac = core.get_current_mac(interface)
    if current_mac:
        print(f"Current MAC for {interface}: {current_mac}")
    else:
        print(f"Failed to get current MAC for {interface}.")
    
    print("-" * 30)

    # Example: Set a specific MAC address (use with caution)
    # Ensure the interface exists and you have permissions.
    # new_specific_mac = "00:AA:BB:CC:DD:EE" 
    # print(f"Attempting to set MAC for {interface} to {new_specific_mac}...")
    # if os.geteuid() == 0: # Only attempt if root
    #     success = core.set_mac(interface, new_specific_mac)
    #     if success:
    #         print(f"Successfully set MAC for {interface} to {new_specific_mac}")
    #     else:
    #         print(f"Failed to set MAC for {interface} to {new_specific_mac}.")
    # else:
    #     print("Skipping set_mac example: root privileges required.")

    # print("-" * 30)

    # Example: Set a random MAC address (use with caution)
    # Ensure the interface exists and you have permissions.
    # print(f"Attempting to set a random MAC for {interface}...")
    # if os.geteuid() == 0: # Only attempt if root
    #     random_success = core.set_random_mac(interface)
    #     if random_success:
    #         # The new random MAC is printed by the core function upon success
    #         print(f"Successfully set a random MAC for {interface}.")
    #     else:
    #         print(f"Failed to set random MAC for {interface}.")
    # else:
    #     print("Skipping set_random_mac example: root privileges required.")
```

## Error Handling
The tool includes checks for:
*   Invalid MAC address format.
*   Failures in executing `ifconfig` commands (e.g., interface not found, permission issues).
*   Verification that the MAC address was actually changed.
Detailed error messages are printed to the console to help diagnose issues.

## Operating System Support
Currently, MAC Address Changer is designed for **Linux** systems that use the `ifconfig` utility for network configuration. It may not work on systems that use `ip` (from `iproute2`) as the primary network configuration tool without modification, or on other operating systems like Windows or macOS.

## Contributing
Contributions are welcome! If you have suggestions for improvements, new features, or find any bugs, please feel free to:
1.  Open an issue in the repository.
2.  Fork the repository and submit a pull request with your changes.

## License
This project is licensed under the **MIT License**. You can find more details in a `LICENSE` file if one is included in the repository. (Assuming MIT License for now).
