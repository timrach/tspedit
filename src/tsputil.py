import math


colors = ["Black", "Red", "Green", "Blue", "Orange", "Cyan",
          "Magenta", "Yellow", "Gray", "White", "Brown",
          "Pink", "Purple", "Violet"]


def reindexNodes(nodes):
    for (index, node) in enumerate(nodes):
        node.id = index


def nothing():
    pass


def getPathLength(nodes, scale, path):
    """ Calculates the pathlength """
    result = 0
    for p in range(0, len(path) - 1):
        start = nodes[int(path[p])]
        end = nodes[int(path[p + 1])]
        result += distance(start, end, scale)
    return result


def distance(start, end, scale):
    """ Calculates the euclidean distance between two points"""
    return math.sqrt(math.pow((start.x - end.x) * scale, 2) +
                     math.pow((start.y - end.y) * scale, 2))


def nearestNeighbor(nodes, node):
    """ Finds the distance of the nearest neighbor """
    result = float("Inf")
    for n in nodes:
        if n is not node:
            result = min(result, distance(node, n, 1))
    return result


def convex_hull(points):
    """Computes the convex hull of a set of 2D points.

    Input: an iterable sequence of (x, y) pairs representing the points.
    Output: a list of vertices of the convex hull in counter-clockwise order,
      starting from the vertex with the lexicographically smallest coordinates.
    Implements Andrew's monotone chain algorithm. O(n log n) complexity.

    SRC: http://en.wikibooks.org/wiki/Algorithm_Implementation/Geometry
         /Convex_hull/Monotone_chain#Python

    NOTE:
    Slightly changed algorithm. Doesn't compute the minimal set,
    but includes nodes directly lying on an edge of the convex_hull.
    See 'CHANGED' comments in code.
    """

    # Sort the points lexicographically (tuples are compared lexicographically)
    # Remove duplicates to detect the case we have just one unique point.

    points = sorted(set(points))

    # Boring case: no points or a single point, possibly repeated multiple
    # times.
    if len(points) <= 1:
        return points

    # 2D cross product of OA and OB vectors, i.e. z-component of their 3D cross
    # product.
    # Returns a positive value, if OAB makes a counter-clockwise turn,
    # negative for clockwise turn, and zero if the points are collinear.
    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    # Build lower hull
    lower = []
    for p in points:
        # CHANGED: while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <=
        # 0:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)

    # Build upper hull
    upper = []
    for p in reversed(points):
        # CHANGED: while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <=
        # 0:
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)

    # Concatenation of the lower and upper hulls gives the convex hull.
    # Last point of each list is omitted because it is repeated at the
    # beginning of the other list.
    return lower[:-1] + upper[:-1]


class FilenameWrapper:

    """ A workaround for the creation of files without having an io wrapper """

    def __init__(self, filename):
        self.name = filename
