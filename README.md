# HTB Machine Initialization

A small Python script to automate the setup of a lab machine (e.g., HackTheBox).
It creates a folder structure, adds the entry to `/etc/hosts`, and launches a VPN. Pressing `Ctrl+C` removes the added entry from `/etc/hosts`.

---

## Usage

The script will ask for:

* The machine's IP address (e.g., `10.10.10.5`)
* The machine's name (e.g., `machine.htb`)

What it does automatically:

* Creates `/home/USER/HTB_<name_without_.htb>` with subfolders `nmap`, `exploit`, and `various`.
* Adds the line `IP name` to `/etc/hosts`.
* Runs `sudo openvpn HTBfile.ovpn`.
* If you press `Ctrl+C`:

     * Stop the VPN.
     * Remove the entry added to `/etc/hosts`.
