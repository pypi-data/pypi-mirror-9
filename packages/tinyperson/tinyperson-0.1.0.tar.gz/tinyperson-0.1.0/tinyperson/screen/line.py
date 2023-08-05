__author__ = 'Brendon Muschamp'
__copyright__  = "Copyright 2015, Marbon Bros Ltd"
__license__ = "GPLv3"
__status__ = "prototype"
__version__ = "0.1.0"
__email__ = "brendon@marbonbros.com"

from drawille import line

from .base import ScreenComponent


class Line(ScreenComponent):
    def __init__(self, x1, y1, x2, y2, world_width, world_height, is_test=False):
        state = {
            'x1': x1,
            'y1': y1,
            'x2': x2,
            'y2': y2
        }

        super(Line, self).__init__(state, world_width, world_height, is_test)

    def draw(self, terminal_width, terminal_height):
        """
        Translate line to
        """
        state = self.get_state()

        x, y = self.translate_xy(state['x1'], state['y1'], terminal_width, terminal_height)
        x2, y2 = self.translate_xy(state['x2'], state['y2'], terminal_width, terminal_height)

        return line(x, y, x2, y2)