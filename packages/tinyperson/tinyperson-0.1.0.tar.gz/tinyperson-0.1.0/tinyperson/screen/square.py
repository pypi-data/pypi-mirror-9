__author__ = 'Brendon Muschamp'
__copyright__  = "Copyright 2015, Marbon Bros Ltd"
__license__ = "GPLv3"
__status__ = "prototype"
__version__ = "0.1.0"
__email__ = "brendon@marbonbros.com"

import itertools
import logging

from .base import ScreenComponent
from .line import Line


logger = logging.getLogger("TinyPerson.screen")
logger.setLevel(logging.WARN)
logger.addHandler(logging.FileHandler("debug_screen.log"))


class Square(ScreenComponent):
    def __init__(self, x, y, half_width, world_width, world_height, is_test=False):
        """
        Initialize square

        :param x: X of center
        :param y: Y of center
        :param width: total width of square
        :param world_width: width of world
        :param world_height: height of world
        :param is_test: for debug
        """

        state = {
            'x': x,
            'y': y,
            'halfWidth': half_width
        }

        super(Square, self).__init__(state, world_width, world_height, is_test)

    def set_center(self, x, y):
        new_state = self.get_state()
        new_state['x'] = x
        new_state['y'] = y

        self.set_state(new_state)

        return self

    def set_width(self, width):
        new_state = self.get_state()
        new_state['width'] = width

        self.set_state(new_state)

        return self

    def draw(self, terminal_width, terminal_height):
        state = self.get_state()
        half_width = state['halfWidth']
        width = half_width * 2
        tl_x = state['x'] - half_width
        tl_y = state['y'] - half_width

        bl_x = tl_x
        bl_y = tl_y + width

        br_x = tl_x + width
        br_y = bl_y

        tr_x = br_x
        tr_y = tl_y

        logger.debug("SQUARE: %s, %s, %s, %s, %s, %s, %s, %s" % (tl_x, tl_y, bl_x, bl_y, tr_x, tr_y, br_x, br_y))

        return itertools.chain(
            # Top Line
            Line(tl_x, tl_y, tr_x, tr_y, self.world_width, self.world_height).draw(terminal_width, terminal_height),
            # Left Line
            Line(tl_x, tl_y, bl_x, bl_y, self.world_width, self.world_height).draw(terminal_width, terminal_height),
            # Bottom Line
            Line(bl_x, bl_y, br_x, br_y, self.world_width, self.world_height).draw(terminal_width, terminal_height),
            # Right Line
            Line(tr_x, tr_y, br_x, br_y, self.world_width, self.world_height).draw(terminal_width, terminal_height),
        )
