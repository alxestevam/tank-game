from game.Bullet import Bullet
from Box2D import *
import pygame
from math import sin, cos
from game.Entity import Entity
from game.Constants import Constants


class Tank(Entity):
    # TODO: Put sprite image at constructor
    def __init__(self, env, pos, color=(0, 0, 0), uid=None):
        # pos = env.convert_screen_to_world(pos[0], pos[1])
        pos = b2Vec2(pos)
        super(Tank, self).__init__(env, env.world.CreateDynamicBody(position=pos, userData=self), uid)

        self.angleArcDistance = Constants.TANK_CONFIG['physics']['angle_arc_distance']
        self.env = env
        self.color = color
        self.wheelRadius = Constants.TANK_CONFIG['physics']['wheel_radius']
        self.angle = b2_pi/4
        self.torque = Constants.TANK_CONFIG['physics']['torque']
        self.speed = Constants.TANK_CONFIG['physics']['speed']
        barrel_distance = Constants.TANK_CONFIG['physics']['gun_barrel_distance']
        barrel_distance = b2Vec2(env.m_from_px(barrel_distance[0]), env.m_from_px(barrel_distance[1]))
        self.gunBarrelDistance = barrel_distance
        # TODO: Apply radius variation with the card mechanics
        self.bullet_radius = 10
        self.direction = 1
        self.removeGravity = False
        self.normalBodyWithTerrain = b2Vec2(0, 0)
        self.health = Constants.TANK_CONFIG['max_health']
        self.healthBarRedColor = 0

        wheel_distance_m = self.env.m_from_px(Constants.TANK_CONFIG['physics']['wheel_distance_px'])

        shape = b2PolygonShape(box=(self.env.m_from_px(Constants.TANK_CONFIG['physics']['turret_width']),
                                    self.env.m_from_px(Constants.TANK_CONFIG['physics']['turret_height'])))

        fixture_def = b2FixtureDef(shape=shape,
                                   density=Constants.TANK_CONFIG['physics']['density'],
                                   friction=Constants.TANK_CONFIG['physics']['friction'],
                                   restitution=Constants.TANK_CONFIG['physics']['restitution'])
        self.body.CreateFixture(fixture_def)

        self.wheels, self.springs = [], []

        offset_y = self.env.m_from_px(Constants.TANK_CONFIG['physics']['turret_height']/2+10)

        x = [-wheel_distance_m/2, wheel_distance_m]
        for x_p in x:
            wheel = env.world.CreateDynamicBody(position=(pos.x + x_p, pos.y - offset_y), userData=self)
            circle = b2CircleShape(radius=self.env.m_from_px(self.wheelRadius))
            fixture_def = b2FixtureDef(shape=circle,
                                       density=Constants.TANK_CONFIG['physics']['wheel_density'],
                                       friction=Constants.TANK_CONFIG['physics']['wheel_friction'],
                                       restitution=Constants.TANK_CONFIG['physics']['wheel_restitution'])
            wheel.CreateFixture(fixture_def)

            spring = env.world.CreateWheelJoint(
                bodyA=self.body,
                bodyB=wheel,
                anchor=wheel.position,
                motorSpeed=0.0,
                enableMotor=True,
                maxMotorTorque=self.torque,
                frequencyHz=Constants.TANK_CONFIG['physics']['frequency_hz'],
                axis=(0, 1)
            )

            self.wheels.append(wheel)
            self.springs.append(spring)

            if self.direction == 1 and self.angle < b2_pi/2:
                self.flip()

    def move(self, direction):
        if direction == 1:  # Left
            if self.direction == 2:
                self.direction = 1
                self.flip()
            for spring in self.springs:
                spring.motorSpeed = self.speed
        elif direction == 2:  # Right
            if self.direction == 1:
                self.direction = 2
                self.flip()
            for spring in self.springs:
                spring.motorSpeed = -self.speed

    def flip(self):
        self.angle = b2_pi - self.angle
        self.gunBarrelDistance.x *= -1

    def stop(self):
        for spring in self.springs:
            spring.motorSpeed = 0.0

    def server_shoot(self, energy):
        bullet = Bullet(self.env, (self.body.position + self.gunBarrelDistance), radius=self.bullet_radius)
        bullet.apply_impulse(b2Vec2(cos(self.angle)*energy, sin(self.angle)*energy))

    def update_angle(self, increase):
        if self.direction == 1:
            angle_speed = -0.01
        else:
            angle_speed = 0.01
        if not increase:
            angle_speed *= -1
        self.angle += angle_speed

    def draw_angle_arc(self, win):
        # TODO: The character rendering will be placed with images
        pos = b2Vec2(self.env.convert_world_to_screen(self.body.position))
        rect = [pos.x - self.angleArcDistance / 2, pos.y - self.angleArcDistance / 2, self.angleArcDistance,
                self.angleArcDistance]

        if self.direction == 1:
            pygame.draw.arc(win, (0, 255, 0), rect, b2_pi - 2, b2_pi)
        else:
            pygame.draw.arc(win, (0, 255, 0), rect, 0, 2)

        point1 = (pos.x + (self.angleArcDistance / 2 - 40) * cos(self.angle),
                  pos.y - (self.angleArcDistance / 2 - 40) * sin(self.angle))

        point2 = (pos.x + (self.angleArcDistance / 2 - 5) * cos(self.angle),
                  pos.y - (self.angleArcDistance / 2 - 5) * sin(self.angle))
        # Draw the current angle
        pygame.draw.line(win, (255, 0, 0), point1, point2)

    def take_damage(self, damage):
        if self.health - damage <= 0:
            self.health = 0
        else:
            self.health -= damage

    def draw_health_bar(self, win):
        size = 100
        ini_position = b2Vec2(self.env.convert_world_to_screen(self.body.position)) - b2Vec2(70, 100)
        pygame.draw.rect(win, (self.translate(self.health, 0, 100, 255, 0), 0, self.translate(self.health, 0, 100, 0, 255)),
                         (ini_position.x, ini_position.y, self.health/Constants.TANK_CONFIG['max_health'] * size, 20))

    @staticmethod
    def translate(value, left_min, left_max, right_min, right_max):
        # Figure out how 'wide' each range is
        left_span = left_max - left_min
        right_span = right_max - right_min

        # Convert the left range into a 0-1 range (float)
        value_scaled = float(value - left_min) / float(left_span)

        # Convert the 0-1 range into a value in the right range.
        return right_min + (value_scaled * right_span)

    def show(self, win):
        self.draw_angle_arc(win)
        self.draw_health_bar(win)
        for fixtures in self.body.fixtures:
            shape = fixtures.shape
            vertices_screen = []
            for vertex_object in shape.vertices:
                vertex_world = self.body.transform * vertex_object
                vertex_screen = self.env.convert_world_to_screen(vertex_world)
                vertices_screen.append(vertex_screen)
            pygame.draw.polygon(win, self.color, vertices_screen)

        for wheel in self.wheels:
            for fixtures in wheel.fixtures:
                shape = fixtures.shape
                if hasattr(shape, 'radius'):
                    pygame.draw.circle(win, (255, 0, 0), self.env.convert_world_to_screen(wheel.position),
                                       self.wheelRadius)
