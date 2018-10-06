from threading import Thread
from server.Match import Match


class RoomAnalyzer(Thread):
    def __init__(self, server):
        super(RoomAnalyzer, self).__init__(name='Room Analyzer Thread')
        self.server = server
        self.setDaemon(True)

    def run(self):
        solo_rooms = []
        duo_rooms = []
        squad_rooms = []
        while True:
            if not self.server.readyRooms['solo'].empty() and len(solo_rooms) < 2:
                print('Matching room...')
                solo_rooms.append(self.server.readyRooms['solo'].get())
                print(solo_rooms)
            if not self.server.readyRooms['duo'].empty() and len(duo_rooms) < 2:
                solo_rooms.append(self.server.readyRooms['duo'].get())
            if not self.server.readyRooms['squad'].empty() and len(squad_rooms) < 2:
                solo_rooms.append(self.server.readyRooms['squad'].get())
            if len(solo_rooms) == 2:
                print('New Match!', solo_rooms)
                match = Match(self, solo_rooms)
                match.start()
                self.server.matches.append(match)
                solo_rooms = []
            if len(duo_rooms) == 2:
                match = Match(self, duo_rooms)
                match.start()
                self.server.matches.append(match)
                duo_rooms = []
            if len(squad_rooms) == 2:
                match = Match(self, squad_rooms)
                match.start()
                self.server.matches.append(match)
                squad_rooms = []
