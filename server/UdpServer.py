import threading
import socket
import json
import queue
import uuid
import time
from server.Match import Match
from server.Room import Room
from server.ClientHandler import ClientHandler
from server.Constants import Constants


class UdpServer(threading.Thread, socket.socket):
    def __init__(self, port=None):
        threading.Thread.__init__(self, name='UdpServer Thread')
        socket.socket.__init__(self, type=socket.SOCK_DGRAM)
        self.port = Constants.DEFAULT_PORT if port is None else port
        self.bind(('', self.port))
        self.clients = []
        self.clientAddresses = {}
        self.clientCounter = 0
        self.rooms = {}
        self.roomCounter = 0
        self.readyRooms = {'solo': queue.Queue(),
                           'pair': queue.Queue(),
                           'squad': queue.Queue()}
        # TODO: Implement auto fill rooms
        self.autoFillRooms = {'pair': {},
                              'squad': {}}
        self.matches = []

    def run(self):
        print('Hosting at', self.getsockname())
        print('Starting')

        while True:
            self.receive_command()

    def receive_command(self):
        # TODO: Handle possible errors
        data, address_info = self.recvfrom(Constants.BUFFER_SIZE)
        if data:
            decoded = data.decode('utf-8')
            try:
                data = json.loads(decoded)
            except ValueError as err:
                print(err)
                raise ValueError('Expecting a JSON string from client, but got something else:', decoded)
            if data is not None and isinstance(data, dict):
                keys = data.keys()
                if 'action' in keys and 'payload' in keys:
                    action = data['action']
                    payload = data['payload']
                    if action == 'connect_client':
                        if isinstance(payload, dict):
                            self.handle_cmd_connect_client(payload, address_info)

    def handle_cmd_connect_client(self, payload, address_info):
        if address_info not in self.clientAddresses:
            # TODO: Login authentication is here

            # If login was successful then
            client_info = self.get_client_info()  # TODO: Make this better
            print('Client connected:', address_info, payload)
            self.clients.append(address_info)
            self.clientCounter += 1
            # Create ClientHandler
            uid_hex = uuid.uuid4().hex  # New uid for each user
            ch = ClientHandler(self, uid_hex, address_info, self.port + self.clientCounter, client_info)
            self.clientAddresses[address_info] = uid_hex
            ch.start()

    def analyze_ready_rooms(self):
        pass

    def create_room(self, client_handler, client_info):
        self.roomCounter += 1
        room = Room(self, client_handler, client_info['lastRoomType'])
        self.rooms[room.uid] = room

    def create_match(self, rooms):
        pass

    def delete_room(self):
        pass

    def player_join_room(self, room_uid, client_handler):
        if room_uid in self.rooms.keys():
            return self.rooms[room_uid].join(client_handler)
        else:
            return None

    def get_client_info(self):
        # TODO: Connect to the database to get the info

        # This is a example of what type of dict this function has to return
        info = {'currentLevel': 10, 'lastRoomType': 'duo', 'playerNumber': 1}
        return info


def test_menu(sv):
    time.sleep(1)
    op = 0
    while op != 6:
        op = int(input("[1] Print rooms\n"
                       "Choose: "))
        if op == 1:
            print(sv.rooms)



if __name__ == '__main__':
    server = UdpServer()
    server.start()
    test_menu(server)
