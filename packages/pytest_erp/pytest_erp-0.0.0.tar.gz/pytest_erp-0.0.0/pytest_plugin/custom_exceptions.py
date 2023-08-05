import logging

__author__ = 'kiryl_zayets'

class ItemNotClosed(Exception):
    pass

class ItemNotStarted(Exception):
    pass

class MoreThanOneFound(Exception):
    pass

class NothingFound(Exception):
    pass