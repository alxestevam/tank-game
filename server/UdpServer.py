import threading
import socket
import json
import queue
import uuid
import server.Match as Match
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
        self.readyRooms = {'solo': {},
                           'pair': {},
                           'squad': {}}
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
                if data['action'] == 'connect_client':
                    if address_info not in self.clientAddresses:
                        self.connect_client(data['payload'], address_info)

    def connect_client(self, payload, address_info):
        # TODO: Login authentication is here

        # If login was successful then
        client_info = self.get_client_info()  # TODO: Make this better
        print('Client connected:', address_info, payload)
        self.clients.append(address_info)
        self.clientCounter += 1
        # Create ClientHandler
        uid = uuid.uuid4()  # New uid for each user
        ch = ClientHandler(self, uid, address_info, self.port + self.clientCounter, client_info)
        self.clientAddresses[address_info] = uid
        ch.start()
        # Send Success
        data = {'action': 'connect_client', 'payload': {'success': True}}
        data = json.dumps(data)
        data = data.encode('utf-8')

        self.sendto(data, address_info)

    def create_room(self, client_handler, client_info):
        self.roomCounter += 1
        room = Room(self, client_handler, client_info['lastRoomType'])
        self.rooms[room.uid] = room

    def delete_room(self):
        pass

    def player_join_room(self, payload, client_handler):
        uid = payload['room_uid']
        self.rooms[uid].join(client_handler)

    def create_match(self):
        pass

    def get_client_info(self):
        # TODO: Connect to the database to get this

        # This is a example of what type of dict this function has to return
        info = {'currentLevel': 10, 'lastRoomType': 'solo', 'playerNumber': 1}
        return info


if __name__ == '__main__':
    server = UdpServer()
    server.start()
