from subprocess import run
from os import getenv, mkdir
from shutil import copy, move
from dotenv import load_dotenv

load_dotenv()


class Host:
    def __init__(self, number):
        self.length = getenv('SERVER').split(',')
        self.host = getenv('HOST').split(',')[number - 1]
        self.port = int(getenv('PORT').split(',')[number - 1])
        self.user = getenv('USER').split(',')[number - 1]
        self.server = getenv('SERVER').split(',')[number - 1]
        self.password = getenv('PASSWORD').split(',')[number - 1]
        self.private_file = f'private/{self.server}'

    @staticmethod
    def connect(server_name, user, host, port):
        cmd = f"ssh -i {server_name} {user}@{host}:{port}"
        run(cmd, shell=True)


class ConfigHost:
    def __init__(self, server: str, port: int, user: str, password: str):
        self.server = server
        self.port = port
        self.user = user
        self.password = password
        self.sshd_config = "/etc/ssh/sshd_config"
        self.etc_ssh = '/etc/ssh/'

    def save_backup(self) -> None:
        copy(self.sshd_config, self.sshd_config + '.backup')

    @staticmethod
    def set_keygen(text: str) -> None:
        if text.startswith('ssh-keygen'):
            run(text, shell=True)

    def set_config_change(self, server: str) -> None:
        change = {"#PermitRootLogin": "PermitRootLogin no\n",
                  "#PubkeyAuthentication": "PubkeyAuthentication yes\n",
                  "#AuthorizedKeysFile": (f"AuthorizedKeysFile .ssh/"
                                          f"{server}.pub\n"),
                  "#PasswordAuthentication": "PasswordAuthentication no\n"}
        text: list = []
        with open(self.sshd_config, 'r') as config:
            text = config.readlines()
        with open(self.sshd_config, 'w') as config:
            text.reverse()
            while text:
                string = text.pop()
                for key in change:
                    if string.startswith(key):
                        string = change[key]
                config.writelines(string)

    def sed_config_change(self, server: str) -> None:
        """
        Variant 2. GNU CoreUtils: sed
        :param server: str
        :return: None
        """
        change = {"#PermitRootLogin": "PermitRootLogin no\n",
                  "#PubkeyAuthentication": "PubkeyAuthentication yes\n",
                  "#AuthorizedKeysFile": (f"AuthorizedKeysFile .ssh/"
                                          f"{server}.pub\n"),
                  "#PasswordAuthentication": "PasswordAuthentication no\n"}
        for key, value in change.items():
            run(f"sed -i 'c/{key}/{value[:-2]}' {self.sshd_config}")

    def move_and_change(self, home_ssh: str, user: str, server: str) -> None:
        # home_ssh = f'/home/{user}/.ssh'
        if home_ssh.startswith('/home/'):
            mkdir(home_ssh)
            move(self.etc_ssh + server, home_ssh)
            move(self.etc_ssh + server + '.pub', home_ssh)
            cmd = [f"cd {home_ssh}",
                   f"chmod 600 {server}*",
                   f"chown {user}:{user} {server}*",
                   f"systemctl reload sshd"]
            [run(i, shell=True) for i in cmd]
