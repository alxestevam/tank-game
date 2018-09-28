from game.Environment import Environment
import Box2D
from server.Constants import Constants


class Match(Environment):
    def __init__(self, udp_server, players):
        Environment.__init__(self, Constants.SCREEN_SIZE, Box2D.b2World())
        self.server = udp_server
        self.players = players
        self.characters = {}
