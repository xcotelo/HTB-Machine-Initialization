import os
import pwd
import subprocess
import sys
import time
import getpass
import glob
import signal
import re

ip = ""
vpn_process = None

if os.geteuid() != 0:
    try:
        args = ["sudo", sys.executable] + sys.argv
        os.execvp("sudo", args)
    except Exception as e:
        print("\033[1;31m✗ Failed to elevate privileges with sudo:\033[0m", e)
        sys.exit(1)

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


def detectar_dominio(target_ip):
    try:
        print(f"Detecting domain for {target_ip}...\n")

        result = subprocess.run(
            ["whatweb", "-a", "1", "--color=never", target_ip],
            capture_output=True,
            text=True,
            timeout=10
        )

        # Buscar patrones .htb en la salida
        output = result.stdout
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
    except Exception:
        return None


def limpiar_hosts():
    try:
        if ip:
            subprocess.run(["sudo", "sed", "-i", f"/{ip}/d", "/etc/hosts"], check=True)
            print(f"\033[1;32m✓ Entry {ip} removed from /etc/hosts\033[0m")
    except Exception as e:
        print(f"\033[1;31m✗ Error cleaning /etc/hosts: {e}\033[0m")


def stop_vpn():
    global vpn_process
    if vpn_process and vpn_process.poll() is None:
        try:
            print("Stopping VPN process...")
            # Terminate the whole process group
            os.killpg(os.getpgid(vpn_process.pid), signal.SIGTERM)
        except Exception:
            try:
                vpn_process.terminate()
            except Exception:
                pass


def cleanup_and_exit(signum=None, frame=None):
    stop_vpn()
    limpiar_hosts()
    sys.exit(0)


# Signal handlers which Ctrl+C cleans up
signal.signal(signal.SIGINT, cleanup_and_exit)
signal.signal(signal.SIGTERM, cleanup_and_exit)


def find_ovpn_files():
    return glob.glob("*.ovpn")


def start_vpn_background(archivo_ovpn):
    global vpn_process
    print(f"\033[1;32m✓ Starting VPN: {archivo_ovpn} (background)\033[0m\n")
    time.sleep(1.5)
    vpn_process = subprocess.Popen(["sudo", "openvpn", archivo_ovpn], preexec_fn=os.setsid)

    time.sleep(3)
    if vpn_process.poll() is None:
        print(f"\n\033[1;32m✓ VPN started (pid {vpn_process.pid})\033[0m\n")
    else:
        print(f"\033[1;31m✗ VPN process exited immediately\033[0m\n")


def main():
    global ip

    ovpn_files = find_ovpn_files()
    if not ovpn_files:
        print("\033[1;31m✗ There are no .ovpn files in the current directory.\033[0m")
        sys.exit(1)

    if len(ovpn_files) == 1:
        archivo_ovpn = ovpn_files[0]
    else:
        for i, archivo in enumerate(ovpn_files, start=1):
            print(f"{i}. {archivo}")
        numero = int(input("Which .ovpn file do you want to run? (Type number): ").strip())
        archivo_ovpn = ovpn_files[numero - 1]

    start_vpn_background(archivo_ovpn)

    try:
        ip = input("Enter the HTB machine IP: ").strip()
    except KeyboardInterrupt:
        cleanup_and_exit()

    dominio_detectado = detectar_dominio(ip)
    if dominio_detectado:
        nombre = dominio_detectado
    else:
        nombre = input("Enter a name for the machine (e.g. machine.htb): ").strip()

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

    # Create entry on /etc/hosts
    try:
        entrada = f"{ip} {nombre}\n"
        subprocess.run(["sudo", "bash", "-c", f"echo '{entrada}' >> /etc/hosts"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"\033[1;31m✗ Error adding entry to /etc/hosts: {e}\033[0m")

    print("\nAll setup steps completed. VPN is running in background.")
    print("Press Ctrl+C to stop the VPN and clean /etc/hosts.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        cleanup_and_exit()


if __name__ == "__main__":
    main()
