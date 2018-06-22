import hashlib
import os
import socket
import threading

from src.services.file_handler import FileHandler


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
        while True:
            data_received = client_conn.recv(1024)
            print('Data received {} from {}'.format(data_received, addr))
            if data_received:
                data = data_received.decode()
                option = data.split(' ')[0]

                if option == '1':
                    self.list_files(client_conn)
                elif option == '2':
                    file_name = data.split(' ')[1]
                    self.receive_file(client_conn, file_name)
                elif option == '3':
                    file_name = data.split(' ')[1]
                    self.send_file(client_conn, file_name)
                elif option == 'exit':
                    print('Disconnected {}'.format(addr))
                    client_conn.close()
                    break
                else:
                    client_conn.sendall(self.show_menu().encode())

    def show_menu(self):
        return "(1) Listar arquivos (Ex: 1) \n" \
               "(2) Upload de arquivo (Ex.: 2 nome_do_arquivo.txt) \n" \
               "(3) Download de arquivo (Ex.: 3 nome_do_arquivo.txt) \n" \
               "(*) Menu (Ex.: 4) \n" \
               "(exit) Sair (ex.: exit)"

    def list_files(self, client_conn):
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
        client_conn.sendall(data_to_send.encode())

    def receive_file(self, client_conn, file_name):
        file_path = './public/' + file_name
        FileHandler(file_path).handle_download_file(client_conn)

    def send_file(self, client_conn, file_name):
        FileHandler('./public/' + file_name).handle_upload_file(client_conn)
