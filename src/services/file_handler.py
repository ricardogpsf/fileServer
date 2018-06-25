import queue
import threading

SIZE_TO_READ_FILE = 1024
SIZE_TO_RECEIVE_STREAM = 1464


class FileHandler:

    def __init__(self, file_name, connection, security):
        self.file_path = file_name
        self.connection = connection
        self.security = security

    def handle_download_file(self):
        data_queue = queue.Queue()
        threading.Thread(target=self.save_downloaded_file, args=(data_queue,)).start()

        while True:
            data_encr = self.connection.recv(SIZE_TO_RECEIVE_STREAM)
            data = self.security.decrypt(data_encr)
            data_queue.put(data)
            if not data or data[len(data)-1] == 0:
                break

    def save_downloaded_file(self, data_queue):
        print("Downloading file '{}'...".format(self.file_path))
        with open(self.file_path, 'w') as f:
            while True:
                data = data_queue.get()
                print("Content queue: '{}'...".format(data))
                if not data:
                    break

                last_index = len(data) - 1
                if data[last_index] == 0:
                    b_text = data[0:last_index]
                    if b_text:
                        f.write(b_text.decode())
                    break

                f.write(data.decode())

        print("File '{}' downloaded.".format(self.file_path))

    def handle_upload_file(self):
        try:
            f = open(self.file_path, 'r')
            print("Sending file '{}'...".format(self.file_path))
            send_end_text_char = True
            data = f.read(SIZE_TO_READ_FILE)
            while data:
                if len(data) < SIZE_TO_READ_FILE:
                    data += '\0'
                    send_end_text_char = False

                msg = self.security.encrypt(data.encode())
                self.connection.send(msg)
                data = f.read(SIZE_TO_READ_FILE)
            f.close()

            if send_end_text_char:
                self.connection.send(self.security.encrypt(b'\0'))

            print("File '{}' sent.".format(self.file_path))
        except FileNotFoundError as e:
            print(e)
