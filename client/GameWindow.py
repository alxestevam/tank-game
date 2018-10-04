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
        self.isRunning = True
        self.serverHandler = server_handler

        screen_size = (1280, 720)
        self.FPS = 60

        # Creating the Box2d World and Environment
        world = b2World(gravity=(0, -20), contactListener=ContactListener())
        self.env = Environment(screen_size, world)
        self.timeStep = 1.0 / self.FPS
        self.vel_iter, self.pos_iter = 10, 10

        # Initializing the game
        pygame.init()
        self.win = pygame.display.set_mode(screen_size)
        self.clock = pygame.time.Clock()

        # Game Variables
        self.charge_level = 0
        self.charging_speed = 1
        self.max_charge = 200
        self.charging = False
        self.shoot = True

    def run(self):
        time = 0
        while self.isRunning:

            dt_s = float(self.clock.tick(self.FPS)) * 1e-3
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.isRunning = False

            self.env.world.Step(self.timeStep, self.vel_iter, self.pos_iter)
            self.win.fill(THECOLORS['white'])

            for obj in self.env.objects:
                if isinstance(obj, Sprite):
                    obj.show(self.win)
                if isinstance(obj, Terrain) or isinstance(obj, Bullet):
                    obj.update()
                    print(obj.body.fixtures[0].shape.vertices)
            
            if self.charging:
                if self.charge_level < self.max_charge - self.charging_speed:
                    self.charge_level += self.charging_speed

            self.draw_charging_bar(self.win, self.charge_level)

            time += dt_s  # Increasing the time counter
            pygame.display.update()

        pygame.quit()

    def create_world_obj(self, obj):
        # TODO: Verify if every item exists in the dict (if 'item' in dict key)
        cls_name = obj['__class__']
        if cls_name == 'Terrain':
            Terrain(self.env, obj['vertices'])
        elif cls_name == 'Tank':
            position = b2Vec2(obj['position']['__value__'])
            Tank(self.env, position)
        elif cls_name == 'Bullet':
            position = b2Vec2(obj['position']['__value__'])
            radius = obj['radius']
            bullet_type = obj['bullet_type']
            Bullet(self.env, position, radius=radius, bullet_type=bullet_type)

    def update_world_obj(self, uid, obj):
        cls_name = obj['__class__']
        for uidHex, obj in self.env.objects.items():
            if isinstance(obj, Entity):
                if obj.uidHex == uidHex:
                    if cls_name == 'Terrain' or cls_name == 'Tank' or cls_name == 'Bullet':
                        position = b2Vec2(obj['position']['__value__'])
                        angle = obj['angle']
                        angular_damping = obj['angularDamping']
                        angular_velocity = obj['angularVelocity']
                        inertia = obj['inertia']
                        linear_damping = obj['linearDamping']
                        linear_velocity = b2Vec2(obj['linearVelocity']['__value__'])
                        local_center = b2Vec2(obj['localCenter']['__value__'])
                        # mass = obj['mass']
                        obj.body.position = position
                        obj.body.angle = angle
                        obj.body.angularDamping = angular_damping
                        obj.body.angularVelocity = angular_velocity
                        obj.body.inertia = inertia
                        obj.body.linearDamping = linear_damping
                        obj.body.linearVelocity = linear_velocity
                        obj.body.localCenter = local_center
                        # obj.body.mass = mass

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
