import pygame
from pygame.color import THECOLORS
from Box2D import *
from game.Environment import Environment
from game.Terrain import Terrain
from game.Tank import Tank
from game.Sprite import Sprite
from game.Bullet import Bullet
from game.ContactListener import ContactListener
from game.Constants import Constants


def draw_charging_bar(win, charging_level):
    size = 500
    pygame.draw.rect(win, THECOLORS['red'], (0, 0, charging_level/max_charge * size, 20))


screen_size = (1280, 720)
FPS = 60

# Creating the Box2d World and Environment
world = b2World(gravity=(0, -20), contactListener=ContactListener())
env = Environment(screen_size, world)
timeStep = 1.0 / FPS
vel_iters, pos_iters = 10, 10

# Initializing the game
pygame.init()
win = pygame.display.set_mode(screen_size)
run = True
clock = pygame.time.Clock()

terrain = Terrain(env, Constants.TERRAIN_CONFIG['1']['vertices'])

# Creating a tank to test

tank = Tank(env, (100, 100), THECOLORS['black'])

# Time counter
time = 0

# Game Variables
charge_level = 0
charging_speed = 1
max_charge = 200
charging = False
shoot = True

while run:
    dt_s = float(clock.tick(FPS)) * 1e-3
    world.Step(timeStep, vel_iters, pos_iters)

    mouse = pygame.mouse.get_pressed()
    mousePos = pygame.mouse.get_pos()

    time += dt_s  # Increasing the time counter
    win.fill(THECOLORS['white'])

    for uid, obj in env.objects.copy().items():
        if isinstance(obj, Sprite):
            obj.show(win)
        if isinstance(obj, Terrain) or isinstance(obj, Bullet):
            obj.update()

    cmd = env.get_local_user_input()
    ctrl = env.controls()

    if ctrl['angle_update']:
        tank.update_angle(ctrl['angle_increase'])
    if ctrl['player_move']:
        tank.move(ctrl['move_direction'])
    if not ctrl['player_move']:
        tank.stop()

    if cmd == 0:
        run = False
        break

    elif cmd == 1:
        charging = True

    elif cmd == 2:
        charging = False
        tank.server_shoot(charge_level)
        print('TIRO', charge_level)
        charge_level = 0

    if charging:
        if charge_level < max_charge - charging_speed:
            charge_level += charging_speed

    draw_charging_bar(win, charge_level)
    pygame.display.update()

pygame.quit()
