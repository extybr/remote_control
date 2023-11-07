import paramiko
from pathlib import Path
from config import Config, load_config

conf: Config = load_config('.env')
host: conf = conf.conf.host
port: conf = conf.conf.port
user: conf = conf.conf.user
secret: conf = conf.conf.password
private_file: conf = conf.conf.filename

path_file = (Path('private') / private_file).absolute()
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
key = paramiko.RSAKey.from_private_key_file(filename=str(path_file),
                                            password=secret)
client.connect(hostname=host, port=port, username=user, pkey=key)
stdin, stdout, stderr = client.exec_command('netstat -ntuop')
output = stdout.readlines()
for line in output:
    print(line.strip())
client.close()

