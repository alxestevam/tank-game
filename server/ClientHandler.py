import threading
import socket
import json
import time
import queue
from server.Room import Room
from server.Constants import Constants


class ClientHandler(threading.Thread, socket.socket):
    def __init__(self, udp_server, uid_hex, client_address, port, client_info):
        threading.Thread.__init__(self, name='Client Handler Thread')
        socket.socket.__init__(self, type=socket.SOCK_DGRAM)
        self.settimeout(10)
        self.bind(('', port))
        self.setDaemon(True)
        self.server = udp_server
        self.clientAddress = client_address
        self.clientInfo = client_info
        self.ready = False
        self.match = None
        self.uidHex = uid_hex
        self.commands = queue.Queue()

        self.mainRoom = Room(udp_server, self, client_info['lastRoomType'])
        self.send_uid_to_client(port)
        self.currentRoom = self.mainRoom

    def run(self):
        ping = threading.Thread(target=self.send_ping)
        ping.start()
        handle = threading.Thread(target=self.handle_command)
        handle.start()

        while True:
            data, address_info = self.recvfrom(Constants.BUFFER_SIZE)
            self.commands.put(data)

            # self.send_world_update()

    def send_uid_to_client(self, port):
        data = {
            'action': 'send_client_uid',
            'payload': {'uid_hex': self.uidHex, 'port': port, 'room_uid': self.mainRoom.uidHex}
        }

        self.sendto(json.dumps(data).encode('utf-8'), self.clientAddress)

    def send_world_update(self):
        pass

    def send_ping(self):
        while True:
            self.sendto(json.dumps({'client_uid': self.uidHex, 'action': 'ping'}).encode('utf-8'), self.clientAddress)
            time.sleep(0.1)

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
                            if data['client_uid'] == self.uidHex:
                                if 'action' in data.keys():
                                    if data['action'] == 'join_room':
                                        self.join_room(data)
                                    if data['action'] == 'leave_room':
                                        self.leave_room()
                                    if data['action'] == 'ping':
                                        pass
                                        #  print('ping received, uid: ', data['client_uid'])

    def join_room(self, data):

        if 'payload' in data.keys():
            if isinstance(data['payload'], dict):
                if 'room_uid' in data['payload'].keys():
                    room_uid = data['payload']['room_uid']
                    if self.currentRoom.uidHex != room_uid:
                        room = self.server.player_join_room(room_uid, self)
                        if room is not None:
                            print('Joining room', room_uid, self.clientAddress)
                            self.sendto(json.dumps(data).encode('utf-8'), self.clientAddress)
                            self.currentRoom = room
                        else:
                            print('Room invalid')

    def leave_room(self):
        if self.currentRoom != self.mainRoom:
            self.currentRoom = self.mainRoom
            self.server.player_leave_room(self)
            data = {
                'client_uid': self.uidHex,
                'action': 'join_room',
                'payload': {
                    'room_uid': self.currentRoom.uidHex
                }
            }
            self.sendto(json.dumps(data).encode('utf-8'), self.clientAddress)

    def toggle_ready(self):
        self.ready = not self.ready
        self.room.ready_verifier()

        # Send success
        data = {'action': 'toggle_ready', 'payload': {'success': True}}

        self.sendto(json.dumps(data).encode('utf-8'), self.clientAddress)

    def move_char(self):
        pass

    def shot(self, charge):
        pass
