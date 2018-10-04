from game.Entity import Entity
from Box2D import *
import pygame
import uuid


class Bullet(Entity):
    def __init__(self, env, pos, color=(0, 100, 100), radius=10, bullet_type=1):
        super(Bullet, self).__init__(env, env.world.CreateDynamicBody(position=pos, userData=self))
        self.radius = radius
        self.color = color
        self.env = env
        self.can_remove = False
        shape = b2CircleShape(radius=env.m_from_px(radius))
        fixture_def = b2FixtureDef(shape=shape, density=1, friction=1, restitution=0.5)
        self.body.CreateFixture(fixture_def)
        # TODO: Implement different types and explosion_radius
        self.bullet_type = bullet_type
        self.explosion_radius = 50

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
