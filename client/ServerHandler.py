import threading
import socket
import random
import json
from server.Constants import Constants


class ServerHandler(threading.Thread, socket.socket):
    def __init__(self, server_address):
        threading.Thread.__init__(self, name='ServerHandler Thread')
        socket.socket.__init__(self, type=socket.SOCK_DGRAM)
        self.settimeout(2)
        self.setDaemon(False)
        self.bind(('localhost', random.randint(10000, 20000)))
        self.server_address = server_address
        self.connected = False

    def run(self):
        while True:
            print('ranning...')
            if not self.connected:
                self.connect()
            self.receive_command()

    def connect(self):
        print('trying to connect')
        # TODO: Add payload for authentication
        data = {'action': 'connect_client', 'payload': 'payload_for_authentication'}
        data = json.dumps(data)
        data = data.encode('utf-8')

        self.sendto(data, self.server_address)

    def get_uid(self):
        pass

    def join_room(self):
        pass

    def send_command(self):
        pass

    def receive_command(self):
        data, address_info = self.recvfrom(Constants.BUFFER_SIZE)
        if data:
            decoded = data.decode('utf-8')
            try:
                data = json.loads(decoded)
            except ValueError as err:
                print(err)
                raise ValueError('Expecting a JSON string from client, but got something else:', decoded)
            if data is not None and isinstance(data, dict):
                if data['action'] == 'connect_client':
                    if data['payload']['success']:
                        self.connected = True

    def toggle_ready(self):
        pass

    def leave_room(self):
        pass


if __name__ == '__main__':
    client = ServerHandler(('127.0.0.1', 10939))
    client.start()

