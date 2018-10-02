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
        self.cmd_uid_to_client(port)
        self.currentRoom = self.mainRoom

    def run(self):
        ping = threading.Thread(target=self.cmd_update_lobby)
        ping.start()
        handle = threading.Thread(target=self.handle_commands)
        handle.start()

        while True:
            data, address_info = self.recvfrom(Constants.BUFFER_SIZE)
            self.commands.put(data)

            # self.send_world_update()

    def cmd_uid_to_client(self, port):
        data = {
            'action': 'uid_to_client',
            'payload': {'uid_hex': self.uidHex, 'port': port, 'room_uid': self.mainRoom.uidHex}
        }

        self.sendto(json.dumps(data).encode('utf-8'), self.clientAddress)

    def cmd_update_lobby(self):
        while True:
            data = {
                'client_uid': self.uidHex,
                'action': 'update_lobby',
                'payload': {
                    'room_uid': self.currentRoom.uidHex,
                    'ready': self.ready
                }
            }
            self.sendto(json.dumps(data).encode('utf-8'), self.clientAddress)
            time.sleep(0.1)

    def cmd_world_update(self):
        pass

    def handle_commands(self):
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
                        keys = data.keys()
                        if 'client_uid' in keys:
                            if data['client_uid'] == self.uidHex:
                                if 'action' in keys and 'payload' in keys:
                                    if isinstance(data['payload'], dict):
                                        payload_keys = data['payload'].keys()
                                        action = data['action']
                                        if action == 'join_room':
                                            self.handle_cmd_join_room(data, payload_keys)
                                        if action == 'leave_room':
                                            self.handle_cmd_leave_room()
                                        if action == 'toggle_ready':
                                            self.handle_cmd_toggle_ready()
                                        if action == 'ping':
                                            pass

    def handle_cmd_join_room(self, data, payload_keys):
        if 'room_uid' in payload_keys:
            room_uid = data['payload']['room_uid']
            if self.currentRoom.uidHex != room_uid:
                room = self.server.player_join_room(room_uid, self)
                if room is not None:
                    print('Joining room', room_uid, self.clientAddress)
                    self.sendto(json.dumps(data).encode('utf-8'), self.clientAddress)
                    self.currentRoom = room
                else:
                    print('Room invalid or full')

    def handle_cmd_leave_room(self):
        if self.currentRoom != self.mainRoom:
            self.room.leave_player(self)

            data = {
                'client_uid': self.uidHex,
                'action': 'join_room',
                'payload': {
                    'room_uid': self.currentRoom.uidHex
                }
            }
            self.sendto(json.dumps(data).encode('utf-8'), self.clientAddress)

    def handle_cmd_toggle_ready(self):
        self.ready = not self.ready
        self.currentRoom.ready_verifier()

    def move_char(self):
        pass

    def shot(self, charge):
        pass
