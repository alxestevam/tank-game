from Box2D import *
from game.Bullet import Bullet
from game.Terrain import Terrain
from game.Tank import Tank


class ContactListener(b2ContactListener):
    def __init__(self):
        b2ContactListener.__init__(self)

    def BeginContact(self, contact):
        object_1 = contact.fixtureA.body.userData
        object_2 = contact.fixtureB.body.userData

        if isinstance(object_1, Bullet) and isinstance(object_2, Terrain) or \
                isinstance(object_2, Bullet) and isinstance(object_1, Terrain):
            if isinstance(object_1, Bullet):
                bullet = object_1
                terrain = object_2
            else:
                bullet = object_2
                terrain = object_1

            next_destruction_position = b2Vec2(contact.worldManifold.points[0])
            next_destruction_radius = bullet.explosion_radius
            terrain.add_destruction(next_destruction_position, next_destruction_radius)
            bullet.can_remove = True

        if isinstance(object_1, Bullet) and isinstance(object_2, Tank) or \
                isinstance(object_2, Bullet) and isinstance(object_1, Tank):
            if isinstance(object_1, Bullet):
                bullet = object_1
                tank = object_2
            else:
                bullet = object_2
                tank = object_1

            bullet.can_remove = True
            tank.take_damage(bullet.damage)




