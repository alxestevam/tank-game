from game.Sprite import Sprite
import uuid


class Entity(Sprite):
    def __init__(self, env, body, uid=None):
        self.uidHex = uid if uid is not None else uuid.uuid4().hex
        self.body = body
        env.objects[self.uidHex] = self
