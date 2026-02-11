import os
import pwd
import subprocess
import sys
import time
import getpass
import glob
import time
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
║   \033[1;33m      Hack The Box – Machine Initialization Tool\033[1;32m           ║
║                                                              ║
║                       \033[1;35mby @xcotelo\033[1;32m                            ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝\033[0m
""")

print("\033[1;33m⚠  IMPORTANT: Press Ctrl+C to terminate VPN connection and clean /etc/hosts\033[0m\n")

def detectar_dominio(ip):
    try:
        print(f"Detecting domain for {ip}...\n")

        result = subprocess.run(
            ["whatweb", "-a", "1", "--color=never", ip],
            capture_output=True,
            text=True,
            timeout=10
        )

        # Buscar patrones .htb en la salida
        output = result.stdout
        import re
        match = re.search(r'([a-zA-Z0-9-]+\.htb)', output)

        if match:
            dominio = match.group(1)
            print(f"\033[1;32m✓ Domain detected: {dominio}\033[0m\n")
            return dominio
        else:
            print("\033[1;31m✗ No .htb domain detected\033[0m\n")
            return None

    except subprocess.TimeoutExpired:
        print("\033[1;33m✗ Timeout detecting domain\033[0m\n")
        return None
    except FileNotFoundError:
        print("\033[1;33m⚠ whatweb is not installed. Install it with: sudo apt install whatweb\033[0m\n")
        return None
    except Exception as e:
        return None

def limpiar_hosts():
    try:
        subprocess.run(["sudo", "sed", "-i", f"/{ip}/d", "/etc/hosts"], check=True)
        print(f"\033[1;32m✓ Entry {ip} removed from /etc/hosts\033[0m")
    except Exception as e:
        print(f"\033[1;31m✗ Error cleaning /etc/hosts: {e}\033[0m")
    sys.exit(0)

try:
    ip = input("Enter the HTB machine IP: ").strip()
    dominio_detectado = detectar_dominio(ip)
    if dominio_detectado:
        nombre=dominio_detectado
    else:
        nombre = input("Enter a name for the machine (e.g. machine.htb): ").strip();
except KeyboardInterrupt:
    sys.exit(0)

nombre_carpeta = nombre.replace(".htb", "")
usuario = os.getenv("SUDO_USER") or getpass.getuser()
ruta_base = (f"/home/{usuario}/HTB_{nombre_carpeta}")

if os.path.exists(ruta_base):
    print(f"The directory {ruta_base} already exists.\n")
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
    print(f"\033[1;31m✗ Error adding entry to /etc/hosts: {e}\033[0m")

try:
    # Busco por los archivos .ovpn
    ovpn_files = glob.glob("*.ovpn")

    if not ovpn_files:
        print("\033[1;31m✗ There are no .ovpn files\033[0m")
        print("Exiting...")
        sys.exit(1)
    else:

        if len(ovpn_files) == 1:
            archivo_ovpn = ovpn_files[0]
            print(f"\033[1;32m✓ Executing {archivo_ovpn}\033[0m\n")
            time.sleep(1.5)
            procesoVPN = subprocess.Popen(["sudo", "openvpn", archivo_ovpn])
            procesoVPN.wait()
        else:
            contador = 1
            for archivo in ovpn_files:
                print(f"{contador}. {archivo}")
                contador += 1

            numero = int(input("Which .ovpn file do you want to run? (Type number): ").strip())
            archivo_ovpn = ovpn_files[numero - 1]
            print(f"\033[1;32m✓ Executing {archivo_ovpn}\033[0m\n")
            time.sleep(1.5)
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
