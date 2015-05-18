"""
    tsputil.py
    Includes everything that doesn't fit in other modules and/or is
    used by more than one module"""
import math

COLORS = ["Black", "Orange", "Cyan", "Magenta", "Yellow", "Blue",
          "White", "Brown", "Pink", "Gray", "Violet"]

RESCOLORS = ["Red", "Green", "Purple"]


def reindex_nodes(nodes):
    """ Assigns node ids to a list of nodes according to their
        position in the list"""
    for (index, node) in enumerate(nodes):
        node.nid = index


def nothing():
    """Does nothing"""
    pass


def find_node_by_coords(coords, nodes):
    """returns the first node, that has the given coordinates"""
    (x_value, y_value) = coords
    node = [node for node in nodes if ((node.x_coord == x_value) and
                                       (node.y_coord == y_value))]
    if len(node):
        return node[0]
    else:
        return None


def get_path_length(nodes, scale, path):
    """ Calculates the pathlength """
    result = 0
    for point in range(0, len(path) - 1):
        start = nodes[int(path[point])]
        end = nodes[int(path[point + 1])]
        result += distance(start, end, scale)
    return result


def distance(start, end, scale):
    """ Calculates the euclidean distance between two nodes"""
    return math.sqrt(math.pow((start.x_coord - end.x_coord) * scale, 2) +
                     math.pow((start.y_coord - end.y_coord) * scale, 2))


def nearest_neighbor(nodes, origin):
    """ Finds the distance of the nearest neighbor """
    distances = [distance(origin, node, 100) for node in nodes]
    if origin in nodes:
        distances[nodes.index(origin)] = float("Inf")
    result = min(distances)
    return (distances.index(result), result)


def convex_hull_helper(nodes):
    """ calls the convex hull function from the tsputil module and
        constructs the tour with the corresponding node objects"""
    if len(nodes):
        # convert nodes into points (x,y)
        points = [(node.x_coord, node.y_coord) for node in nodes]
        # get convex hull as list of ids
        result = [find_node_by_coords(point, nodes).nid for
                  point in convex_hull(points)]
        result.append(result[0])
        return result
    else:
        return None


def convex_hull(points):
    """Computes the convex hull of a set of 2D points.

    Input: an iterable sequence of (x, y) pairs representing the points.
    Output: a list of vertices of the convex hull in counter-clockwise order,
      starting from the vertex with the lexicographically smallest coordinates.
    Implements Andrew's monotone chain algorithm. O(n log n) complexity.

    SRC: http://en.wikibooks.org/wiki/Algorithm_Implementation/Geometry
         /Convex_hull/Monotone_chain#Python

    NOTE:
    Can be changed to include nodes directly lying on an edge of the
    convex hull. See 'CHANGE' comments in code.
    """

    # Sort the points lexicographically (tuples are compared lexicographically)
    # Remove duplicates to detect the case we have just one unique point.

    points = sorted(set(points))

    # Boring case: no points or a single point, possibly repeated multiple
    # times.
    if len(points) <= 1:
        return points

    def cross(point_o, point_a, point_b):
        """ 2D cross product of OA and OB vectors, i.e. z-component of their
        3D cross product.
        Returns a positive value, if OAB makes a counter-clockwise turn,
        negative for clockwise turn, and zero if the points are collinear."""
        return ((point_a[0] - point_o[0]) * (point_b[1] - point_o[1]) -
                (point_a[1] - point_o[1]) * (point_b[0] - point_o[0]))

    # Build lower hull
    lower = []
    for point in points:
        # CHANGE:
        # To include nodes on the edges:
        # while len(lower) >= 2 and cross(lower[-2], lower[-1], p) < 0:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], point) <= 0:
            lower.pop()
        lower.append(point)

    # Build upper hull
    upper = []
    for point in reversed(points):
        # CHANGE:
        # To include nodes on the edges:
        # while len(upper) >= 2 and cross(upper[-2], upper[-1], p) < 0:
        while len(upper) >= 2 and cross(upper[-2], upper[-1], point) <= 0:
            upper.pop()
        upper.append(point)

    # Concatenation of the lower and upper hulls gives the convex hull.
    # Last point of each list is omitted because it is repeated at the
    # beginning of the other list.
    return lower[:-1] + upper[:-1]


class FilenameWrapper(object):

    """ A workaround for the creation of files without having an io wrapper """

    def __init__(self, filename):
        self.name = filename

    def get_name(self):
        """returns the name"""
        return self.name

    def to_string(self):
        """ returns the classes string representation"""
        return "FilenameWrapper(" + self.name + ")"
