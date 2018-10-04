import uuid
from game.Constants import Constants


class Room:
    def __init__(self, udp_server, client_handler, room_type):
        self.server = udp_server
        self.ownerClient = client_handler
        self.room_type = room_type
        self.ready = False
        self.uidHex = uuid.uuid4().hex
        self.players = dict()
        self.players[client_handler.uidHex] = client_handler
        self.counter = 1
        self.server.rooms[self.uidHex] = self

        self.autoFill = False

    def join(self, client_handler):
        if Constants.ROOM_CAPACITIES[self.room_type] >= self.counter + 1:
            self.counter += 1
            self.players[client_handler.uidHex] = client_handler
            client_handler.room = self
            return self
        return None

    def leave_player(self, client_handler):
        if client_handler != self.ownerClient:
            client_handler.currentRoom = client_handler.mainRoom
            self.counter -= 1
            del self.players[client_handler.uidHex]
            self.ready = False

    def ready_verifier(self):
        ready = True

        for uid, player in self.players.items():
            if not player.ready:
                ready = False

        if ready and self.counter == Constants.ROOM_CAPACITIES[self.room_type]:
            self.ready = True
            print('Ready room', self)
            self.server.readyRooms[self.room_type].put(self)
        elif ready and self.counter < Constants.ROOM_CAPACITIES[self.room_type] and self.autoFill:
            # TODO: Implement auto fill rooms
            pass
        else:
            self.ready = False
