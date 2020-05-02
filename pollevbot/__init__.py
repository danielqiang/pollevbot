from sys import version_info

assert version_info >= (3, 7), "pollevbot requires python 3.7 or later"

from .pollbot import PollBot
import logging

# Log all messages as white text
WHITE = "\033[1m"
logging.basicConfig(level=logging.INFO,
                    format=WHITE + "%(asctime)s.%(msecs)03d [%(name)s] "
                                   "%(levelname)s: %(message)s",
                    datefmt='%Y-%m-%d %H:%M:%S')
