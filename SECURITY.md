# Security Policy

## Supported Versions

Use this section to tell people about which versions of your project are
currently being supported with security updates.

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

If you discover a security vulnerability within this project, please open an issue on GitHub with a clear description of the vulnerability and steps to reproduce it. We appreciate your efforts to disclose your findings responsibly. You can typically expect an acknowledgment within 48-72 hours and periodic updates on the status of a reported vulnerability.

---

## Security Considerations for `mac-changer`

The `mac-changer` tool, while useful for certain network testing and privacy exploration scenarios, comes with significant security implications that users must understand and respect.

### Responsible Usage
*   **Authorization Required:** This tool should **only** be used on networks and devices for which you have explicit, prior authorization.
*   **Compliance with Policies:** Unauthorized MAC address changes can violate Terms of Service (ToS) of network providers, company policies, or other network usage agreements. Always ensure your actions are compliant with all applicable policies.

### Legal and Ethical Implications
*   **Potential for Misuse:** Changing MAC addresses can be used in ways that may be illegal or unethical in certain jurisdictions or situations (e.g., to circumvent access controls, impersonate other devices, or hide malicious activity).
*   **User Responsibility:** Users are solely responsible for ensuring their use of this tool is lawful and ethical within their jurisdiction and context. Ignorance of the law is not an excuse.

### Anonymity Limitations
*   **Not a Complete Anonymity Solution:** While MAC spoofing can alter one layer of network identification, it is **not** a comprehensive anonymity solution.
*   **Other Identifiers:** Your network traffic, browser fingerprints, user accounts, and other digital traces can still be used to identify you or your device.
*   **Detection:** MAC spoofing can sometimes be detected by sophisticated network monitoring or by inconsistencies (e.g., a MAC address associated with one vendor appearing on hardware from another).

### Potential for Network Disruption
*   **Incorrect MAC Addresses:** Setting an improper or malformed MAC address can lead to loss of network connectivity for your device.
*   **MAC Address Conflicts:** Changing your MAC address to one that is already in use on the local network can cause IP address conflicts and network disruptions for both your device and the device you are impersonating.
*   **Reserved/Multicast Addresses:** Using a multicast address as a source MAC address or using reserved MAC addresses can have unpredictable and disruptive effects on network behavior.

### Administrative Privileges
*   **Root/Sudo Required:** This tool requires administrative (root/sudo) privileges to execute the underlying `ifconfig` commands necessary for modifying network interface settings.
*   **Risks of Elevated Privileges:** Users should be aware of the risks associated with running any software with elevated privileges. Only run trusted software as root, as malicious software running with such permissions can compromise the entire system. Ensure you understand the commands being executed by the tool.

### Secure Development
*   **Input Validation:** The tool implements input validation for MAC address formats to prevent command injection or malformed commands. However, all software can contain bugs.
*   **Limited Scope of System Interaction:** The tool is designed to interact with the system primarily through `ifconfig` commands. Its scope of direct system modification is limited to what `ifconfig` allows.

Users should exercise caution and understand these considerations before using the `mac-changer` tool.
