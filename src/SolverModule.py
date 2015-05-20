"""
    SolverModule.py
    See class description
"""
import tspio
import tsputil
import platform
import subprocess
import os
import copy
from random import randint


class SolverModule:

    """ The solver module includes all solving algorithms and bindings
        to external programs. Completed tours are passed to the given
        datacontroller, not the calling parent."""

    def __init__(self, parent, datacontroller):

        self._parent = parent
        self._datacontroller = datacontroller

        self._datacontroller.register_data('path', {})
        self._datacontroller.register_data('pathsteps', [])

    def empty_solution(self):
        """ commits an empty path and an empty pathsteps array"""
        self._datacontroller.commit_change('pathsteps', [])
        self._datacontroller.commit_change('path', {})

    def concorde(self):
        """------------------------------------------------------------------------
        --------------------------- Optimal Tour -------------------------------
        ------------------------------------------------------------------------
        Uses the tool concorde to find the optimal tour in the problem.
        See  http://www.math.uwaterloo.ca/tsp/concorde.html for more information
        """
        nodes = self._datacontroller.get_data('nodes')
        if len(nodes):
            scale = self._datacontroller.get_data('scale')
            comment = "GENERATED TEMPORARY FILE"
            # generate temporary file containing the current problem
            filename = tspio.export_tsp(nodes, scale, comment,
                                        tsputil.FilenameWrapper("tmpfile.tsp"))
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
            #the basename is the filename without path and extension
            basename = os.path.splitext(filename)[0]

            # open solution file and parse solution string
            solution = tspio.parse_solution_file(basename + ".sol")
            # generate a list of ids from the character list in the solution file
            tour = [int(char) for char in solution.split()]
            # concorde doesn't include the start again as end, so it is added here
            tour.append(tour[0])

            # delete files generated by concorde
            for prefix in ["", "O"]:
                for extension in [".tsp", ".sol", ".mas", ".pul", ".sav"]:
                    file_to_delete = directory + "/" + prefix + basename + extension
                    if os.path.isfile(file_to_delete):
                        os.remove(file_to_delete)

            result = construct_step(tour, 'Unknown', 'Unknown', nodes, scale)
            steps = [{'Tour': [], 'Tourlength': 0}, result]

            self._datacontroller.commit_change('pathsteps', steps)
            self._datacontroller.commit_change('path', result)

    def convex_hull(self):
        """ Returns all nodes defining the convex_hull or lying on its edge."""
        nodes = self._datacontroller.get_data('nodes')
        scale = self._datacontroller.get_data('scale')
        hull = tsputil.convex_hull_helper(nodes)
        if hull:
            result = construct_step(hull, 'Most Top Left Node', 'Clockwise', nodes, scale)
            self._datacontroller.commit_change('path', result)

    def convex_hull_model(self, _start='random', _direction='random'):
        """------------------------------------------------------------------------
           ------------------------ Convex Hull Model -----------------------------
           ------------------------------------------------------------------------
           A model for the simulation of human solving strategies for TSP, designed
           by MacGregor et al.
           Description comments in the code are citations from the original paper:
        """
        steps = [{'Tour': [], 'Tourlength': 0}]
        nodes = self._datacontroller.get_data('nodes')
        scale = self._datacontroller.get_data('scale')

        if nodes:
            # Step 1: Sketch the connections between adjacent boundary
            #        points of the convex hull.
            # hull is a list of ids, not nodes,the hull is always generated CW
            hull = tsputil.convex_hull_helper(nodes)
            # Step 2: Select a starting point and a direction (randomly).
            # start is an id not a node
            startinfo = get_direction_and_start(nodes, _start, _direction)
            start = startinfo[0]
            # if direction is ccw ,reverse hull
            if not startinfo[1] == 1:
                hull.reverse()

            steps.append(construct_step(hull, startinfo[2], startinfo[3], nodes, scale))

            # Step 3: If the starting point is on the boundary,
            # the starting node is the current node. """
            if start in hull:
                # The arc connecting the current node to the adjacent boundary
                # node in the direc- tion of travel is referred to as the
                # current arc.
                cn_index = hull.index(start)
                current_node = hull[cn_index]
                # get adjacent node
                an_index = (cn_index + 1) % (len(hull))
                adjacent_node = hull[an_index]
                # Proceed immediately to Step 4."""
            else:
                # If the starting point is not on the boundary, apply the
                # insertion rule to find the closest arc on the boundary. """
                closest_arc = find_closest_arc(start, hull, nodes)
                # Connect the starting point to the end node of the closest
                # arc which is in the direction of travel.
                # This node becomes the current node."""
                # insert startnode into hull
                hull.insert(hull.index(closest_arc[0]) + 1, start)
                steps.append(construct_step(hull, startinfo[2], startinfo[3], nodes, scale))
                # update current arc nodes
                current_node = start
                adjacent_node = hull[hull.index(closest_arc[1])]
            # Step 4: Apply the insertion criterion to identify which
            # unconnected interior point is closest to the current arc.
            # repeat step 4 and 5 until all nodes are included in the path
            while len(hull) <= len(nodes):
                while True:
                    current_arc = (current_node, adjacent_node)
                    # find closest node not in the hull
                    interior_node = find_closest_interior_node(current_arc, hull, nodes)
                    # Apply the insertion criterion to check whether the
                    # closest node is closer to any other arc.
                    is_closer = is_closer_to_other_arc(interior_node, current_arc, hull, nodes)
                    # If not, proceed to Step 5. If it is, move to the end node of
                    # the current arc. This becomes the current node. Repeat
                    # Step 4.
                    if not is_closer:
                        break
                    else:
                        current_node = current_arc[1]
                        an_index = (hull.index(current_node) + 1) % (len(hull))
                        adjacent_node = hull[an_index]
                # Step 5: Insert the closest node. The connection between the
                # current node and the newly inserted node becomes the current arc.
                # Retaining the current node, return to Step 4 and repeat Steps 4 and
                # 5 until a complete tour is obtained"""
                hull.insert(hull.index(current_node) + 1, interior_node)
                adjacent_node = interior_node
                steps.append(construct_step(hull, startinfo[2], startinfo[3], nodes, scale))

            self._datacontroller.commit_change('pathsteps', steps)
            self._datacontroller.commit_change('path', steps[-1])

    def nearest_neighbor(self):
        """ Constructs a tour by folowing the nearest neighbor heuristic"""
        steps = [{'Tour': [], 'Tourlength': 0}]
        tour = []
        original_nodes = self._datacontroller.get_data('nodes')
        nodes = copy.deepcopy(original_nodes)
        scale = self._datacontroller.get_data('scale')

        # Step 1: Get a tour start
        starts = [node for node in nodes if node.start]
        _start = 'Random from marked nodes'
        if not len(starts):
            starts = nodes
            _start = 'Random from all nodes'

        current = starts[randint(0, (len(starts) - 1))]
        while True:
            tour.append(current.nid)
            nodes.remove(current)
            steps.append(construct_step(tour, str(_start), 'random', original_nodes, scale))
            if not len(nodes):
                break
            current = nodes[tsputil.nearest_neighbor(nodes, current)[0]]
        tour.append(tour[0])
        steps.append(construct_step(tour, str(_start), 'random', original_nodes, scale))
        self._datacontroller.commit_change('pathsteps', steps)
        self._datacontroller.commit_change('path', steps[-1])


