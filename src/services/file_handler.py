import queue
import threading

BUF_SIZE = 1024


class FileHandler:

    def __init__(self, file_name):
        self.file_path = file_name

    def handle_download_file(self, connection):
        data_queue = queue.Queue()
        threading.Thread(target=self.save_downloaded_file, args=(data_queue,)).start()

        while True:
            data = connection.recv(BUF_SIZE)
            data_queue.put(data)
            if not data or data[len(data) - 1] == 0:
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

    def handle_upload_file(self, connection):
        try:
            f = open(self.file_path, 'r')
            print("Sending file '{}'...".format(self.file_path))
            data = f.read(BUF_SIZE)
            while data:
                connection.send(data.encode())
                data = f.read(BUF_SIZE)
            f.close()
            print("File '{}' sent.".format(self.file_path))
        except FileNotFoundError as e:
            print(e)

        connection.send(b'\0')
