from Box2D import *
import math
import pygame
import threading


class Environment(threading.Thread):
    def __init__(self, screensize_tuple, world):
        threading.Thread.__init__(self, name='Environment Thread')
        self.world = world
        self.viewZoom = 10.0
        self.viewCenter = b2Vec2(0, 0.0)
        self.viewOffset = b2Vec2(0, 0)
        self.screenSize = b2Vec2(*screensize_tuple)
        self.flipX = False
        self.flipY = True
        self.objects = {}

    @staticmethod
    def to_json(obj):
        obj_class = obj.__class__.__name__

        if isinstance(obj, Box2D.b2Vec2):
            return {
                '__class__': obj_class,
                '__value__': [obj.x, obj.y]
            }

    def m_from_px(self, px):
        return px/self.viewZoom

    def px_from_m(self, m):
        return int(m*self.viewZoom)

    def convert_screen_to_world(self, x, y):
        self.viewOffset = self.viewCenter
        return b2Vec2((x + self.viewOffset.x) / self.viewZoom,
                      ((self.screenSize.y - y + self.viewOffset.y) / self.viewZoom))

    def convert_world_to_screen(self, point):
        self.viewOffset = self.viewCenter
        x = (point.x * self.viewZoom) - self.viewOffset.x
        if self.flipX:
            x = self.screenSize.x - x
        y = (point.y * self.viewZoom) - self.viewOffset.y
        if self.flipY:
            y = self.screenSize.y - y

        return int(round(x)), int(round(y))  # return tuple of integers

    @staticmethod
    def make_circle_vertices(point, radius):
        vertices = []
        i = 0
        sharpness = 0.5
        while i <= math.pi * 2 - 0.5:
            i += sharpness
            vertices.append(b2Vec2(int(point.x + radius * math.cos(i)), int(point.y + radius * math.sin(i))))

        return vertices

    @staticmethod
    def get_local_user_input():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 0
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return 1
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    return 2

    @staticmethod
    def controls():
        cmd = {}
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            cmd['player_move'] = True
            cmd['move_direction'] = 1
        elif keys[pygame.K_RIGHT]:
            cmd['player_move'] = True
            cmd['move_direction'] = 2
        else:
            cmd['player_move'] = False

        if keys[pygame.K_UP]:
            cmd['angle_update'] = True
            cmd['angle_increase'] = True
        elif keys[pygame.K_DOWN]:
            cmd['angle_update'] = True
            cmd['angle_increase'] = False
        else:
            cmd['angle_update'] = False

        return cmd
