from game.Tank import Tank
from pygame.color import THECOLORS
from random import random


class Character:
    def __init__(self, env, player, team):
        skin_number = player.clientInfo['currentSkin']
        # TODO: Put skin number in tank construction
        position = ((random()*(env.m_from_px(env.screenSize.x) - env.m_from_px(50)))
                    + env.m_from_px(50), env.m_from_px(300))
        self.tank = Tank(env, position, THECOLORS['black'])
        self.uidHex = player.uidHex
        self.team = team
        player.character = self
        self.player = player
        self.surrender = False

    def shoot(self, energy):
        if self.tank.health > 0:
            self.tank.server_shoot(energy)
