class Node:

    """ Represents a node in a 2D cell array
        at position x,y. The node has an id and a color
        represented by an integer value """

    def __init__(self, id, x, y, color):
        self.id = id
        self.x = x
        self.y = y
        self.color = color
        self.start = False

    def toString(self):
        """ Construct a string with the node informations """
        xdelim = ""
        if(self.x < 10):
            xdelim = "  "
        ydelim = ""
        if(self.y < 10):
            ydelim = "  "

        return (str(self.id) + "\t X:" + xdelim + str(self.x)
                + " \t Y:" + ydelim + str(self.y))
