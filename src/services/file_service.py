import hashlib
import os
import socket
import threading

from src.services.file_handler import FileHandler
from src.services.security_service import SecurityService

SIZE_TO_RECEIVE_STREAM = 1024


class FileService:

    def __init__(self, host='127.0.0.1', port=5000):
        self.host = host
        self.port = port
        self.can_continue = True

    def start(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((self.host, self.port))
        server.listen(10)
        print('Waiting connection...')
        while self.can_continue:
            conn, addr = server.accept()
            t = threading.Thread(target=self.handle_connection, args=(conn, addr))
            t.start()

    def stop(self):
        self.can_continue = False

    def handle_connection(self, client_conn, addr):
        print('Connected to {}'.format(addr))

        security = SecurityService()
        pub_key = str(security.pub_key).encode()
        print('Sharing pub.key {} to {}'.format(pub_key, addr))
        client_conn.send(pub_key)
        pub_key_received = client_conn.recv(SIZE_TO_RECEIVE_STREAM)
        security.set_friend_pub_key(pub_key_received.decode())

        while True:
            data_received = client_conn.recv(SIZE_TO_RECEIVE_STREAM)
            print('Data received {} from {}'.format(data_received, addr))
            if data_received:
                data = security.decrypt(data_received).decode()
                option = data.split(' ')[0]

                if option == '1':
                    self.list_files(client_conn, security)
                elif option == '2':
                    file_name = data.split(' ')[1]
                    self.receive_file(client_conn, security, file_name)
                elif option == '3':
                    file_name = data.split(' ')[1]
                    self.send_file(client_conn, security, file_name)
                elif option == 'exit':
                    print('Disconnected {}'.format(addr))
                    client_conn.close()
                    break
                else:
                    self.send_message(client_conn, security, self.show_menu())

    def send_message(self, conn, security, msg_text):
        conn.send(security.encrypt(msg_text.encode()))

    def show_menu(self):
        return "(1) Listar arquivos (Ex: 1) \n" \
               "(2) Upload de arquivo (Ex.: 2 nome_do_arquivo.txt) \n" \
               "(3) Download de arquivo (Ex.: 3 nome_do_arquivo.txt) \n" \
               "(*) Menu (Ex.: 4) \n" \
               "(exit) Sair (ex.: exit)"

    def list_files(self, client_conn, security):
        print('Listing files...')
        descriptions = []
        files = os.listdir("./public")
        for file_name in files:
            hasher = hashlib.md5()
            with open('./public/' + file_name, 'rb') as afile:
                buff = afile.read()
                hasher.update(buff)

            digest = hasher.hexdigest()
            descriptions.append("-> '%s' (its hash is %s)" % (file_name, digest))

        data_to_send = str.join('\n', descriptions)
        self.send_message(client_conn, security, data_to_send)

    def receive_file(self, client_conn, security, file_name):
        file_path = './public/' + file_name
        FileHandler(file_path, client_conn, security).handle_download_file()

    def send_file(self, client_conn, security, file_name):
        FileHandler('./public/' + file_name, client_conn, security).handle_upload_file()
