from game.Environment import Environment
from server.Character import Character
from game.ContactListener import ContactListener
from game.Terrain import Terrain
from game.Bullet import Bullet
import pygame
import uuid
import Box2D
from game.Constants import Constants


class Match(Environment):
    def __init__(self, udp_server, rooms):
        Environment.__init__(self, Constants.SCREEN_SIZE, Box2D.b2World(gravity=(0, -20),
                                                                        contactListener=ContactListener()))
        self.server = udp_server
        self.rooms = rooms
        self.characters = {}
        self.uidHex = uuid.uuid4().hex
        # TODO: Add terrain variation
        Terrain(self, Constants.TERRAIN_CONFIG['1']['vertices'])

        # Creating the characters for each player
        team = 1
        for room in self.rooms:
            for uid, player in room.players.items():
                player.match = self
                player.ready = False
                character = Character(self, player, team)
                self.characters[character.uidHex] = character
            team += 1

    def run(self):
        time_step = 1.0 / Constants.FPS
        vel_iter, pos_iter = 10, 10
        run = True
        clock = pygame.time.Clock()
        time = 0
        while run:
            dt_s = float(clock.tick(Constants.FPS)) * 1e-3
            self.world.Step(time_step, vel_iter, pos_iter)
            time += dt_s

    def world_locations(self):
        #  Generate world json data based on objects uid
        data = {}
        for uidHex, obj in self.objects:
            if isinstance(obj, Terrain):
                data[uidHex] = {
                    '__class__': obj.__class__.__name__,
                    'vertices': []
                }

                for fixture in obj.body.fixtures:
                    data[uidHex]['vertices'].append(fixture.shape.vertices)
            elif isinstance(obj, Bullet):
                data[uidHex] = {
                    '__class__': obj.__class__.__name__,
                    'position': self.to_json(obj.body.position),
                    'angle': obj.body.angle,
                    'angularDamping': obj.body.angularDamping,
                    'angularVelocity': obj.body.angularVelocity,
                    'inertia': obj.body.inertia,
                    'linearDamping': obj.body.linearDamping,
                    'linearVelocity': self.to_json(obj.body.linearVelocity),
                    'localCenter': self.to_json(obj.body.localCenter),
                    'mass': obj.body.mass,
                    'radius': obj.radius,
                    'bullet_type': obj.bullet_type,
                    'explosion_radius': obj.explosion_radius
                }
            elif isinstance(obj.body, Box2D.b2Body):
                data[uidHex] = {
                    '__class__': obj.__class__.__name__,
                    'position': self.to_json(obj.body.position),
                    'angle': obj.body.angle,
                    'angularDamping': obj.body.angularDamping,
                    'angularVelocity': obj.body.angularVelocity,
                    'inertia': obj.body.inertia,
                    'linearDamping': obj.body.linearDamping,
                    'linearVelocity': self.to_json(obj.body.linearVelocity),
                    'localCenter': self.to_json(obj.body.localCenter),
                    'mass': obj.body.mass
                }

        return data

    def broadcast_players_world_locations(self):
        for room in self.rooms:
            for uid, player in room.players.items():
                player.cmd_world_locations()

    def close_match(self):
        pass
