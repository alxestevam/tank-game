from game.Sprite import Sprite
import uuid


class Entity(Sprite):
    def __init__(self, env, body):
        self.uidHex = uuid.uuid4().hex
        self.body = body
        env.objects[self.uidHex] = self
