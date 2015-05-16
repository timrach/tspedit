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

        result = (str(self.id) + "     X:" + xdelim + str(self.x)
                  + "      Y:" + ydelim + str(self.y))
        if self.start:
            result += "     Start"
        return result
