import threading
import socket
import json
import time
import queue
from pygame.time import Clock
from server.Room import Room
from game.Constants import Constants
from server.CommandHandler import CommandHandler


class ClientHandler(threading.Thread, socket.socket):
    def __init__(self, udp_server, uid_hex, client_address, port, client_info):
        threading.Thread.__init__(self, name='Client Handler Thread')
        socket.socket.__init__(self, type=socket.SOCK_DGRAM)
        # TODO: Configure the timeout
        self.settimeout(2)
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
        self.character = None
        self.clock = Clock()

    def run(self):
        update_lobby = threading.Thread(target=self.cmd_update_lobby)
        update_lobby.start()

        # TODO: Make the thread stop or decide to use broadcast from Match.py
        world_locations = threading.Thread(target=self.cmd_world_locations)
        world_locations.start()

        while True:
            data, address_info = self.recvfrom(Constants.BUFFER_SIZE)
            c = CommandHandler(self, data)
            c.start()

    def cmd_world_locations(self):
        while True:
            if self.match is not None:
                data = {
                    'client_uid': self.uidHex,
                    'action': 'world_locations',
                    'payload': {
                        'locations': self.match.world_locations()
                    }
                }
                self.sendto(json.dumps(data).encode('utf-8'), self.clientAddress)
            self.clock.tick(40)

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
            if self.match is None:
                data['payload']['match'] = None
            else:
                data['payload']['match'] = self.match.uidHex

            self.sendto(json.dumps(data).encode('utf-8'), self.clientAddress)
            # TODO: Verify the need of the delay
            self.clock.tick(30)

    def cmd_world_update(self):
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
            self.currentRoom.leave_player(self)

            data = {
                'client_uid': self.uidHex,
                'action': 'join_room',
                'payload': {
                    'room_uid': self.currentRoom.uidHex
                }
            }
            self.sendto(json.dumps(data).encode('utf-8'), self.clientAddress)

    def handle_cmd_player_shoot(self, data, payload_keys):
        # TODO: Make this better
        if self.match is not None and self.character is not None:
            if 'energy' in payload_keys:
                energy = data['payload']['energy']
                self.character.shoot(energy)

    def handle_cmd_toggle_ready(self):
        self.ready = not self.ready
        self.currentRoom.ready_verifier()

    def move_char(self):
        pass

    def shot(self, charge):
        pass
