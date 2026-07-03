<div align="center">

# HTB Machine Initialization

</div>

<div align="center">
  <img width="623" height="329" alt="image" src="https://github.com/user-attachments/assets/77107ed3-05a2-472d-b87b-597abaf307ba" />
</div>

## What it does

- Starts OpenVPN with your `.ovpn` file
- Creates `HTB_<machine>` folder with `nmap/`, `exploit/`, and `varios/` subfolders
- Adds `IP machine.htb` to `/etc/hosts`
- Creates Python virtual environment `.venv`
- `Ctrl+C` → stops VPN and removes the `/etc/hosts` entry

```bash
python3 MachineInitialization.py
```

Just enter the machine IP and name when prompted.