import subprocess
import os
import tspio

colors = ["Black", "Red", "Green", "Blue", "Orange", "Cyan",
          "Magenta", "Yellow", "Gray", "White", "Brown",
          "Pink", "Purple", "Violet"]




def solveTSP(filename,callback):
    out = subprocess.check_output(["./concorde", filename])
    #print(out.decode("utf-8"))
    #open solutionfile and parse solution string
    basename = os.path.splitext(filename)[0]
    solution = tspio.parseSolutionfile(basename + ".sol")
    callback(solution.split())




class FilenameWrapper:
    def __init__(self,filename):
        self.name = filename