def is_closer_to_other_arc(interior_node, arc, hull, nodes):
    """ Returns true, if the given node forms a shorter path, when
        inserted into an other arc than the given one """
    closest_arc = find_closest_arc(interior_node, hull, nodes)
    return not ((closest_arc == arc) or (closest_arc[::-1] == arc))


def construct_step(tour, start, direction, nodes, scale):
    """ Constructs a step object from tour information"""
    return {'Tour': copy.deepcopy(tour),
            'Tourlength': tsputil.get_path_length(nodes, scale, tour),
            'Start': start,
            'Direction': direction}


def get_direction_and_start(nodes, _start, _direction):
    """ Returns a startnode and a direction. If multiple starts are possible
    a random one will be returned. If a direction is predefined it will
    be retained, otherwise the direction will be random ccw or cw."""
    starts = [node for node in nodes if node.start]
    if not len(starts):
        starts = nodes
        start_string = _start
    else:
        start_string = 'Random from marked nodes'
    start = starts[randint(0, (len(starts) - 1))].nid
    # directions: -1 = ccw, 1 = cw
    if not _direction is 'random':
        direction = _direction
    else:
        direction = randint(0, 1)
        direction_string = "Clockwise"
    if not direction == 1:
        direction_string = "Counter Clockwise"
        if _direction == 'random':
            direction_string += " (random)"
    return (start, direction, start_string, direction_string)


def find_closest_arc(point, _hull, nodes):
    """ Finds the arc to a point, so that when the point is included into
        that arc, the resulting tour is shorter than any other tour
        formed by inserting the point into an other arc"""
    hull = copy.deepcopy(_hull)
    lengths = [float("inf") for x in range(len(hull))]
    # insert the point into every existing arc and remember
    # the resulting tour length
    for i in range(1, len(hull)):
        hull.insert(i, point)
        lengths[i] = (tsputil.get_path_length(nodes, 100, hull))
        hull.pop(i)

    ci_index = lengths.index(min(lengths))
    an_index = (ci_index - 1) % len(hull)
    return (hull[an_index], hull[ci_index])


def find_closest_interior_node(arc, hull, nodes):
    """ Returns the node that forms the shortest hull, when inserted
        in the given arc of the given hull """
    lengths = [float("inf") for x in range(len(nodes))]
    for (j, node) in enumerate(nodes):
        if not node.nid in hull:
            i = hull.index(arc[1])
            hull.insert(i, node.nid)
            lengths[j] = (tsputil.get_path_length(nodes, 100, hull))
            hull.pop(i)
    return lengths.index(min(lengths))
