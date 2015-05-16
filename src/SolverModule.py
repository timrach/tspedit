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


    def convexHullModel(self, _start='random', _direction='random'):
        nodes = self._datacontroller.getData('nodes')
        if nodes:
            """Step 1: Sketch the connections between adjacent boundary
                       points of the convex hull."""
            #hull is a list of ids, not nodes
            hull = self.convexHullHelper(nodes)
            print("Step 1: Identified hull:" + str(hull))
            """Step 2: Select a starting point and a direction (randomly). """
            #start is an id not a node
            start = randint(0, (len(nodes) - 1))
            #directions: -1 = ccw, 1 = cw
            direction = randint(0,1) 
            """ if direction is ccw , reverse hull. the hull is always 
             generated cw"""
            if direction == 0:
                direction = -1
            """ if start or direction were predefined apply the values """
            if not _start is 'random':
                start = _start
            if not _direction is 'random':
                direction = _direction

            print("Step 2: Start is " + str(start) + ", direction is " + str(direction))
            """ Step 3: If the starting point is on the boundary, 
            the starting node is the current node. """
            if start in hull:
                """The arc connecting the current node to the adjacent boundary 
                node in the direc- tion of travel is referred to as the 
                current arc."""
                print("Step 3: Start is in hull")
                cn_index = hull.index(start)
                an_index = (cn_index + 1) % (len(hull))

                current_node = hull[cn_index]
                adjacent_node = hull[an_index]      
                """Proceed immediately to Step 4."""
            else:
                print("Step 3: Start is not in hull")
                """If the starting point is not on the boundary, apply the 
                insertion rule to find the closest arc on the boundary. """
                closest_arc = self.findClosestArc(start, hull, nodes, direction)
                """Connect the starting point to the end node of the closest 
                arc which is in the direction of travel. 
                This node becomes the current node."""
                #insert startnode into hull
                hull.insert(hull.index(closest_arc[1]), start)
                #end
                current_node = start
                adjacent_node = hull[hull.index(closest_arc[1])]
                print("Inserted node, new hull is: " + str(hull))
            while len(hull) <= len(nodes):
                print("Step 4")
                """Step 4: Apply the insertion criterion to identify which 
                unconnected interior point is closest to the current arc. 
                Apply the insertion criterion to check whether the closest node is
                closer to any other arc."""
                counter = 0
                while True:
                    current_arc = (current_node, adjacent_node)
                    print("Current arc is " + str(current_arc))
                    interior_node = self.findClosestInteriorNode(current_arc, hull, nodes)
                    is_closer = self.isCloserToOtherArc(interior_node, current_arc, hull, nodes, direction)
                    """If not, proceed to Step 5. If it is, move to the end node of 
                    the current arc. This becomes the current node. Repeat Step 4."""
                    if not is_closer:
                        print("Found closest point, proceed with Step 5")
                        break
                    else:
                        print("Point is closer to another arc, move forward and repeat Step 4.")
                        current_node = current_arc[1]
                        an_index = (hull.index(current_node) + 1) % (len(hull))
                        adjacent_node = hull[an_index]
                        counter += 1
                """Step 5: Insert the closest node. The connection between the 
                current node and the newly inserted node becomes the current arc. 
                Retaining the current node, return to Step 4 and repeat Steps 4 and 
                5 until a complete tour is obtained"""
                hull.insert(hull.index(adjacent_node),interior_node)
                adjacent_node = interior_node
                print("Step 5: Inserted node, new hull is: " + str(hull))
            print("Found solution: " + str(hull))
            dirstring = "Clockwise"
            if direction == -1:
                hull.reverse()
                dirstring = "Counter Clockwise"
            if (_direction == 'random'):
                dirstring += " (random)"
            scale = self._datacontroller.getData('scale')
            result = {'Tour' : hull,
                      'Tourlength' : tsputil.getPathLength(nodes, scale, hull),
                      'Start' : str(_start),
                      'Direction' : dirstring}
            self._datacontroller.commitChange('path', result)


    def findClosestInteriorNode(self, current_arc, hull, nodes):
        lengths = [float("inf") for x in range(len(nodes))]
        for (j,node) in enumerate(nodes):
            if not node.id in hull:
                i = hull.index(current_arc[1])
                hull.insert(i, node.id)
                lengths[j] = (tsputil.getPathLength(nodes,100,hull))
                hull.pop(i)
        result = lengths.index(min(lengths))
        print(lengths)
        print("Closest interior point is :" + str(result))
        return result

    def isCloserToOtherArc(self, interior_node, arc, hull, nodes, direction):
        cl = self.findClosestArc(interior_node, hull, nodes, direction)
        result = not ((cl == arc) or (cl[::-1] == arc))
        return result
        

    def findClosestArc(self, point, _hull, nodes, direction, rule='CI'):
        hull = copy.deepcopy(_hull)
        lengths = []
        print("point is:" + str(point))
        print("hull is:" + str(hull))
        for i in range(0, len(hull) - 1):
            hull.insert(i, point)
            lengths.append(tsputil.getPathLength(nodes,100,hull))
            hull.pop(i)
        ci_index = lengths.index(min(lengths))
        print(lengths)
        an_index = hull[(ci_index-1)%len(hull)]
        result =  (an_index,hull[ci_index])
        print("Closest Arc to " + str(point) + " is " + str(result))
        return result
