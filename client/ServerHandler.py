import threading
import socket
import random
import json
import time
import queue
from server.Constants import Constants


class ServerHandler(threading.Thread, socket.socket):
    def __init__(self, server_address):
        threading.Thread.__init__(self, name='ServerHandler Thread')
        socket.socket.__init__(self, type=socket.SOCK_DGRAM)
        self.settimeout(10)
        self.setDaemon(False)
        self.bind(('localhost', random.randint(10000, 20000)))
        self.server_address = server_address
        self.uidHex = None
        self.commands = queue.Queue()
        self.mainRoomUid = None
        self.currentRoomUid = None

    def run(self):
        self.connect()

        ping = threading.Thread(target=self.send_ping)
        handle = threading.Thread(target=self.handle_command)
        handle.start()
        ping.start()

        while True:
            data, address_info = self.recvfrom(Constants.BUFFER_SIZE)
            self.commands.put(data)

    def connect(self):
        # TODO: Add payload for authentication
        data = {'action': 'connect_client', 'payload': 'payload_for_authentication'}
        data = json.dumps(data)
        data = data.encode('utf-8')

        self.sendto(data, self.server_address)

    def send_ping(self):
        while True:
            self.sendto(json.dumps({'client_uid': self.uidHex, 'action': 'ping'}).encode('utf-8'), self.server_address)
            time.sleep(0.1)

    def join_room_confirmation(self):
        pass

    def handle_command(self):
        while True:
            if not self.commands.empty():
                data = self.commands.get()
                if data:
                    decoded = data.decode('utf-8')
                    try:
                        data = json.loads(decoded)
                    except ValueError as err:
                        print(err)
                        raise ValueError('Expecting a JSON string from client, but got something else:', decoded)
                    if data is not None and isinstance(data, dict):
                        if 'client_uid' in data.keys():
                            self.uidHex = data['client_uid']
                        if 'action' in data.keys():
                            if data['action'] == 'ping':
                                pass
                                #  print('ping received, uid: ', data['client_uid'])
                            if data['action'] == 'send_client_uid':
                                if 'payload' in data.keys():
                                    if isinstance(data['payload'], dict):
                                        pk = data['payload'].keys()
                                        if 'uid_hex' in pk:
                                            self.uidHex = data['payload']['uid_hex']
                                        if 'port' in pk:
                                            self.server_address = (self.server_address[0], data['payload']['port'])
                                            print('connected')
                                        if 'room_uid' in pk:
                                            self.mainRoomUid = data['payload']['room_uid']
                                            self.currentRoomUid = data['payload']['room_uid']
                            if data['action'] == 'join_room':
                                if 'payload' in data.keys():
                                    if isinstance(data['payload'], dict):
                                        pk = data['payload'].keys()
                                        if 'room_uid' in pk:
                                            self.currentRoomUid = data['payload']['room_uid']

    def cmd_join_room(self, uid):
        data = {
            'client_uid': self.uidHex,
            'action': 'join_room',
            'payload': {
                'room_uid': uid
            }
        }
        self.sendto(json.dumps(data).encode('utf-8'), self.server_address)

    def toggle_ready(self):
        pass

    def cmd_leave_room(self):
        data = {
            'client_uid': self.uidHex,
            'action': 'leave_room'
        }
        self.sendto(json.dumps(data).encode('utf-8'), self.server_address)


def test_menu(server_handler):
    time.sleep(1)
    op = 0
    while op != 6:
        op = int(input("[1] Print Current Room uid\n"
                       "[2] Print Main Room Uid\n"
                       "[3] Join room\n"
                       "[4] Leave room\n"
                       "[5] Ready\n"
                       "[6] Disconnect\n"
                       "Choose: "))
        if op == 1:
            print(server_handler.currentRoomUid)
        elif op == 2:
            print(server_handler.mainRoomUid)
        elif op == 3:
            room_uid = input("UID: ")
            server_handler.cmd_join_room(room_uid)
        elif op == 4:
            server_handler.cmd_leave_room()


if __name__ == '__main__':
    client = ServerHandler(('127.0.0.1', 10939))
    client.start()
    test_menu(client)

