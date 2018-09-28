from game.Bullet import Bullet
from game.Sprite import Sprite
from Box2D import *
import pygame
from math import sin, cos


class Tank(Sprite):
    def __init__(self, env, pos, color, turret_width, turret_height, density, friction, restitution,
                 wheel_density, wheel_friction, wheel_restitution, wheel_distance_px, wheel_radius, frequency_hz,
                 torque, speed, barrel_distance, angle_arc_distance):

        pos = env.convert_screen_to_world(pos[0], pos[1])
        self.angleArcDistance = angle_arc_distance
        self.env = env
        self.color = color
        self.wheelRadius = wheel_radius
        self.angle = b2_pi/4
        self.body = env.world.CreateDynamicBody(position=pos)
        self.torque = torque
        self.speed = speed
        barrel_distance = b2Vec2(env.m_from_px(barrel_distance[0]), env.m_from_px(barrel_distance[1]))
        self.gunBarrelDistance = barrel_distance
        self.bullet_radius = 10
        self.direction = 1

        wheel_distance_m = self.env.m_from_px(wheel_distance_px)

        shape = b2PolygonShape(box=(self.env.m_from_px(turret_width),
                                    self.env.m_from_px(turret_height)))

        fixture_def = b2FixtureDef(shape=shape, density=density, friction=friction, restitution=restitution)
        self.body.CreateFixture(fixture_def)

        self.wheels, self.springs = [], []

        offset_y = self.env.m_from_px(turret_height/2+10)

        x = [-wheel_distance_m/2, wheel_distance_m]
        for x_p in x:
            wheel = env.world.CreateDynamicBody(position=(pos.x + x_p, pos.y - offset_y))
            circle = b2CircleShape(radius=self.env.m_from_px(self.wheelRadius))
            fixture_def = b2FixtureDef(shape=circle, density=wheel_density, friction=wheel_friction,
                                       restitution=wheel_restitution)
            wheel.CreateFixture(fixture_def)

            spring = env.world.CreateWheelJoint(
                bodyA=self.body,
                bodyB=wheel,
                anchor=wheel.position,
                motorSpeed=0.0,
                enableMotor=True,
                maxMotorTorque=self.torque,
                frequencyHz=frequency_hz,
                axis=(0, 1)
            )

            self.wheels.append(wheel)
            self.springs.append(spring)

            if self.direction == 1 and self.angle < b2_pi/2:
                self.flip()

        env.objects.append(self)

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

    def shoot(self, energy):
        bullet = Bullet(self.env, (self.body.position + self.gunBarrelDistance), (0, 100, 100), self.bullet_radius)
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
        # TODO: A renderização do personagem será substituída por imagens
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

    def show(self, win):
        self.draw_angle_arc(win)
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