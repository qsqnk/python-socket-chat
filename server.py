import socket
import threading
import logging

from typing import Tuple, Iterable

from config import SERVER_IP, SERVER_PORT


class SocketServer:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.connections = []

    def start(self) -> None:
        with socket.socket(
            family=socket.AF_INET,
            type=socket.SOCK_STREAM,
        ) as s:
            logging.info("Server is starting working on {}:{}", self.ip, self.port)
            try:
                s.bind((self.ip, self.port))
                s.listen()
                while True:
                    connection, ip_port = s.accept()
                    self.connections.append(connection)
                    threading.Thread(
                        target=self._handle,
                        args=[connection, ip_port],
                    ).start()
            except Exception as e:
                logging.error("An exception occurred during accepting connection", e)
            finally:
                for conn in self.connections:
                    self._drop(conn)

    def _handle(self, connection: socket.socket, ip_port: Tuple[str, str]) -> None:
        try:
            while True:
                ip, port = ip_port
                message = connection.recv(1024)
                if not message:
                    break
                message = f"{ip}:{port} says: {message.decode()}"
                self._broadcast(
                    message=message,
                    connections=filter(lambda c: c != connection, self.connections),
                )
        except Exception as e:
            logging.error("An exception occurred during handling connection", e)
        finally:
            self._drop(connection)

    def _broadcast(self, message: str, connections: Iterable[socket.socket]) -> None:
        for c in connections:
            self._send_or_drop(message, c)

    def _send_or_drop(self, message: str, connection: socket.socket):
        try:
            connection.send(message.encode())
        except Exception as e:
            logging.error("An exception occurred during broadcasting message", e)
            self._drop(connection)

    def _drop(self, connection: socket.socket) -> None:
        if connection not in self.connections:
            return
        self.connections.remove(connection)
        connection.close()


if __name__ == "__main__":
    SocketServer(
        ip=SERVER_IP,
        port=SERVER_PORT,
    ).start()
