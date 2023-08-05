__author__ = 'Brendon Muschamp'
__copyright__  = "Copyright 2015, Marbon Bros Ltd"
__license__ = "GPLv3"
__status__ = "prototype"
__version__ = "0.1.0"
__email__ = "brendon@marbonbros.com"

import logging

import pymunk


logger = logging.getLogger("TinyPerson.physics")

# Physics world is a square
PHYSICS_WIDTH = 200
PHYSICS_HEIGHT = 200


def convert_physics_to_world(physics_x, physics_y, window_width, window_height):
    return window_width * (physics_x / PHYSICS_WIDTH), window_height * (physics_y / PHYSICS_HEIGHT)


class PhysicsWorld(object):
    def __init__(self, gravity=100.0):
        self.world = pymunk.Space()
        self.world.gravity = (0.0, 0.0)
        self.active = True

        static_body = pymunk.Body()
        static_lines = [
            # bottom
            pymunk.Segment(static_body, (0, 0), (PHYSICS_WIDTH, 0), 0.0),
            # left
            pymunk.Segment(static_body, (0, 0), (0, PHYSICS_HEIGHT), 0.0),
            # right
            pymunk.Segment(static_body, (PHYSICS_WIDTH, PHYSICS_HEIGHT), (PHYSICS_WIDTH, 0), 0.0),
            # top
            pymunk.Segment(static_body, (0, PHYSICS_HEIGHT), (PHYSICS_WIDTH, PHYSICS_HEIGHT), 0.0)
        ]

        for line in static_lines:
            line.elasticity = 0.95
        self.world.add(static_lines)

        mass = 10
        radius = 5
        inertia = pymunk.moment_for_circle(mass, 0, radius, (0, 0))
        self.main_player = pymunk.Body(mass, inertia)
        self.main_player._set_velocity_limit(100)
        self.main_player.position = 100, 100
        shape = pymunk.Circle(self.main_player, radius, (0, 0))
        shape.elasticity = 0.
        shape.friction = 4
        self.world.add(self.main_player, shape)

        logger.debug("Initialized physics world")

    def window_player_position(self, window_width, window_height):
        x, y = self.main_player.position
        return convert_physics_to_world(x, y, window_width, window_height)

    def move_player(self, up, down, left, right):
        """

        :param jump: bool
        :param left: bool
        :param right: bool
        :return:
        """

        x, y = self.main_player._get_velocity()

        if up:
            y -= 50

        if down:
            y += 50

        if left:
            x -= 50

        if right:
            x += 50

        self.main_player._set_velocity((x, y))

    def add(self, asset):
        self.world.add(asset)

    def remote(self, asset):
        self.world.remove(asset)

    def destroy(self):
        self.active = False

    def step(self, dt):
        if self.active:
            self.world.step(dt)
        else:
            logger.warn("The physics loop is not active")