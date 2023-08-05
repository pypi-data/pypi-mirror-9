__author__ = 'Brendon Muschamp'
__copyright__  = "Copyright 2015, Marbon Bros Ltd"
__license__ = "GPLv3"
__status__ = "prototype"
__version__ = "0.1.0"
__email__ = "brendon@marbonbros.com"

from Queue import Queue


class BaseComponent(object):
    def __init__(self, initial_state, is_test=False):
        self.initial_state = initial_state.copy()
        self.state = initial_state.copy()
        self.queue_in = Queue()
        self.active = True
        self.is_test = is_test

    def disable_component(self):
        """
        Toggle the active flag so any threads inside the component know it's time to turn off

        :return: The instance used to call this func
        """
        self.active = False

        return self

    def enable_component(self):
        """
        Toggle the active flag so that it's enabled...
        IMPORTANT: This doesn't start any threads required by the component

        :return: The instance used to call this func
        """
        self.active = True

        return self

    def is_enabled(self):
        return self.active

    def get_state(self):
        """
        :return: The component state
        """

        return self.state.copy()

    def set_state(self, new_state):
        """

        :param new_state: State that is to be set on the component
        :return: instance of self, so that he have the option to chain commands
        """
        self.state = new_state.copy()

        return self
