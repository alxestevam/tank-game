from game.Sprite import Sprite
from game.Entity import Entity
from Box2D import *
import pygame
import pyclipper
import queue
import uuid


class Terrain(Entity):
    def __init__(self, env, color=(0, 0, 0)):
        surface_vertices = [b2Vec2(0, 0), b2Vec2(150, 0), b2Vec2(150, 20), b2Vec2(100, 15), b2Vec2(0, 20)]
        self.uidHex = uuid.uuid4().hex

        self.body = env.world.CreateStaticBody(position=(0, 0), userData=self)
        self.env = env
        self.color = color
        chain_shape = b2ChainShape(vertices=surface_vertices)
        fixture_def = b2FixtureDef(shape=chain_shape, density=1, friction=5, restitution=0)
        self.body.CreateFixture(fixture_def)
        self.canDestruct = False
        self.nextDestructionRadius = 0
        self.nextDestructionPosition = b2Vec2(0, 0)
        self.destructionQueue = queue.Queue()

        env.objects.append(self)

    def show(self, win):
        for fixtures in self.body.fixtures:
            shape = fixtures.shape
            vertices_screen = []
            for vertex_object in shape.vertices:
                vertex_world = self.body.transform * vertex_object
                vertex_screen = self.env.convert_world_to_screen(vertex_world)
                vertices_screen.append(vertex_screen)
            pygame.draw.polygon(win, self.color, vertices_screen)

    def add_destruction(self, position, radius):
        self.destructionQueue.put((position, radius))

    def update(self):
        if not self.destructionQueue.empty():
            destruction_position, destruction_radius = self.destructionQueue.get()
            surface_vertices = [[]]

            for fixture in self.body.fixtures:
                surface_vertices.append(fixture.shape.vertices)

            cv = self.env.make_circle_vertices(b2Vec2(destruction_position.x, destruction_position.y),
                                               self.env.m_from_px(destruction_radius))
            pc = pyclipper.Pyclipper()
            pc.AddPath(cv, pyclipper.PT_CLIP, True)
            pc.AddPaths(surface_vertices, pyclipper.PT_SUBJECT, True)

            clipped = pc.Execute(pyclipper.CT_DIFFERENCE, pyclipper.PFT_EVENODD, pyclipper.PFT_EVENODD)

            for f in self.body.fixtures:
                self.body.DestroyFixture(f)

            for vertices in clipped:
                chain_shape = b2ChainShape(vertices=vertices)
                self.body.CreateFixture(shape=chain_shape)
