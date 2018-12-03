from threading import Thread
from server.Match import Match


class RoomAnalyzer(Thread):
    def __init__(self, server):
        super(RoomAnalyzer, self).__init__(name='Room Analyzer Thread')
        self.server = server
        self.setDaemon(True)

        self.rooms = {
            'solo': [],
            'duo': [],
            'squad': []
        }

    def run(self):
        while True:
            for type_room, list_room in self.rooms.items():
                if len(list_room) < 2 and not self.server.readyRooms[type_room].empty():
                    room = self.server.readyRooms[type_room].get()
                    if room.isActive:
                        self.rooms[type_room].append(room)
                if len(list_room) == 2:
                    if self.rooms[type_room][0] != self.rooms[type_room][1]:
                        match = Match(self.server, self.rooms[type_room])
                        match.start()
                        self.server.matches.append(match)
                    self.rooms[type_room] = []
