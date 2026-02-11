import os
import pwd
import subprocess
import sys
import time
import getpass
import glob
ip = ""

print("""
\033[1;32m╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   ██╗  ██╗████████╗██████╗     ███╗   ███╗██╗████████╗       ║
║   ██║  ██║╚══██╔══╝██╔══██╗    ████╗ ████║██║╚══██╔══╝       ║
║   ███████║   ██║   ██████╔╝    ██╔████╔██║██║   ██║          ║
║   ██╔══██║   ██║   ██╔══██╗    ██║╚██╔╝██║██║   ██║          ║
║   ██║  ██║   ██║   ██████╔╝    ██║ ╚═╝ ██║██║   ██║          ║
║   ╚═╝  ╚═╝   ╚═╝   ╚═════╝     ╚═╝     ╚═╝╚═╝   ╚═╝          ║
║                                                              ║
║                                                              ║
║   \033[1;33m	  Hack The Box – Machine Initialization Tool\033[1;32m           ║
║                                                              ║
║                       \033[1;35mby @xcotelo\033[1;32m                            ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝\033[0m
""")

print("\033[1;33m⚠  IMPORTANT: Press Ctrl+C to terminate VPN connection and clean /etc/hosts\033[0m\n")

def limpiar_hosts():    
    try:
        subprocess.run(["sudo", "sed", "-i", f"/{ip}/d", "/etc/hosts"], check=True)        
        print(f"✓ Entry {ip} removed from /etc/hosts")
    except Exception as e:
        print(f"✗ Error cleaning /etc/hosts: {e}")
    sys.exit(0)

try:
    ip = input("Enter the HTB machine IP: ").strip()
    nombre = input("Enter a name for the machine (e.g. machine.htb): ").strip()

except KeyboardInterrupt:
    sys.exit(0)

nombre_carpeta = nombre.replace(".htb", "")
usuario = os.getenv("SUDO_USER") or getpass.getuser()
ruta_base = (f"/home/{usuario}/HTB_{nombre_carpeta}")

if os.path.exists(ruta_base):
	print("The directory {ruta_base} already exists.")
else:
	subcarpetas = ["nmap", "exploit", "varios"]
	os.makedirs(ruta_base, exist_ok=True)

	# Crear subcarpetas dentro de "HTB"
	for carpeta in subcarpetas:
    		ruta_sub = os.path.join(ruta_base, carpeta)
    		os.makedirs(ruta_sub, exist_ok=True)

	# Permisos de usuario a carpeta base y subcarpetas
	uid_usuario = pwd.getpwnam(usuario).pw_uid
	gid_usuario = pwd.getpwnam(usuario).pw_gid

	os.chown(ruta_base, uid_usuario, gid_usuario)
	for carpeta in subcarpetas:
		ruta_sub = os.path.join(ruta_base, carpeta)
		os.chown(ruta_sub, uid_usuario, gid_usuario)

# Crear entrada en /etc/hosts
try:
    entrada = f"{ip} {nombre}\n"
    subprocess.run(["sudo", "bash", "-c", f"echo '{entrada}' >> /etc/hosts"], check=True)
except subprocess.CalledProcessError as e:
    print(f"✗ Error adding entry to /etc/hosts: {e}")

try:
	# Busco por los archivos .ovpn
	ovpn_files = glob.glob("*.ovpn")
	
	if not ovpn_files:
		print("There are no .ovpn files")
		print("Exiting...")
		sys.exit(1)
	else:
		contador = 1
		for archivo in ovpn_files:
			print(f"{contador}. {archivo}")
			contador += 1
			
	if len(ovpn_files) == 1:
		archivo_ovpn = ovpn_files[0]
		procesoVPN = subprocess.Popen(["sudo", "openvpn", archivo_ovpn])
	else:
		numero = int(input("Which .ovpn file do you want to run? (Type number): ").strip())		
		archivo_ovpn = ovpn_files[numero -1]
		# Usar Popen y esperar manualmente para capturar Ctrl+C
		procesoVPN = subprocess.Popen(["sudo", "openvpn", archivo_ovpn])

except KeyboardInterrupt:
    print("\nCtrl+C detected. Closing VPN...")

finally:
    if 'procesoVPN' in locals() and procesoVPN.poll() is None:
        print("Stopping VPN process...")
        procesoVPN.terminate()
        try:
            procesoVPN.wait(timeout=5)
        except subprocess.TimeoutExpired:
            procesoVPN.kill()

    limpiar_hosts()
