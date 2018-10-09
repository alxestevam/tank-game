import threading
import socket
import json
import queue
from uuid import uuid4
from pygame.time import Clock
from server.Room import Room
from game.Constants import Constants


class ClientHandler(threading.Thread, socket.socket):
    def __init__(self, udp_server, client_address, port, client_info):
        threading.Thread.__init__(self, name='Client Handler Thread')
        socket.socket.__init__(self, type=socket.SOCK_DGRAM)
        # TODO: Configure the timeout
        self.settimeout(10)
        self.port = port
        self.bind(('', port))
        self.setDaemon(True)
        self.server = udp_server
        self.clientAddress = client_address
        self.clientInfo = client_info
        self.ready = False
        self.match = None
        self.uidHex = uuid4().hex
        self.commands = queue.Queue()

        self.mainRoom = Room(udp_server, self, client_info['lastRoomType'])
        self.cmd_uid_to_client(port)
        self.currentRoom = self.mainRoom
        self.character = None
        self.clock = Clock()
        self.connected = True

    def run(self):
        while self.connected:
            try:
                data, address_info = self.recvfrom(Constants.BUFFER_SIZE)
                self.handle_command(data)
            except socket.timeout:
                print('Client disconnected:', self.clientAddress)
                self.connected = False
                self.server.clientIpList.append(self.port)
                self.mainRoom.delete_room()
                self.currentRoom.delete_player(self.uidHex)

    def handle_command(self, data):
        if data:
            decoded = data.decode('utf-8')
            try:
                data = json.loads(decoded)
            except ValueError as err:
                print(err)
                raise ValueError('Expecting a JSON string from client, but got something else:', decoded)
            if data is not None:
                try:
                    if data['client_uid'] == self.uidHex:
                        action = data['action']
                        if action == 'update_lobby':
                            self.handle_cmd_update_lobby()
                        if action == 'join_room':
                            self.handle_cmd_join_room(data)
                        if action == 'leave_room':
                            self.handle_cmd_leave_room()
                        if action == 'toggle_ready':
                            self.handle_cmd_toggle_ready()
                        if action == 'player_shoot':
                            self.handle_cmd_player_shoot(data)
                        if action == 'update_world':
                            self.handle_cmd_update_world(data)
                except KeyError:
                    pass

    def cmd_uid_to_client(self, port):
        data = {
            'client_uid': self.uidHex,
            'action': 'uid_to_client',
            'payload': {'uid_hex': self.uidHex, 'port': port, 'room_uid': self.mainRoom.uidHex}
        }

        self.sendto(json.dumps(data).encode('utf-8'), self.clientAddress)

    def handle_cmd_update_world(self, data):
        if self.match is not None:
            try:
                controls = data['controls']

                if controls['angle_update']:
                    self.character.tank.update_angle(controls['angle_increase'])
                if controls['player_move']:
                    self.character.tank.move(controls['move_direction'])
                else:
                    self.character.tank.stop()
            except KeyError:
                pass
            data = {
                'client_uid': self.uidHex,
                'action': 'world_locations',
                'payload': {
                    'locations': self.match.world_locations()
                }
            }
            self.sendto(json.dumps(data).encode('utf-8'), self.clientAddress)

    def handle_cmd_update_lobby(self):
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

    def handle_cmd_join_room(self, data):
        try:
            room_uid = data['payload']['room_uid']
            if self.currentRoom.uidHex != room_uid:
                room = self.server.player_join_room(room_uid, self)
                if room is not None:
                    print('Joining room', room_uid, self.clientAddress)
                    self.sendto(json.dumps(data).encode('utf-8'), self.clientAddress)
                    self.currentRoom = room
                else:
                    print('Room invalid or full')
        except KeyError:
            print(KeyError)

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

    def handle_cmd_player_shoot(self, data):
        # TODO: Make this better
        if self.match is not None and self.character is not None:
            try:
                energy = data['payload']['energy']
                self.character.shoot(energy)
            except KeyError:
                print(KeyError)

    def handle_cmd_toggle_ready(self):
        self.ready = not self.ready
        self.currentRoom.ready_verifier()
