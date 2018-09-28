from Box2D import *
from Bullet import Bullet
from Terrain import Terrain


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

