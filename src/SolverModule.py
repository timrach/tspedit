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
        self._datacontroller.registerData('pathsteps', [])

    def emptySolution(self):
        self._datacontroller.commitChange('pathsteps', [])
        self._datacontroller.commitChange('path', {})

    """------------------------------------------------------------------------
       --------------------------- Optimal Tour -------------------------------
       ------------------------------------------------------------------------
       Uses the tool concorde to find the optimal tour in the problem.
       See  http://www.math.uwaterloo.ca/tsp/concorde.html for more information
   """

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
            result = {'Tour': tour,
                      'Tourlength': tsputil.getPathLength(nodes, scale, tour)}
            steps = [{'Tour': [], 'Tourlength': 0}, result]

            self._datacontroller.commitChange('pathsteps', steps)
            self._datacontroller.commitChange('path', result)

    def convexHullHelper(self, nodes):
        if len(nodes):
            # convert nodes into points (x,y)
            points = list(map(lambda n: (n.x, n.y), nodes))
            # get convex hull as list of ids
            result = list(map(lambda p: tsputil.findNodeByCoords(p, nodes).id,
                              tsputil.convex_hull(points)))
            result.append(result[0])
            return result
        else:
            return None

    def convexHull(self):
        """ Returns all nodes defining the convex_hull or lying on its edge."""
        nodes = self._datacontroller.getData('nodes')
        scale = self._datacontroller.getData('scale')
        hull = self.convexHullHelper(nodes)
        if hull:
            result = {'Tour': hull,
                      'Tourlength': tsputil.getPathLength(nodes, scale, hull),
                      'Start': 'Most Top Left Node',
                      'Direction': 'Clockwise'}
            self._datacontroller.commitChange('path', result)

    def convexHullModel(self, _start='random', _direction='random'):
        """------------------------------------------------------------------------
           ------------------------ Convex Hull Model -----------------------------
           ------------------------------------------------------------------------


           A model for the simulation of human solving strategies for TSP, designed
           by MacGregor et al.
           Description comments in the code are citations from the original paper:


        """
        steps = [{'Tour': [], 'Tourlength': 0}]
        nodes = self._datacontroller.getData('nodes')
        scale = self._datacontroller.getData('scale')

        if nodes:
            """Step 1: Sketch the connections between adjacent boundary
                       points of the convex hull."""
            # hull is a list of ids, not nodes,the hull is always generated CW
            hull = self.convexHullHelper(nodes)
            """Step 2: Select a starting point and a direction (randomly). """
            # start is an id not a node
            starts = list(filter(lambda n: n.start, nodes))
            if not len(starts):
                starts = nodes
            else:
                _start = 'Random from marked nodes'
            start = starts[randint(0, (len(starts) - 1))].id
            # directions: -1 = ccw, 1 = cw
            if not _direction is 'random':
                direction = _direction
            else:
                direction = randint(0, 1)
                dirstring = "Clockwise"
            # if direction is ccw ,reverse hull
            if not direction == 1:
                dirstring = "Counter Clockwise"
                if (_direction == 'random'):
                    dirstring += " (random)"
                hull.reverse()

            steps.append({'Tour': copy.deepcopy(hull),
                          'Tourlength': tsputil.getPathLength(nodes,
                                                              scale, hull),
                          'Start': str(_start),
                          'Direction': dirstring})

            """ Step 3: If the starting point is on the boundary, 
            the starting node is the current node. """
            if start in hull:
                """The arc connecting the current node to the adjacent boundary 
                node in the direc- tion of travel is referred to as the 
                current arc."""
                # gset the current node
                cn_index = hull.index(start)
                current_node = hull[cn_index]
                # get adjacent node
                an_index = (cn_index + 1) % (len(hull))
                adjacent_node = hull[an_index]
                """Proceed immediately to Step 4."""
            else:
                """If the starting point is not on the boundary, apply the 
                insertion rule to find the closest arc on the boundary. """
                closest_arc = self.findClosestArc(start, hull, nodes)
                """Connect the starting point to the end node of the closest 
                arc which is in the direction of travel. 
                This node becomes the current node."""
                # insert startnode into hull
                hull.insert(hull.index(closest_arc[0]) + 1, start)
                steps.append({'Tour': copy.deepcopy(hull),
                              'Tourlength': tsputil.getPathLength(nodes,
                                                                  scale, hull),
                              'Start': str(_start),
                              'Direction': dirstring})
                # update current arc nodes
                current_node = start
                adjacent_node = hull[hull.index(closest_arc[1])]
            """Step 4: Apply the insertion criterion to identify which 
                unconnected interior point is closest to the current arc."""
            # repeat step 4 and 5 until all nodes are included in the path
            while len(hull) <= len(nodes):
                while True:
                    current_arc = (current_node, adjacent_node)
                    # find closest node not in the hull
                    interior_node = self.findClosestInteriorNode(
                        current_arc, hull, nodes)
                    """Apply the insertion criterion to check whether the closest node is
                       closer to any other arc."""
                    is_closer = self.isCloserToOtherArc(
                        interior_node, current_arc, hull, nodes)
                    """If not, proceed to Step 5. If it is, move to the end node of 
                    the current arc. This becomes the current node. Repeat Step 4."""
                    if not is_closer:
                        break
                    else:
                        current_node = current_arc[1]
                        an_index = (hull.index(current_node) + 1) % (len(hull))
                        adjacent_node = hull[an_index]
                """Step 5: Insert the closest node. The connection between the 
                current node and the newly inserted node becomes the current arc. 
                Retaining the current node, return to Step 4 and repeat Steps 4 and 
                5 until a complete tour is obtained"""
                hull.insert(hull.index(current_node) + 1, interior_node)
                adjacent_node = interior_node
                steps.append({'Tour': copy.deepcopy(hull),
                              'Tourlength': tsputil.getPathLength(nodes,
                                                                  scale, hull),
                              'Start': str(_start),
                              'Direction': dirstring})

            self._datacontroller.commitChange('pathsteps', steps)
            self._datacontroller.commitChange('path', steps[-1])

    def findClosestInteriorNode(self, current_arc, hull, nodes):
        lengths = [float("inf") for x in range(len(nodes))]
        for (j, node) in enumerate(nodes):
            if not node.id in hull:
                i = hull.index(current_arc[1])
                hull.insert(i, node.id)
                lengths[j] = (tsputil.getPathLength(nodes, 100, hull))
                hull.pop(i)
        return lengths.index(min(lengths))

    def isCloserToOtherArc(self, interior_node, arc, hull, nodes):
        cl = self.findClosestArc(interior_node, hull, nodes)
        return not ((cl == arc) or (cl[::-1] == arc))

    def findClosestArc(self, point, _hull, nodes):
        hull = copy.deepcopy(_hull)
        lengths = [float("inf") for x in range(len(hull))]
        for i in range(1, len(hull)):
            hull.insert(i, point)
            lengths[i] = (tsputil.getPathLength(nodes, 100, hull))
            hull.pop(i)

        ci_index = lengths.index(min(lengths))
        an_index = (ci_index - 1) % len(hull)
        return (hull[an_index], hull[ci_index])

    def nearestNeighbor(self):
        steps = [{'Tour': [], 'Tourlength': 0}]
        tour = []
        ordiginal_nodes = self._datacontroller.getData('nodes')
        nodes = copy.deepcopy(ordiginal_nodes)
        scale = self._datacontroller.getData('scale')

        """Step 1: Get a tour start """
        starts = list(filter(lambda n: n.start, nodes))
        _start = 'Random from marked nodes'
        if not len(starts):
            starts = nodes
            _start = 'Random from all nodes'
            
        current = nodes[randint(0, (len(starts) - 1))]
        while True:
            tour.append(current.id)
            nodes.remove(current)
            steps.append({'Tour': copy.deepcopy(tour),
                              'Tourlength': tsputil.getPathLength(
                                ordiginal_nodes, scale, tour),
                              'Start': str(_start),
                              'Direction': 'random'})
            if not len(nodes):
                break
            current = nodes[tsputil.nearestNeighbor(nodes, current)[0]]
        tour.append(tour[0])
        steps.append({'Tour': copy.deepcopy(tour),
                          'Tourlength': tsputil.getPathLength(
                            ordiginal_nodes, scale, tour),
                          'Start': str(_start),
                          'Direction': 'random'})
        self._datacontroller.commitChange('pathsteps', steps)
        self._datacontroller.commitChange('path', steps[-1])


