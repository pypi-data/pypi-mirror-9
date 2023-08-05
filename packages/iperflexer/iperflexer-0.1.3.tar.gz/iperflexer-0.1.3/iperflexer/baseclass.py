
import logging


DOT_JOIN = "{0}.{1}"


class BaseClass(object):
    """
    This class holds the minimum common features.
    """
    def __init__(self):
        self._logger = None
        return

    @property
    def logger(self):
        """
        :return: A logging object.
        """
        if self._logger is None:
            self._logger = logging.getLogger(DOT_JOIN.format(self.__module__,
                                  self.__class__.__name__))
        return self._logger
# end BaseClass
