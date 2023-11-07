import subprocess
import os
from dotenv import load_dotenv

load_dotenv()

HOST = os.getenv('HOST')
PORT = int(os.getenv('PORT'))
USER = os.getenv('USER')
SERVER = os.getenv('SERVER')

CHANGE = {"#PermitRootLogin": "PermitRootLogin no\n",
          "#PubkeyAuthentication": "PubkeyAuthentication yes\n",
          "#AuthorizedKeysFile": f"AuthorizedKeysFile .ssh/"
          f"{SERVER}.pub\n",
          "#PasswordAuthentication": "PasswordAuthentication no\n"}

# SSHD_CONFIG = "/etc/ssh/sshd_config"
SSHD_CONFIG = "ssh/sshd"


def set_keygen():
    keygen = f"ssh-keygen -t rsa -b 2048 -C '{SERVER.upper()}' -f {SERVER}"
    subprocess.run(keygen, shell=True)


def set_config_change():
    text: list = []
    with open(SSHD_CONFIG, 'r') as config:
        text = config.readlines()
    with open(SSHD_CONFIG, 'w') as config:
        text.reverse()
        while text:
            string = text.pop()
            for key in CHANGE:
                if string.startswith(key):
                    string = CHANGE[key]
            config.writelines(string)


def sed_config_change():
    for key, value in CHANGE.items():
        subprocess.run(f"sed -i 'c/{key}/{value[:-2]}' {SSHD_CONFIG}")


def connect(path):
    cmd = [f"cd {path}", f"chmod 600 {SERVER}",
           f"chmod 600 {SERVER}.pub",
           f"systemctl reload sshd",
           f"ssh -i {SERVER} {USER}@{HOST}:{PORT}"]
    [subprocess.run(i, shell=True) for i in cmd]


if __name__ == '__main__':
    set_config_change()
