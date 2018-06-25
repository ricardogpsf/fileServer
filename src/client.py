import socket

from src.services.file_handler import FileHandler
from src.services.security_service import SecurityService

SIZE_TO_RECEIVE_STREAM = 1024


class ClientService:

    def __init__(self, host='127.0.0.1', port=5000):
        self.host = host
        self.port = port
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.security = None

    def start(self):
        self.security = SecurityService()
        self.conn.connect((self.host, self.port))

        data = self.conn.recv(SIZE_TO_RECEIVE_STREAM)
        print("Recebendo data {}".format(data.decode()))
        self.conn.send(str(self.security.pub_key).encode())
        self.security.set_friend_pub_key(data.decode())

        self.send_option('menu')
        self.receive_simple_text()
        while True:
            option = input("\n Digite a opção:\n")
            value = option.split(' ')[0]
            if value == '1':
                self.send_option(value)
                self.receive_simple_text()
            elif value == '2':
                self.upload_file(option)
            elif value == '3':
                self.download_file(option)
            elif value == 'exit':
                self.send_option("exit")
                break
            else:
                self.send_option('menu')
                self.receive_simple_text()

    def receive_simple_text(self):
        data = self.conn.recv(SIZE_TO_RECEIVE_STREAM)
        data = self.security.decrypt(data)
        print(data.decode() + '\n')

    def send_option(self, option_text):
        msg = self.security.encrypt(option_text.encode())
        self.conn.send(msg)

    def download_file(self, option_text):
        self.send_option(option_text)
        file_path = './downloaded/' + option_text.split(' ')[1]
        FileHandler(file_path, self.conn, self.security).handle_download_file()

    def upload_file(self, option_text):
        self.send_option(option_text)
        file_name = option_text.split(' ')[1]
        FileHandler('./downloaded/' + file_name, self.conn, self.security).handle_upload_file()


if __name__ == '__main__':
    ClientService().start()
