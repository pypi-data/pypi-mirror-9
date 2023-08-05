__author__ = 'Brendon Muschamp'
__copyright__  = "Copyright 2015, Marbon Bros Ltd"
__license__ = "GPLv3"
__status__ = "prototype"
__version__ = "0.1.0"
__email__ = "brendon@marbonbros.com"

import curses
from time import sleep
from threading import Thread

from .screen import TerminalScreen, Square
from .controller import GameController, UP, DOWN, LEFT, RIGHT
from .physics import PhysicsWorld


FPS = 60.0
RENDER_STEP = 1. / FPS
PHYSICS_FPS = 60.0
PHYSICS_STEP = 1. / PHYSICS_FPS

# Window is a square
WINDOW_WIDTH = 50

import logging

logger = logging.getLogger("TinyPerson.MainLoop")
logger.setLevel(logging.WARN)
logger.addHandler(logging.FileHandler("debug.log"))


class GameLoop(object):
    """
    Wrapper for the game
    """

    def __init__(self, world_width, world_height, is_test=False):
        if is_test:
            print "starting game"

        self.window_physics = PhysicsWorld()

        self.stdscr = curses.initscr()
        self.stdscr.refresh()
        self.world_width = world_width
        self.world_height = world_height

        self.term = TerminalScreen(self.stdscr, TerminalScreen.BLANK_TERMINAL, is_test)
        self.controller = GameController(self.stdscr, GameController.RESET_CONTROLLER, is_test)
        self.active = True
        self.assets = []

    def convert_world_to_square(self, world_x, world_y):
        half_square = WINDOW_WIDTH / 2

        return world_x + ((self.world_width / 2) - half_square), world_y + ((self.world_height / 2) - half_square)


    def draw_assets(self):
        self.assets.append(
            Square(self.world_width / 2, self.world_height / 2, WINDOW_WIDTH / 2, self.world_width, self.world_height))

        player_x, player_y = self.convert_world_to_square(
            *self.window_physics.window_player_position(WINDOW_WIDTH, WINDOW_WIDTH))

        player = Square(player_x, player_y, 1, self.world_width, self.world_height)

        while self.active:
            player_x, player_y = self.convert_world_to_square(
                *self.window_physics.window_player_position(WINDOW_WIDTH, WINDOW_WIDTH))
            logger.debug("player position: %s, %s" % (player_x, player_y))
            player.set_center(player_x, player_y)

            self.term.queue_in.put(self.assets + [player])

            sleep(RENDER_STEP)

    def step_physics(self):
        while self.active:
            self.window_physics.step(PHYSICS_STEP)

            controller_state = self.controller.get_state()

            self.window_physics.move_player(
                up=controller_state[UP],
                down=controller_state[DOWN],
                left=controller_state[LEFT],
                right=controller_state[RIGHT]
            )

            # should the game end?
            if not self.controller.is_enabled():
                self.goodbye()

            sleep(PHYSICS_STEP)

    def start(self):
        render_thread = Thread(
            group=None,
            target=self.draw_assets,
            name="Render Loop",
            args=(),
            kwargs={}
        )

        physics_thread = Thread(
            group=None,
            target=self.step_physics,
            name="Physics Loop",
            args=(),
            kwargs={}
        )

        render_thread.start()
        physics_thread.start()


    def goodbye(self):
        self.active = False
        self.term.disable_component()
        self.controller.disable_component()

    def __exit__(self, type, value, traceback):
        if self.is_test:
            print type, value, traceback

        self.goodbye()

