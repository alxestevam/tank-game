from game.Environment import Environment
from server.Character import Character
from game.ContactListener import ContactListener
from game.Terrain import Terrain
from game.Bullet import Bullet
from game.Tank import Tank
import pygame
import uuid
import Box2D
from game.Constants import Constants
from game.Entity import Entity


class Match(Environment):
    def __init__(self, udp_server, rooms):
        Environment.__init__(self, Constants.SCREEN_SIZE, Box2D.b2World(gravity=(0, -20),
                                                                        contactListener=ContactListener()))
        self.server = udp_server
        self.rooms = rooms
        self.characters = {}
        self.uidHex = uuid.uuid4().hex
        # TODO: Add terrain variation
        Terrain(self, vertices=Constants.TERRAIN_CONFIG['1']['vertices'])
        self.teams = {1: [],
                      2: []}
        # Creating the characters for each player
        team_num = 1
        for room in self.rooms:
            for uid, player in room.players.items():
                player.match = self
                player.ready = False
                character = Character(self, player, team_num)
                self.characters[character.uidHex] = character
                self.teams[team_num].append(character)
            team_num += 1

    def run(self):
        time_step = 1.0 / Constants.FPS*1.5
        vel_iter, pos_iter = 10, 10
        run = True
        clock = pygame.time.Clock()
        time = 0
        while run:
            dt_s = float(clock.tick(Constants.FPS)) * 1e-3
            self.world.Step(time_step, vel_iter, pos_iter)

            for uid, obj in self.objects.copy().items():
                if isinstance(obj, Entity):
                    obj.update()

            end_game = True
            team_winner = 0
            for num, team in self.teams.items():
                end_game = True
                team_winner = 0
                for char in team:
                    if char is not None:
                        if char.tank.health > 0 and (not char.surrender):
                            end_game = False
                            break
                if end_game:
                    team_winner = num
                    break

            if end_game:
                run = False
                for room in self.rooms:
                    for player in room.players.values():
                        player.match = None
                        player.ready = False
                        player.character = None

                # TODO: show the winners
                winners = "Team: "
                team = team_winner
                for ch in self.characters.values():
                    if team == ch.team:
                        winners += ch.player.nickname + " "

                for ch in self.characters.values():
                    ch.player.nextWinners = winners

            time += dt_s

    def world_locations(self):
        #  Generate world json data based on objects uid
        data = {}
        for uidHex, obj in self.objects.copy().items():
            if isinstance(obj, Terrain):
                data[uidHex] = {
                    '__class__': obj.__class__.__name__,
                    'vertices_list': []
                }

                for fixture in obj.body.fixtures:
                    data[uidHex]['vertices_list'].append(fixture.shape.vertices)
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
            elif isinstance(obj, Tank):
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
                    'gunBarrelDistance': self.to_json(obj.gunBarrelDistance),
                    'aimAngle': obj.angle,
                    'direction': obj.direction,
                    'health': obj.health
                }

        return data

    def close_match(self):
        pass
