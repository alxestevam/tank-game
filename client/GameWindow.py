import threading
import pygame
from Box2D import *
from game.Environment import Environment
from game.Sprite import Sprite
from game.Terrain import Terrain
from game.Bullet import Bullet
from game.Tank import Tank
from game.Entity import Entity
from game.ContactListener import ContactListener
from pygame.color import THECOLORS


class GameWindow(threading.Thread):
    def __init__(self, server_handler):
        threading.Thread.__init__(self, name='Game Window Thread')
        self.setDaemon(True)
        self.serverHandler = server_handler

        self.screen_size = (1280, 720)
        self.FPS = 60

        # Creating the Box2d World and Environment
        world = b2World(gravity=(0, -20), contactListener=ContactListener())
        self.env = Environment(self.screen_size, world)
        self.timeStep = 1.0 / self.FPS
        self.vel_iter, self.pos_iter = 10, 10

        self.win = None
        self.clock = None
        self.isRunning = False

        # Game Variables
        self.charge_level = 0
        self.charging_speed = 1
        self.max_charge = 200
        self.charging = False
        self.shoot = True
        self.controls = None

    def run(self):
        # Initializing the game
        pygame.init()

        self.win = pygame.display.set_mode(self.screen_size)
        self.clock = pygame.time.Clock()
        self.isRunning = True

        time = 0
        while self.isRunning:
            dt_s = float(self.clock.tick(self.FPS)) * 1e-3

            self.env.world.Step(self.timeStep, self.vel_iter, self.pos_iter)
            self.win.fill(THECOLORS['white'])

            for uid, obj in self.env.objects.copy().items():
                if isinstance(obj, Sprite):
                    obj.show(self.win)
                if isinstance(obj, Terrain) or isinstance(obj, Bullet):
                    obj.update()

            cmd = self.env.get_local_user_input()
            self.controls = self.env.controls()

            if cmd == 0:
                self.isRunning = False
                self.serverHandler.cmd_surrender()
                break
            elif cmd == 1:
                self.charging = True
            elif cmd == 2:
                self.charging = False
                self.serverHandler.cmd_player_shoot(self.charge_level)
                self.charge_level = 0

            if self.charging:
                if self.charge_level < self.max_charge - self.charging_speed:
                    self.charge_level += self.charging_speed

            self.draw_charging_bar(self.win, self.charge_level)

            time += dt_s  # Increasing the time counter
            pygame.display.update()

        pygame.quit()

    def create_world_obj(self, uid, obj):
        # TODO: Apply try exception
        cls_name = obj['__class__']
        if cls_name == 'Terrain':
            terrain = Terrain(self.env, uid=uid)
            vertices_list = obj['vertices_list']

            for f in terrain.body.fixtures:
                terrain.body.DestroyFixture(f)

            for vertices in vertices_list:
                del vertices[-1]
                chain_shape = b2ChainShape(vertices=vertices)
                terrain.body.CreateFixture(shape=chain_shape)
        elif cls_name == 'Tank':
            position = b2Vec2(obj['position']['__value__'])
            Tank(self.env, position, uid=uid)
        elif cls_name == 'Bullet':
            position = b2Vec2(obj['position']['__value__'])
            radius = obj['radius']
            bullet_type = obj['bullet_type']
            Bullet(self.env, position, radius=radius, bullet_type=bullet_type, uid=uid)

    def update_world_obj(self, uid, obj):
        # TODO: Apply try exception
        for uidHex, entity in self.env.objects.copy().items():
            if uidHex == uid:
                if isinstance(entity, Terrain):
                    vertices_list = obj['vertices_list']
                    for f in entity.body.fixtures:
                        try:
                            entity.body.DestroyFixture(f)
                        except AssertionError:
                            pass

                    for vertices in vertices_list:
                        del vertices[-1]
                        chain_shape = b2ChainShape(vertices=vertices)
                        entity.body.CreateFixture(shape=chain_shape)
                elif isinstance(entity, Entity):
                    position = b2Vec2(obj['position']['__value__'])
                    angle = obj['angle']
                    angular_damping = obj['angularDamping']
                    angular_velocity = obj['angularVelocity']
                    inertia = obj['inertia']
                    linear_damping = obj['linearDamping']
                    linear_velocity = b2Vec2(obj['linearVelocity']['__value__'])
                    local_center = b2Vec2(obj['localCenter']['__value__'])
                    # mass = obj['mass']
                    entity.body.position = position
                    entity.body.angle = angle
                    entity.body.angularDamping = angular_damping
                    entity.body.angularVelocity = angular_velocity
                    entity.body.inertia = inertia
                    entity.body.linearDamping = linear_damping
                    entity.body.linearVelocity = linear_velocity
                    entity.body.localCenter = local_center
                    # obj.body.mass = mass
                if isinstance(entity, Tank):
                    aim_angle = obj['aimAngle']
                    direction = obj['direction']
                    health = obj['health']
                    gun_barrel_distance = b2Vec2(obj['gunBarrelDistance']['__value__'])
                    entity.angle = aim_angle
                    entity.gunBarrelDistance = gun_barrel_distance
                    entity.direction = direction
                    entity.health = health

    def destroy_world_object(self):
        pass

    @staticmethod
    def draw_charging_bar(win, charging_level):
        size = 500
        max_charge = 200
        pygame.draw.rect(win, THECOLORS['red'], (0, 0, charging_level / max_charge * size, 20))

    def start_game(self):
        self.start()
        # self.join()

    def close_game(self):
        self.isRunning = False
