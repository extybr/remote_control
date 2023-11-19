import paramiko
import threading
from scp import SCPClient
from pathlib import Path
from PyQt5 import QtWidgets, uic
from PyQt5.QtGui import QIcon, QIntValidator
from configuration_host import Host, ConfigHost


def thread(function):
    def run():
        threading.Thread(target=function).start()
    return run


def clear_lineedit() -> None:
    window_line = [window.lineEdit, window.lineEdit_2, window.lineEdit_3,
                   window.lineEdit_4, window.lineEdit_5, window.lineEdit_15]
    for item in window_line:
        item.clear()


def set_server_config() -> None:
    clear_lineedit()
    host = Host(window.comboBox.currentIndex())
    for number in range(1, len(host.length) + 1):
        if window.comboBox.currentIndex() == number:
            window.lineEdit.setText(host.host)  # host
            window.lineEdit_2.setText(str(host.port))  #
            window.lineEdit_4.setText(host.server)  # server name
            window.lineEdit_3.setText(host.user)  # user
            window.lineEdit_5.setText(host.password)  # password
            window.lineEdit_15.setText(host.private_file)  # private file


def get_host_variables() -> list:
    return [window.lineEdit.displayText(), window.lineEdit_2.displayText(),
            window.lineEdit_3.displayText(), window.lineEdit_4.displayText(),
            window.lineEdit_5.displayText(), window.lineEdit_15.displayText()]


def singleton(function):
    instances = {}

    def get_instances(*args, **kwargs):
        if function not in instances:
            instances[function] = function(*args, **kwargs)
        return instances[function]

    return get_instances


@singleton
def connect_to_server() -> paramiko.SSHClient:
    host = Host(window.comboBox.currentIndex())
    _variables = get_host_variables()
    path_file = Path(_variables[5]).absolute()
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    for number in range(len(host.length) + 1):
        if not all(_variables[:3]):
            window.textBrowser.clear()
            window.textBrowser.append('<h4>missing required data</h4>')
        if window.comboBox.currentIndex() == number:
            if path_file:
                key = paramiko.RSAKey.from_private_key_file(
                    filename=str(path_file),
                    password=_variables[4])
                client.connect(hostname=_variables[0], port=_variables[1],
                               username=_variables[2], pkey=key, timeout=5)
        if all(_variables[:3]) and not _variables[5] and _variables[4]:
            client.connect(hostname=_variables[0], port=_variables[1],
                           username=_variables[2], password=_variables[4],
                           timeout=5)
    return client


def command_execute(command: str) -> None:
    command = command if command else 'netstat -ntuop'
    window.textBrowser.clear()
    server = window.lineEdit.displayText()
    try:
        client = connect_to_server()
        stdin, stdout, stderr = client.exec_command(command)
        output = stdout.readlines()
        window.textBrowser.clear()
        for line in output:
            window.textBrowser.append(line.strip())
        window.textBrowser.scrollToAnchor("scroll")
    except TimeoutError as e:
        window.textBrowser.append(f'unable to connect to server: <h1>{server}'
                                  f'</h1> (<font color="red">{e})</font>')


def execute() -> None:
    command = window.lineEdit_6.displayText()
    try:
        command_execute(command=command)
    except Exception as e:
        window.textBrowser.append(str(e))


def get_variables() -> tuple:
    server_name = window.lineEdit_7.displayText()
    user = window.lineEdit_9.displayText()
    return server_name, user


def generate_text_keygen() -> str:
    server_name = get_variables()[0]
    text = (f"ssh-keygen -t rsa -b 2048 -C '{server_name.upper()}' -f "
            f"{server_name}")
    window.lineEdit_12.setText(text)
    return text


def set_keygen() -> None:
    keygen = window.lineEdit_12.displayText()
    config.set_keygen(keygen)


def set_config() -> None:
    port = pubkey_authentication = ''
    permit_root_login = password_authentication = ''
    if window.checkBox_5.isChecked():
        port = window.lineEdit_16.displayText()
    if window.checkBox.isChecked():
        pubkey_authentication = ('yes' if window.radioButton_3.isChecked()
                                 else 'no')
    if window.checkBox_4.isChecked():
        permit_root_login = 'yes' if window.radioButton_2.isChecked() else 'no'
    if window.checkBox_2.isChecked():
        password_authentication = ('yes' if window.radioButton_5.isChecked()
                                   else 'no')
    authorized_keys_file_path = (True if window.checkBox_3.isChecked()
                                 else False)
    path = window.lineEdit_11.displayText()
    try:
        config.set_config_change(server=window.lineEdit_7.displayText(),
                                 port=port,
                                 pubkey_authentication=pubkey_authentication,
                                 permit_root_login=permit_root_login,
                                 password_authentication=password_authentication,
                                 authorized_keys_file_path=authorized_keys_file_path,
                                 path=path)
        window.label_11.setText('success')
    except PermissionError:
        window.label_11.setText('forbidden! (!sudo)')


