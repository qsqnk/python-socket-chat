import socket
import threading

from config import SERVER_IP, SERVER_PORT, MAX_MESSAGE_LENGTH


class Client:
    def __init__(self, server_ip, server_port):
        self.server_ip = server_ip
        self.server_port = server_port
        self.connection = None

    def start(self) -> None:
        self.connection = socket.socket()
        with self.connection:
            try:
                self.connection.connect((self.server_ip, self.server_port))
                threading.Thread(
                    target=self._handle_server_messages,
                ).start()
                print("You are connected to chat")
                self._handle_user_messages()
            except Exception as _:
                print("Unexpected error. Connection refused...")
        self.connection = None

    def _handle_server_messages(self):
        _META_INFO_LENGTH = 128
        while True:
            message = self.connection.recv(MAX_MESSAGE_LENGTH + _META_INFO_LENGTH)
            if not message:
                break
            print(message.decode())

    def _handle_user_messages(self):
        while True:
            message = input()
            if not message:
                continue
            self.connection.send(message[:MAX_MESSAGE_LENGTH].encode())


if __name__ == "__main__":
    Client(
        server_ip=SERVER_IP,
        server_port=SERVER_PORT,
    ).start()
