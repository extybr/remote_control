from subprocess import run
from os import getenv, mkdir
from shutil import copy, move
from dotenv import load_dotenv

load_dotenv()


class Host:
    def __init__(self, number: int) -> None:
        self.length = getenv('SERVER').split(',')
        self.host = getenv('HOST').split(',')[number - 1]
        self.port = int(getenv('PORT').split(',')[number - 1])
        self.user = getenv('USER').split(',')[number - 1]
        self.server = getenv('SERVER').split(',')[number - 1]
        self.password = getenv('PASSWORD').split(',')[number - 1]
        self.private_file = f'private/{self.server}'

    @staticmethod
    def connect(server_name: str, user: str, host: str, port: str) -> None:
        cmd = f"ssh -i {server_name} {user}@{host}:{port}"
        run(cmd, shell=True)


class ConfigHost:
    def __init__(self, server: str, port: str, user: str, password: str) -> None:
        self.server = server
        self.port = port
        self.user = user
        self.password = password
        self.sshd_config = "/etc/ssh/sshd_config"
        self.etc_ssh = '/etc/ssh/'

    def save_backup(self) -> None:
        copy(self.sshd_config, self.sshd_config + '.backup')

    def restore_config(self) -> None:
        copy(self.sshd_config + '.backup', self.sshd_config)

    @staticmethod
    def set_keygen(text: str) -> None:
        if text.startswith('ssh-keygen'):
            run(text, shell=True)

    def set_config_change(self, server: str,
                          pubkey_authentication: str = '',
                          permit_root_login: str = '',
                          password_authentication: str = '',
                          authorized_keys_file_path: bool = True,
                          path: str = '') -> None:
        change = {"#PermitRootLogin": "PermitRootLogin no\n",
                  "#PubkeyAuthentication": "PubkeyAuthentication yes\n",
                  "#AuthorizedKeysFile": (f"AuthorizedKeysFile .ssh/"
                                          f"{server}.pub\n"),
                  "#PasswordAuthentication": "PasswordAuthentication no\n"}
        if not authorized_keys_file_path:
            del change["#AuthorizedKeysFile"]
        elif authorized_keys_file_path:
            if path != '.ssh/{server}.pub':
                change["#AuthorizedKeysFile"] = f"AuthorizedKeysFile {path}\n"
        if pubkey_authentication:
            if pubkey_authentication == 'no':
                change['#PubkeyAuthentication'] = "PubkeyAuthentication no\n"
        elif not pubkey_authentication:
            del change['#PubkeyAuthentication']
        if permit_root_login:
            if permit_root_login == 'yes':
                change["#PermitRootLogin"] = "PermitRootLogin yes\n"
        elif not permit_root_login:
            del change["#PermitRootLogin"]
        if password_authentication:
            if password_authentication == 'yes':
                change["#PasswordAuthentication"] = "PasswordAuthentication yes\n"
        elif not password_authentication:
            del change["#PasswordAuthentication"]
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

    def move_and_change(self, from_ssh: str,
                        to_ssh: str,
                        user: str,
                        server: str) -> None:
        # home_ssh = f'/home/{user}/.ssh'
        from_path = from_ssh if from_ssh else self.etc_ssh + server
        if to_ssh.startswith('/home/'):
            mkdir(to_ssh)
            move(from_path, to_ssh)
            move(from_path + '.pub', to_ssh)
            cmd = [f"cd {to_ssh}",
                   f"chmod 600 {server}*",
                   f"chown {user}:{user} {server}*",
                   f"systemctl reload sshd"]
            [run(i, shell=True) for i in cmd]

    @staticmethod
    def service_config_reload() -> None:
        cmd = 'systemctl reload ssh'
        run(cmd, shell=True)
