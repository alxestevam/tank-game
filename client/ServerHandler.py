import threading
import socket
import random
import json
import time
import queue
from pygame.time import Clock
from game.Constants import Constants
from client.GameWindow import GameWindow
from client.LobbyScreen import LobbyScreen


class ServerHandler(threading.Thread, socket.socket):
    def __init__(self, server_address):
        threading.Thread.__init__(self, name='ServerHandler Thread')
        socket.socket.__init__(self, type=socket.SOCK_DGRAM)
        self.settimeout(2)
        self.setDaemon(True)
        self.bind(('', random.randint(10000, 20000)))
        self.server_address = server_address
        self.uidHex = None
        self.commands = queue.Queue()
        self.mainRoomUid = None
        self.currentRoomUid = None
        self.ready = False
        self.matchUid = None
        self.gameWindow = None
        self.lock = threading.Lock()
        self.clock = Clock()

    def run(self):
        while self.uidHex is None:
            self.cmd_connect_client()
            try:
                data, address_info = self.recvfrom(Constants.BUFFER_SIZE)
                self.handle_command(data)
            except Exception:
                pass

        lobby_screen = LobbyScreen(self)
        lobby_screen.start()
        while True:

            while self.matchUid is None:
                self.cmd_update_lobby()
                try:
                    data, address_info = self.recvfrom(Constants.BUFFER_SIZE)
                    self.handle_command(data)
                except Exception:
                    pass

            # lobby_screen.win.destroy()
            # lobby_screen.join()

            while self.matchUid is not None:
                self.clock.tick(60)
                self.cmd_update_world(self.gameWindow.controls)
                try:
                    data, address_info = self.recvfrom(Constants.BUFFER_SIZE)
                    self.handle_command(data)
                except Exception:
                    pass

    def cmd_update_lobby(self):
        data = json.dumps({
            'client_uid': self.uidHex,
            'action': 'update_lobby'
        }).encode('utf-8')
        self.sendto(data, self.server_address)

    def cmd_update_world(self, controls):
        data = {
            'client_uid': self.uidHex,
            'action': 'update_world'
        }

        if controls is not None:
            data['controls'] = dict()
            data['controls']['player_move'] = controls['player_move']
            data['controls']['move_direction'] = controls['move_direction']
            data['controls']['angle_update'] = controls['angle_update']
            data['controls']['angle_increase'] = controls['angle_increase']

        self.sendto(json.dumps(data).encode('utf-8'), self.server_address)

    def cmd_connect_client(self):
        data = json.dumps({
            'action': 'connect_client',
            'payload': {
                'description': 'payload_for_authentication'
            }
        }).encode('utf-8')

        self.sendto(data, self.server_address)

    def cmd_join_room(self, uid):
        data = json.dumps({
            'client_uid': self.uidHex,
            'action': 'join_room',
            'payload': {
                'room_uid': uid
            }
        }).encode('utf-8')
        self.sendto(data, self.server_address)

    def cmd_toggle_ready(self):
        data = json.dumps({
            'client_uid': self.uidHex,
            'action': 'toggle_ready',
            'payload': {}
        }).encode('utf-8')
        self.sendto(data, self.server_address)

    def cmd_leave_room(self):
        data = json.dumps({
            'client_uid': self.uidHex,
            'action': 'leave_room',
            'payload': {}
        }).encode('utf-8')
        self.sendto(data, self.server_address)

    def cmd_player_shoot(self, energy):
        data = json.dumps({
            'client_uid': self.uidHex,
            'action': 'player_shoot',
            'payload': {'energy': energy}
        }).encode('utf-8')
        self.sendto(data, self.server_address)

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
                    self.uidHex = data['client_uid']
                except KeyError as err:
                    print(err)
                try:
                    action = data['action']
                except KeyError as err:
                    print(err)
                else:
                    if action == 'update_lobby':
                        self.handle_cmd_update_lobby(data)
                    if action == 'uid_to_client':
                        self.handle_cmd_uid_to_client(data)
                    if action == 'join_room':
                        self.handle_cmd_join_room(data)
                    if action == 'world_locations':
                        self.handle_cmd_world_locations(data)

    def handle_cmd_uid_to_client(self, data):
        original_server = self.server_address
        try:
            self.uidHex = data['payload']['uid_hex']
            self.mainRoomUid = data['payload']['room_uid']
            self.currentRoomUid = data['payload']['room_uid']
            self.server_address = (self.server_address[0], data['payload']['port'])
        except KeyError:
            self.uidHex = None
            self.mainRoomUid = None
            self.currentRoomUid = None
            self.server_address = original_server
            print(KeyError)
        else:
            print('Connected')

    def handle_cmd_join_room(self, data):
        try:
            self.currentRoomUid = data['payload']['room_uid']
        except KeyError:
            print(KeyError)

    def handle_cmd_update_lobby(self, data):
        uid_hex = self.uidHex
        current_room_uid = self.currentRoomUid
        ready = self.ready

        try:
            self.uidHex = data['client_uid']
            self.currentRoomUid = data['payload']['room_uid']
            self.ready = data['payload']['ready']
            match = data['payload']['match']
        except KeyError:
            self.uidHex = uid_hex
            self.currentRoomUid = current_room_uid
            self.ready = ready
            print(KeyError)
        else:
            if self.matchUid is None and match is not None:
                self.gameWindow = GameWindow(self)
                self.gameWindow.start_game()
                self.matchUid = match
            if self.matchUid is not None and match is None:
                self.gameWindow.close_game()
                self.matchUid = None

    def handle_cmd_world_locations(self, data):
        self.handle_cmd_update_lobby(data)
        if self.matchUid is not None:
            try:
                locations = data['payload']['locations']
            except KeyError:
                print(KeyError)
            else:
                try:
                    for uid, obj in locations.items():
                        if uid in self.gameWindow.env.objects:
                            if isinstance(obj, dict):
                                self.gameWindow.update_world_obj(uid, obj)
                        elif isinstance(obj, dict):
                                self.gameWindow.create_world_obj(uid, obj)
                except KeyError:
                    print(KeyError)


def test_menu(server_handler):
    time.sleep(1)
    op = 0
    while op != 7:
        op = int(input("[1] Print Current Room uid\n"
                       "[2] Print Main Room Uid\n"
                       "[3] Join room\n"
                       "[4] Leave room\n"
                       "[5] Ready\n"
                       "[6] Status\n"
                       "[7] Disconnect\n"
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
        elif op == 5:
            server_handler.cmd_toggle_ready()
        elif op == 6:
            if server_handler.ready:
                print('Ready!')
            else:
                print('Not ready.')


if __name__ == '__main__':
    client = ServerHandler(('127.0.0.1', 10939))
    client.start()
    client.join()
    # test_menu(client)


