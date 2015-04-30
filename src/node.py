class Node:

    def __init__(self, id, x, y, color):
        self.id = id
        self.x = x
        self.y = y
        self.color = color

    def toString(self):
        xdelim = ""
        if(self.x < 10):
            xdelim = "  "
        ydelim = ""
        if(self.y < 10):
            ydelim = "  "

        return "X:" + xdelim + str(self.x) + " , Y:" + ydelim + str(self.y)
