import tspio
import tsputil
import platform
import subprocess
import os
import copy
from random import randint


class SolverModule:

    def __init__(self, parent, datacontroller):

        self._parent = parent
        self._datacontroller = datacontroller

        self._datacontroller.registerData('path', {})

    def emptySolution(self):
        self._datacontroller.commitChange('path', {})

    def concorde(self):
        nodes = self._datacontroller.getData('nodes')
        if len(nodes):
            scale = self._datacontroller.getData('scale')
            comment = "GENERATED TEMPORARY FILE"
            dummy = tsputil.FilenameWrapper("tmpfile.tsp")
            # generate temporary file containing the current problem
            filename = tspio.exportTSP(nodes, scale, comment, dummy)
            directory = os.path.dirname(os.path.realpath(__file__))

            # Check operating system first
            sysos = platform.system()
            # and call the corresponding binary of concorde
            if sysos == "Darwin":
                subprocess.call([directory + "/../bin/concorde-osx", filename])
            elif sysos == "Linux":
                subprocess.call(
                    [directory + "/../bin/concorde-fedora", filename])
            elif sysos == "Windows":
                return  # this function is not supported under windows yet
            else:
                return
            # open solutionfile and parse solution string
            basename = os.path.splitext(filename)[0]
            solution = tspio.parseSolutionfile(basename + ".sol")
            # delete files generated by concorde
            file_prefixes = ["", "O"]
            file_extensions = [".tsp", ".sol", ".mas", ".pul", ".sav"]
            for pre in file_prefixes:
                for ext in file_extensions:
                    fileToDelete = pre + basename + ext
                    if os.path.isfile(fileToDelete):
                        os.remove(fileToDelete)

            tour = solution.split()
            tour = list(map(int, tour))
            tour.append(tour[0])
            result = {'Tour' : tour,
                      'Tourlength' : tsputil.getPathLength(nodes, scale, tour)}
            self._datacontroller.commitChange('path', result)

    def convexHullHelper(self, nodes):
        if len(nodes):
            points = []

            for n in nodes:
                points.append((n.x, n.y))

            hull = tsputil.convex_hull(points)
            hull_nodes = []
            for p in hull:
                for n in nodes:
                    pos = (n.x, n.y)
                    if (pos == p):
                        hull_nodes.append(n)
            result = []
            for node in hull_nodes:
                result.append(node.id)
            result.append(result[0])
            return result


    def convexHull(self):
        """ Returns all nodes defining the convex_hull or lying on its edge."""
        nodes = self._datacontroller.getData('nodes')
        scale = self._datacontroller.getData('scale')
        hull = self.convexHullHelper(nodes)
        if hull:
            result = {'Tour' : hull,
                      'Tourlength' : tsputil.getPathLength(nodes, scale, hull),
                      'Start' : 'Most Top Left Node',
                      'Direction' : 'Clockwise'}
            self._datacontroller.commitChange('path', result)
