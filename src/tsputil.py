import subprocess
import os
import tspio

colors = ["Black", "Red", "Green", "Blue", "Orange", "Cyan",
          "Magenta", "Yellow", "Gray", "White", "Brown",
          "Pink", "Purple", "Violet"]


class FilenameWrapper:
    def __init__(self,filename):
        self.name = filename
