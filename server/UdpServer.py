import threading
import socket
import json
import queue
from server.Match import Match
import time
from server.Room import Room
from server.ClientHandler import ClientHandler
from game.Constants import Constants


class UdpServer(threading.Thread, socket.socket):
    def __init__(self, port=None):
        threading.Thread.__init__(self, name='UdpServer Thread')
        socket.socket.__init__(self, type=socket.SOCK_DGRAM)
        self.port = Constants.DEFAULT_PORT if port is None else port
        self.player_limit = Constants.SERVER_PLAYER_LIMIT
        self.bind(('', self.port))
        self.clients = []
        self.clientAddresses = {}
        self.clientCounter = 0
        self.rooms = {}
        self.roomCounter = 0
        self.readyRooms = {'solo': queue.Queue(),
                           'duo': queue.Queue(),
                           'squad': queue.Queue()}
        # TODO: Implement auto fill rooms
        self.autoFillRooms = {'duo': {},
                              'squad': {}}
        self.matches = []
        self.roomsReady = {
            'solo': [],
            'duo': [],
            'squad': []
        }

        self.clientIpList = list(range(Constants.DEFAULT_PORT + 1, Constants.DEFAULT_PORT
                                       + Constants.SERVER_PLAYER_LIMIT))

    def run(self):
        print('Hosting at', self.getsockname())
        print('Starting')

        room_analyzer = threading.Thread(target=self.analise_rooms, name="Room Analyzer")
        room_analyzer.setDaemon(True)
        room_analyzer.start()

        while True:
            self.receive_command()

    def analise_rooms(self):
        while True:
            for type_room, list_room in self.roomsReady.copy().items():
                if len(list_room) < 2 and not self.readyRooms[type_room].empty():
                    room = self.readyRooms[type_room].get()
                    if room.isActive:
                        self.roomsReady[type_room].append(room)
                if len(list_room) == 2:
                    if self.roomsReady[type_room][0] != self.roomsReady[type_room][1]:
                        match = Match(self, self.roomsReady[type_room])
                        match.start()
                        self.matches.append(match)
                    self.roomsReady[type_room] = []

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
            if data is not None:
                try:
                    action = data['action']
                    payload = data['payload']
                    if action == 'connect_client':
                        self.handle_cmd_connect_client(payload, address_info)
                except KeyError:
                    pass

    def handle_cmd_connect_client(self, payload, address_info):
        if address_info not in self.clientAddresses:
            # TODO: Login authentication is here

            # If login was successful then
            client_info = self.get_client_info()  # TODO: Make this better
            print('Client connected:', address_info, payload)
            self.clients.append(address_info)
            self.clientCounter += 1
            nickname = payload['nickname']
            # Create ClientHandler
            port = self.clientIpList[0]
            del self.clientIpList[0]
            ch = ClientHandler(self, address_info, port, client_info, nickname)
            self.clientAddresses[address_info] = ch.uidHex
            ch.start()

    def create_room(self, client_handler, client_info):
        self.roomCounter += 1
        room = Room(self, client_handler, client_info['lastRoomType'])
        self.rooms[room.uidHex] = room

    def delete_room(self):
        pass

    def player_join_room(self, room_uid, client_handler):
        if room_uid in self.rooms.keys():
            return self.rooms[room_uid].join(client_handler)
        else:
            return None

    @staticmethod
    def get_client_info():
        # TODO: Connect to the database to get the info

        # This is a example of what type of dict this function has to return
        info = {
            'currentLevel': 10,
            'lastRoomType': 'solo',
            'playerNumber': 1,
            'currentSkin': 1
        }
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
