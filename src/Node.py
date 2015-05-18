"""
    Node.py
    See class description
"""


class Node(object):

    """ Represents a node in a 2D cell array
        at position x,y. The node has an id and a color
        represented by an integer value """

    def __init__(self, nid, x, y, color):
        self.nid = nid
        self.x_coord = x
        self.y_coord = y
        self.color = color
        self.start = False

    def to_string(self):
        """ Construct a string with the node informations """
        xdelim = ""
        ydelim = ""
        if self.x_coord < 10:
            xdelim = "  "
        if self.y_coord < 10:
            ydelim = "  "

        result = (str(self.nid) + "     X:" + xdelim + str(self.x_coord)
                  + "      Y:" + ydelim + str(self.y_coord))
        if self.start:
            result += "     Start"
        return result

    def get_coords(self):
        """ returns the node coordinates as a tuple"""
        return (self.x_coord, self.y_coord)
