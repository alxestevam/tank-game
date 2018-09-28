from game.Sprite import Sprite
from Box2D import *
import pygame


class Bullet(Sprite):
    def __init__(self, env, pos, color, radius):
        self.radius = radius
        self.color = color
        self.env = env
        self.body = env.world.CreateDynamicBody(position=pos, userData=self)
        self.can_remove = False
        shape = b2CircleShape(radius=env.m_from_px(radius))
        fixture_def = b2FixtureDef(shape=shape, density=1, friction=1, restitution=0.5)
        self.body.CreateFixture(fixture_def)
        self.explosion_radius = 50

        env.objects.append(self)

    def apply_impulse(self, force):
        self.body.ApplyLinearImpulse(force, self.body.position, True)

    def show(self, win):
        for fixtures in self.body.fixtures:
            shape = fixtures.shape
            if hasattr(shape, 'radius'):
                pygame.draw.circle(win, self.color, self.env.convert_world_to_screen(self.body.position),
                                   self.radius)

    def update(self):
        if self.can_remove:
            self.env.world.DestroyBody(self.body)
            self.env.objects.remove(self)
