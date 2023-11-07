import paramiko
import os
import io
from dotenv import load_dotenv

load_dotenv()
host = os.getenv('HOST')
port = int(os.getenv('PORT'))
user = os.getenv('USER')
password = os.getenv('PASSWORD')
key = io.StringIO(os.getenv('KEY'))
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
string = paramiko.RSAKey.from_private_key(file_obj=key, password=password)
client.connect(hostname=host, port=port, username=user, pkey=string)
stdin, stdout, stderr = client.exec_command('netstat -ntuop')
output = stdout.readlines()
for line in output:
    print(line.strip())
client.close()

