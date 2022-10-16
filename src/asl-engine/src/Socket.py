import threading 
import socket
import time 
from collections import deque

class Socket:
    def __init__(self, host: str = "172.20.10.2", port: int = 25001, test: bool = False) -> None:
        self.host = host
        self.port = port

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.message_history = deque(maxlen=3)

        print("[SOCKET] Connecting to server...")
        self.socket.connect((self.host, self.port))
        print("[SOCKET] Connected to server")

    def write(self, message):
        print(f"[SOCKET] Sending message: '{message}'")

        if len(self.message_history) == self.message_history.maxlen:
            self.message_history.popleft()

        self.message_history.append(message)
        self.socket.send(message.encode('utf-8'))

    def __writeDelayed(self, message):
        time.sleep(1)
        self.write(message)

    def writeDelayed(self, message):
        threading.Thread(target=self.__writeDelayed, args=(message,)).start()

    def get_history(self) -> list:
        return list(self.message_history)