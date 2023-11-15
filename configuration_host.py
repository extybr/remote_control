import os
from platform import system
from subprocess import run, getoutput
from shutil import copy, move
from dotenv import load_dotenv

load_dotenv()


class Host:
    def __init__(self, number: int) -> None:
        self.length = os.getenv('SERVER').split(',')
        self.host = os.getenv('HOST').split(',')[number - 1]
        self.port = int(os.getenv('PORT').split(',')[number - 1])
        self.user = os.getenv('USERS').split(',')[number - 1]
        self.server = os.getenv('SERVER').split(',')[number - 1]
        self.password = os.getenv('PASSWORD').split(',')[number - 1]
        self.private_file = f'private/{self.server}'

    @staticmethod
    def ping_host(host: str, port: str = 0) -> str:
        result = ''
        system_os = system()
        if system_os == 'Windows':
            system_encoding = getoutput('chcp').split(' ')[-1]
            result += getoutput(f"ping -n 3 {host}", encoding=system_encoding)
            return result
        elif system_os == 'Linux':
            result = getoutput(f"ping -c3 {host}")
            if port:
                nmap = 'nmap -Pn -p '
                result += '\n\n' + getoutput(f'{nmap}{port} {host}')
            return result
        return 'unknown system'

    @staticmethod
    def generate_text_scp(private_file: str, local_folder: str, user: str,
                          host: str, remote_folder: str,
                          reverse: bool) -> str:
        _remote_folder = f'{user}@{host}:{remote_folder}'
        if not reverse:
            _remote_folder, local_folder = local_folder, _remote_folder
        cmd = f'scp -i {private_file} -r {local_folder} {_remote_folder}'
        return cmd


class ConfigHost:
    def __init__(self, server: str, user: str) -> None:
        self.server = server
        self.user = user
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
                          port: str = '',
                          pubkey_authentication: str = '',
                          permit_root_login: str = '',
                          password_authentication: str = '',
                          authorized_keys_file_path: bool = True,
                          path: str = '') -> None:
        config = {"#Port 22": f"Port {port.strip()}\n",
                  "#PermitRootLogin": "PermitRootLogin no\n",
                  "#PubkeyAuthentication": "PubkeyAuthentication yes\n",
                  "#AuthorizedKeysFile": (f"AuthorizedKeysFile .ssh/"
                                          f"{server}.pub\n"),
                  "#PasswordAuthentication": "PasswordAuthentication no\n"}
        if not port or not port.strip().isdigit():
            del config["#Port 22"]
        if not authorized_keys_file_path:
            del config["#AuthorizedKeysFile"]
        elif authorized_keys_file_path:
            if path != '.ssh/{server}.pub' and path.strip() != '':
                config["#AuthorizedKeysFile"] = f"AuthorizedKeysFile {path}\n"
        if pubkey_authentication:
            if pubkey_authentication == 'no':
                config['#PubkeyAuthentication'] = "PubkeyAuthentication no\n"
        elif not pubkey_authentication:
            del config['#PubkeyAuthentication']
        if permit_root_login:
            if permit_root_login == 'yes':
                config["#PermitRootLogin"] = "PermitRootLogin yes\n"
        elif not permit_root_login:
            del config["#PermitRootLogin"]
        if password_authentication:
            if password_authentication == 'yes':
                config["#PasswordAuthentication"] = "PasswordAuthentication yes\n"
        elif not password_authentication:
            del config["#PasswordAuthentication"]
        ConfigHost.change_config(self, config)

    def change_config(self, _config):
        text: list = []
        with open(self.sshd_config, 'r') as config:
            text = config.readlines()
        with open(self.sshd_config, 'w') as config:
            text.reverse()
            while text:
                string = text.pop()
                for key in _config:
                    if string.startswith(key):
                        string = _config[key]
                config.writelines(string)

    @staticmethod
    def move_and_change(from_ssh: str,
                        to_ssh: str,
                        user: str,
                        server: str) -> None:
        # home_ssh = f'/home/{user}/.ssh'
        if os.path.exists(from_ssh) and os.path.isfile(from_ssh):
            if not os.path.exists(to_ssh):
                os.mkdir(to_ssh)
            if os.path.exists(to_ssh) and os.path.isdir(to_ssh):
                move(from_ssh, to_ssh)
            if os.path.exists(from_ssh + '.pub') and os.path.isfile(from_ssh + '.pub'):
                move(from_ssh + '.pub', to_ssh)
            if os.path.exists(to_ssh + server) or os.path.exists(f'{to_ssh}/{server}'):
                if not to_ssh.endswith('/'):
                    to_ssh = to_ssh + '/'
                cmd = [f"chmod 700 {to_ssh}",
                       f"chmod 600 {to_ssh}{server}*"]
                [run(i, shell=True) for i in cmd]
                if user:
                    cmd = f'chown {user}:{user} {to_ssh}{server}*'
                    run(cmd, shell=True)

    @staticmethod
    def service_config_reload() -> None:
        cmd = 'sudo systemctl reload sshd'
        run(cmd, shell=True)
