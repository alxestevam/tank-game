import uuid
from server.Constants import Constants


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
        if Constants.ROOM_CAPACITIES[self.room_type] <= self.counter + 1:
            self.counter += 1
            self.players[client_handler.uidHex] = client_handler
            client_handler.room = self
            return self
        return None

    def leave(self, client_handler):
        if client_handler != self.ownerClient:
            self.counter -= 1
            del self.players[client_handler.uid]

    def ready_verifier(self):
        ready = True

        for player in self.players:
            if not player.ready:
                ready = False

        if ready and self.counter == Constants.ROOM_CAPACITIES[self.room_type]:
            self.ready = True
            self.server.readyRooms[self.room_type][self.uid] = self
        elif ready and self.counter < Constants.ROOM_CAPACITIES[self.room_type] and self.autoFill:
            # TODO: Implement auto fill rooms
            pass
        else:
            self.ready = False
            del self.server.readyRooms[self.room_type][self.uid]