from Box2D import b2Vec2


class Constants:
    FPS = 60
    SERVER_PLAYER_LIMIT = 100
    BUFFER_SIZE = 4096*10
    DEFAULT_PORT = 10939
    TIMEOUT = 2.0
    COMMAND_RATE = 60
    ROOM_CAPACITIES = {'solo': 1, 'duo': 2, 'squad': 4}
    SCREEN_SIZE = (1280, 720)
    TANK_CONFIG = {
        'physics': {
            'turret_width': 20,
            'turret_height': 20,
            'density': 1,
            'friction': 0,
            'restitution': 0,
            'wheel_density': 1,
            'wheel_friction': 100,
            'wheel_restitution': 0.1,
            'wheel_radius': 20,
            'wheel_distance_px': 30,
            'frequency_hz': 60,
            'torque': 500,
            'speed': 5,
            'gun_barrel_distance': (30, 30),
            'angle_arc_distance': 150
        }
    }
    TERRAIN_CONFIG = {
        '1': {
            'vertices': [[0, 0], [150, 0], [150, 20], [100, 20], [0, 20]],
            'sprite_image': None
        }
    }
