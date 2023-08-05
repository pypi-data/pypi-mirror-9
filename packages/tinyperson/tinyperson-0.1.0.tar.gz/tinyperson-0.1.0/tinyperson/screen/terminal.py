__author__ = 'Brendon Muschamp'
__copyright__  = "Copyright 2015, Marbon Bros Ltd"
__license__ = "GPLv3"
__status__ = "prototype"
__version__ = "0.1.0"
__email__ = "brendon@marbonbros.com"

from Queue import Empty
import curses
from threading import Thread

from drawille import Canvas

from ..base import BaseComponent


class TerminalScreen(BaseComponent):
    """
    Hello, this is the screen controller for my game.

    This is a handler for getting drawille onto the curses interface.

    On each draw attempt, this will take the assets from the game world and attempt to draw them on screen.

    terminal_window provides units in y,x format. This game provides units in x,y
    """

    BLANK_TERMINAL = {
        'frames': 0,
        'elapsed_time': 0
    }

    def __init__(self, terminal_window, initial_state, is_test):
        """
        Assume that curses has already been initialize
        :param initial_state: first state of the terminal
        :param is_test: is this being tested/debugged?
        :return: n/a
        """
        super(TerminalScreen, self).__init__(initial_state, is_test)
        self.terminal_window = terminal_window
        self.canvas = Canvas()
        self._refresh_size()

        if is_test:
            print "terminal is %s wide, %s high" % (self.width, self.height)

        terminal_thread = Thread(
            group=None,
            target=curses.wrapper,
            name="Screen Thread",
            args=(self.draw,),
            kwargs={}
        )

        terminal_thread.start()


    def _is_frame_valid(self, frame):
        return frame is not None and len(frame) > 0

    def _refresh_size(self):
        """

        Example terminal:

        x is blank
        H is border block
        o is game panel

        XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
        XXHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHXX
        XXHooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooHXX
        XXHooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooHXX
        XXHooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooHXX
        XXHooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooHXX
        XXHooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooHXX
        XXHooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooHXX
        XXHooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooHXX
        XXHooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooHXX
        XXHooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooHXX
        XXHooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooHXX
        XXHooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooHXX
        XXHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHXX
        XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

        braile is 2 wide, 4 high.

        :return: (width, height) of the terminal game panel
        """
        height, width = self.terminal_window.getmaxyx()
        self.width, self.height = (width - 6) * 2, (height - 4) * 4


    def draw(self, terminal_screen):
        """
        Push

        From self.queue_in, check for a tuple of items to be rendered on the terminal.
        frame instances must inherit from ScreenComponent
        :return: Nothing
        """

        frame = None
        terminal_screen.refresh()

        while self.active:
            try:
                frame = self.queue_in.get(timeout=0.1)
            except Empty:
                if self.is_test:
                    print "there aren't any frames to render, lets cycle through for kicks"

            self._refresh_size()

            if self._is_frame_valid(frame):
                self.canvas.set(0, 0)

                for asset in frame:
                    for xp, yp in asset.draw(self.width, self.height):
                        if self.is_test:
                            print "terminal is %s wide, %s high" % (self.width, self.height)
                            print "point x: %s, point y: %s" % (xp, yp)

                        if xp >= 0 and xp <= self.width and yp >= 0 and yp <= self.height:
                            self.canvas.set(6 + xp, yp + 8)

                rendered_frame = self.canvas.frame() + '\n'
                terminal_screen.addstr(0, 0, rendered_frame)
                terminal_screen.refresh()
                self.canvas.clear()

                frame = None