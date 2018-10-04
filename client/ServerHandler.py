import threading
import socket
import random
import json
import time
import queue
from game.Constants import Constants
from client.GameWindow import GameWindow


class ServerHandler(threading.Thread, socket.socket):
    def __init__(self, server_address):
        threading.Thread.__init__(self, name='ServerHandler Thread')
        socket.socket.__init__(self, type=socket.SOCK_DGRAM)
        self.settimeout(2)
        self.setDaemon(True)
        self.bind(('localhost', random.randint(10000, 20000)))
        self.server_address = server_address
        self.uidHex = None
        self.commands = queue.Queue()
        self.mainRoomUid = None
        self.currentRoomUid = None
        self.ready = False
        self.matchUid = None
        self.gameWindow = None
        self.lock = threading.Lock()

    def run(self):
        self.cmd_connect_client()

        ping = threading.Thread(target=self.cmd_ping)
        handle = threading.Thread(target=self.handle_commands)
        handle.start()
        ping.start()

        while True:
            data, address_info = self.recvfrom(Constants.BUFFER_SIZE)
            self.commands.put(data)

    def cmd_connect_client(self):
        # TODO: Add payload for authentication
        data = {
            'action': 'connect_client',
            'payload': {
                'description': 'payload_for_authentication'
            }
        }
        data = json.dumps(data)
        data = data.encode('utf-8')

        self.sendto(data, self.server_address)

    def cmd_ping(self):
        while True:
            self.sendto(json.dumps({'client_uid': self.uidHex, 'action': 'ping'}).encode('utf-8'), self.server_address)
            time.sleep(0.1)

    def cmd_join_room(self, uid):
        data = {
            'client_uid': self.uidHex,
            'action': 'join_room',
            'payload': {
                'room_uid': uid
            }
        }
        self.sendto(json.dumps(data).encode('utf-8'), self.server_address)

    def cmd_toggle_ready(self):
        data = {
            'client_uid': self.uidHex,
            'action': 'toggle_ready',
            'payload': {}
        }
        self.sendto(json.dumps(data).encode('utf-8'), self.server_address)

    def cmd_leave_room(self):
        data = {
            'client_uid': self.uidHex,
            'action': 'leave_room',
            'payload': {}
        }
        self.sendto(json.dumps(data).encode('utf-8'), self.server_address)

    def cmd_player_shoot(self, energy):
        data = {
            'client_uid': self.uidHex,
            'action': 'player_shoot',
            'payload': {'energy': energy}
        }
        self.sendto(json.dumps(data).encode('utf-8'), self.server_address)

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
                        if 'client_uid' in data.keys():
                            self.uidHex = data['client_uid']
                        if 'action' in keys and 'payload' in keys:
                            if isinstance(data['payload'], dict):
                                payload_keys = data['payload'].keys()
                                action = data['action']
                                if action == 'update_lobby':
                                    self.handle_cmd_update_lobby(data, payload_keys)
                                if action == 'uid_to_client':
                                    self.handle_cmd_uid_to_client(data, payload_keys)
                                if action == 'join_room':
                                    self.handle_cmd_join_room(data, payload_keys)
                                if action == 'world_locations':
                                    self.handle_cmd_world_locations(data, payload_keys)

    def handle_cmd_uid_to_client(self, data, payload_keys):
        if 'uid_hex' in payload_keys:
            self.uidHex = data['payload']['uid_hex']
        if 'port' in payload_keys:
            self.server_address = (self.server_address[0], data['payload']['port'])
            print('connected')
        if 'room_uid' in payload_keys:
            self.mainRoomUid = data['payload']['room_uid']
            self.currentRoomUid = data['payload']['room_uid']

    def handle_cmd_join_room(self, data, payload_keys):
        if 'room_uid' in payload_keys:
            self.currentRoomUid = data['payload']['room_uid']

    def handle_cmd_update_lobby(self, data, payload_keys):
        if 'client_uid' in data.keys():
            self.uidHex = data['client_uid']
        if 'room_uid' in payload_keys:
            self.currentRoomUid = data['payload']['room_uid']
        if 'ready' in payload_keys:
            self.ready = data['payload']['ready']
        if 'match' in payload_keys:
            match = data['payload']['match']
            if self.matchUid is None and match is not None:
                self.gameWindow = GameWindow(self)
                self.gameWindow.start_game()
                self.matchUid = match
            if self.matchUid is not None and match is None:
                self.gameWindow.close_game()
                self.matchUid = None

    def handle_cmd_world_locations(self, data, payload_keys):
        # print('cmd world locations received')
        if self.matchUid is not None:
            if 'locations' in payload_keys:
                locations = data['payload']['locations']
                if isinstance(locations, dict):
                    for uid, obj in locations.items():
                        # self.lock.acquire()
                        if uid in self.gameWindow.env.objects:
                            if isinstance(obj, dict):
                                self.gameWindow.update_world_obj(uid, obj)
                        elif isinstance(obj, dict):
                                self.gameWindow.create_world_obj(uid, obj)
                        # self.lock.release()


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
    test_menu(client)


