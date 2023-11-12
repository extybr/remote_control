import paramiko
from pathlib import Path
from PyQt5 import QtWidgets, uic
from PyQt5.QtGui import QIcon
from configuration_host import Host, ConfigHost


def set_server_config() -> None:
    window_line = [window.lineEdit, window.lineEdit_2, window.lineEdit_3,
                   window.lineEdit_4, window.lineEdit_5, window.lineEdit_15]
    for item in window_line:
        item.clear()
    host = Host(window.comboBox.currentIndex())
    for number in range(1, len(host.length) + 1):
        if window.comboBox.currentIndex() == number:
            window.lineEdit.setText(host.host)  # host
            window.lineEdit_2.setText(str(host.port))  #
            window.lineEdit_4.setText(host.server)  # server name
            window.lineEdit_3.setText(host.user)  # user
            window.lineEdit_5.setText(host.password)  # password
            window.lineEdit_15.setText(host.private_file)  # private file


def command_execute(command: str) -> None:
    command = command if command else 'netstat -ntuop'
    window.textBrowser.clear()
    host = Host(window.comboBox.currentIndex())
    for number in range(1, len(host.length) + 1):
        if window.comboBox.currentIndex() == number:
            path_file = Path(window.lineEdit_15.displayText()).absolute()
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            key = paramiko.RSAKey.from_private_key_file(filename=str(path_file),
                                                        password=host.password)
            client.connect(hostname=host.host, port=host.port,
                           username=host.user, pkey=key)
            stdin, stdout, stderr = client.exec_command(command)
            output = stdout.readlines()
            window.textBrowser.clear()
            for line in output:
                window.textBrowser.append(line.strip())
            client.close()


def execute() -> None:
    command = window.lineEdit_6.displayText()
    command_execute(command=command)


def get_variables() -> tuple:
    server_name = window.lineEdit_7.displayText()
    port = window.lineEdit_8.displayText()
    user = window.lineEdit_9.displayText()
    password = window.lineEdit_10.displayText()
    return server_name, port, user, password


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
    pubkey_authentication = permit_root_login = password_authentication = ''
    if window.checkBox.isChecked():
        pubkey_authentication = 'yes' if window.radioButton_3.isChecked() else 'no'
    if window.checkBox_4.isChecked():
        permit_root_login = 'yes' if window.radioButton_2.isChecked() else 'no'
    if window.checkBox_2.isChecked():
        password_authentication = 'yes' if window.radioButton_5.isChecked() else 'no'
    authorized_keys_file_path = True if window.checkBox_3.isChecked() else False
    path = window.lineEdit_11.displayText()
    config.set_config_change(server=window.lineEdit_7.displayText(),
                             pubkey_authentication=pubkey_authentication,
                             permit_root_login=permit_root_login,
                             password_authentication=password_authentication,
                             authorized_keys_file_path=authorized_keys_file_path,
                             path=path)


def move_and_change() -> None:
    from_ssh = window.lineEdit_13.displayText()
    to_ssh = window.lineEdit_14.displayText()
    server_name = window.lineEdit_7.displayText()
    user = window.lineEdit_9.displayText()
    config.move_and_change(from_ssh=from_ssh,
                           to_ssh=to_ssh,
                           user=user,
                           server=server_name)


def connect() -> None:
    server_name = window.lineEdit_4.displayText()
    user = window.lineEdit_3.displayText()
    host = window.lineEdit.displayText()
    port = window.lineEdit_2.displayText()
    Host.connect(server_name=server_name, user=user, host=host, port=port)


def select_from_path():
    file_path = QtWidgets.QFileDialog.getOpenFileName(
        window, 'Open file', '/home/')[0]
    window.lineEdit_13.setText(file_path)


def select_to_path():
    path = QtWidgets.QFileDialog.getExistingDirectory(
        window, 'Open folder', '/home/')
    window.lineEdit_14.setText(path)


def select_private_file_path():
    file_path = QtWidgets.QFileDialog.getOpenFileName(
        window, 'Open file', '/home/')[0]
    window.lineEdit_15.setText(file_path)


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = uic.loadUi("ssh.ui")
    window.comboBox.addItems(Host(1).length)
    window.pushButton_8.clicked.connect(set_server_config)  # select
    window.pushButton_7.clicked.connect(connect)
    window.pushButton.clicked.connect(execute)  # execute command
    variable = get_variables()
    config = ConfigHost(server=variable[0], port=variable[1],
                        user=variable[2], password=variable[3])
    window.toolButton.clicked.connect(select_from_path)
    window.toolButton_2.clicked.connect(select_to_path)
    window.toolButton_3.clicked.connect(select_private_file_path)
    window.pushButton_10.clicked.connect(generate_text_keygen)  # generate
    window.pushButton_2.clicked.connect(set_keygen)  # execute keygen
    window.pushButton_9.clicked.connect(config.save_backup)  # backup
    window.pushButton_3.clicked.connect(set_config)  # change sshd file
    window.pushButton_5.clicked.connect(move_and_change)  # move
    window.pushButton_4.clicked.connect(config.restore_config)  # restore
    window.pushButton_6.clicked.connect(config.service_config_reload)  # config reload
    app.setWindowIcon(QIcon('images/favicon.ico'))
    window.show()
    app.exec_()