def move_and_change() -> None:
    from_ssh = window.lineEdit_13.displayText()
    to_ssh = window.lineEdit_14.displayText()
    server_name = window.lineEdit_7.displayText()
    user = window.lineEdit_9.displayText()
    config.move_and_change(from_ssh=from_ssh,
                           to_ssh=to_ssh,
                           user=user,
                           server=server_name)


def ping_host() -> None:
    window.textBrowser.clear()
    thread_ping_hosts()


@thread
def thread_ping_hosts() -> None:
    host = window.lineEdit.displayText()
    port = window.lineEdit_2.displayText()
    output = Host.ping_host(host=host, port=port)
    window.textBrowser.append(output.strip())


def select_from_path() -> None:
    file_path = QtWidgets.QFileDialog.getOpenFileName(
        window, 'Select a private file', '/home/')[0]
    window.lineEdit_13.setText(file_path)


def select_to_path() -> None:
    path = QtWidgets.QFileDialog.getExistingDirectory(
        window, 'Select the destination folder', '/home/')
    window.lineEdit_14.setText(path)


def select_private_file_path() -> None:
    file_path = QtWidgets.QFileDialog.getOpenFileName(
        window, 'Select a private file', '/home/')[0]
    window.lineEdit_15.setText(file_path)


def select_from_folder_copy() -> None:
    message = 'local destination folder'
    if window.checkBox_6.isChecked():
        message = 'local source folder'
    path = QtWidgets.QFileDialog.getExistingDirectory(
        window, message, '/home/')
    window.lineEdit_8.setText(path)


def generate_text_scp() -> None:
    _variables = get_host_variables()
    host = _variables[0]
    user = _variables[2]
    private_file = Path(_variables[5]).absolute()
    local_folder = Path(window.lineEdit_8.displayText()).absolute()
    window.lineEdit_10.setText(
        window.lineEdit_10.displayText().replace('{user}', user))
    remote_folder = window.lineEdit_10.displayText()
    reverse = False
    if window.checkBox_6.isChecked():
        reverse = True
    command = Host.generate_text_scp(host=host, user=user,
                                     private_file=str(private_file),
                                     local_folder=str(local_folder),
                                     remote_folder=remote_folder,
                                     reverse=reverse)
    window.lineEdit_17.setText(command)


def copy_scp() -> None:
    local_folder = Path(window.lineEdit_8.displayText()).absolute()
    remote_folder = window.lineEdit_10.displayText()
    try:
        client = connect_to_server()
        with SCPClient(client.get_transport()) as scp:
            if not window.checkBox_6.isChecked():
                scp.get(remote_folder, str(local_folder), recursive=True)
            elif window.checkBox_6.isChecked():
                local_file = local_folder
                scp.put(str(local_file), remote_folder, recursive=True)
        window.label_17.setText('successfully! copied')
    except Exception as e:
        window.lineEdit_17.setText(str(e))
        window.label_17.setText('error')


def functional() -> None:
    window.comboBox.addItems(Host(1).length)
    window.lineEdit_2.setValidator(QIntValidator(1, 65535, window))
    window.lineEdit_16.setValidator(QIntValidator(1, 65535, window))
    window.toolButton.clicked.connect(select_from_path)  # from (move)
    window.toolButton_2.clicked.connect(select_to_path)  # to (move)
    window.toolButton_3.clicked.connect(
        select_private_file_path)  # private file
    window.toolButton_4.clicked.connect(select_from_folder_copy)  # from (copy)
    window.pushButton.clicked.connect(execute)  # execute command
    window.pushButton_2.clicked.connect(set_keygen)  # execute keygen
    window.pushButton_3.clicked.connect(set_config)  # change sshd file
    window.pushButton_4.clicked.connect(config.restore_config)  # restore
    window.pushButton_5.clicked.connect(move_and_change)  # move
    window.pushButton_6.clicked.connect(
        config.service_config_reload)  # config reload
    window.pushButton_7.clicked.connect(ping_host)  # connect
    window.pushButton_8.clicked.connect(set_server_config)  # select (hide)
    window.pushButton_9.clicked.connect(config.save_backup)  # backup
    window.pushButton_10.clicked.connect(generate_text_keygen)  # generate
    window.pushButton_11.clicked.connect(generate_text_scp)  # generate (scp)
    window.pushButton_12.clicked.connect(copy_scp)  # execute (scp)
    window.show()
    app.setWindowIcon(QIcon('images/favicon.ico'))
    app.exec_()


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = uic.loadUi("ssh.ui")
    variable = get_variables()
    config = ConfigHost(server=variable[0], user=variable[1])
    functional()
