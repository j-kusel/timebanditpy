from timebandit.network.server import Server
from timebandit.lib import tbFile

import os
import time

class Metronome(object):
    def __init__(self, file):
        self.file = file
