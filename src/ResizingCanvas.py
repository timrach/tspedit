import tkinter as tk
import math


class ResizingCanvas(tk.Canvas):

    """ The Canvas Module. All drawable data is drawn here"""

    def __init__(self, parent, **kwargs):
        """ DATA """
        tk.Canvas.__init__(self, parent, **kwargs)
        self.parent = parent
        self.configure(highlightthickness=0)
        self.height = self.winfo_reqheight()
        self.width = self.winfo_reqwidth()
        self.selectedNode = None
        self.com = 1
        self.cog = 1
        self.hscale = 1.0
        self.wscale = 1.0
        self.fieldsize = 30
        self.padding = 5
        self.rows = math.floor(self.height / self.fieldsize)
        self.cols = math.floor(self.width / self.fieldsize)
        self.points = [None for i in range(0, self.rows * self.cols)]

        """ register the canvas area for click and hover events.
            If the user clicks on the canvas call the canvas_clicked method
            when the user hovers over the canvas, the position indicator label
            is updated to show the coordinates of the selected field """
        self.bind("<Button-1>", self.canvas_clicked)
        self.bind("<Motion>", self.onMotion)
        self.bind("<Configure>", self.on_resize)
        self.drawGrid()

    def on_resize(self, event):
        """ Gets called whenever the window is resized.
        Handles correct item scaling and updates data fields"""
        # determine the ratio of old width/height to new width/height
        wscale = float(event.width) / self.width
        hscale = float(event.height) / self.height
        self.width = event.width
        self.height = event.height
        # resize the canvas
        self.config(width=self.width, height=self.height)
        # rescale all the objects tagged with the "all" tag
        self.hscale *= hscale
        self.wscale *= wscale
        self.scale("all", 0, 0, wscale, hscale)

    def drawGrid(self):
        """Draws the grid for the node positions on the canvas
        as gray lines."""
        # draw vertical lines
        for x in range(0, self.cols + 1):
            xcoord = x * self.fieldsize
            self.create_line(
                xcoord, 0, xcoord, self.rows * self.fieldsize,
                fill="#ddd", tags="grid")
        # draw horizontal lines
        for y in range(0, self.rows + 1):
            ycoord = y * self.fieldsize
            self.create_line(
                0, ycoord, self.cols * self.fieldsize, ycoord,
                fill="#ddd", tags="grid")
        # draw 0,0 indicator
        # vertical arrow for y axis
        self.create_line(
            0, 0, 0, self.fieldsize * 2, arrow=tk.LAST, fill="green")
        # horizontal arrow for x axis
        self.create_line(
            0, 0, self.fieldsize * 2, 0, arrow=tk.LAST, fill="red")
        self.move("all", 5, 5)

    def onMotion(self, event):
        """ Gets called whenever the mouse is moved on the canvas.
        Calls the update routine for the position indicator label"""
        # get relative field coordinates
        q = math.floor(
            (event.x - self.padding) / (self.fieldsize * self.wscale))
        r = math.floor(
            (event.y - self.padding) / (self.fieldsize * self.hscale))
        self.parent.updatePositionLabel(q, r)

    def canvas_clicked(self, event):
        """Callback for the click-event on the canvas area.
        Draws a point at the clicked position if the position is empty.
        If the click was on an existing point, the point is selected
        and the event passed to the other modules."""
        # get relative field coordinates
        q = math.floor(
            (event.x - self.padding) / (self.fieldsize * self.wscale))
        r = math.floor(
            (event.y - self.padding) / (self.fieldsize * self.hscale))
        # only do something if the clicked position is within bounds
        if(q < self.cols and r < self.rows and q >= 0 and r >= 0):
            point = self.points[r * self.cols + q]
            # if there is no node already add one
            if point is None:
                self.parent.parent.addNode(q, r)
            # else delete it if there is one
            else:
                pass
                # self.parent.parent.deleteNode(q, r)

    def clear(self):
        """ Clear all drawn objects and redraw the grid"""
        self.delete(tk.ALL)
        self.drawGrid()
        self.scale("all", 0, 0, self.wscale, self.hscale)

    def addNode(self, x, y, color):
        """ draws a point on the specified position on the canvas and adds
        the data to the nodes and points arrays"""
        index = y * self.cols + x
        point = self.circle(x, y, 0.5, fill=color, tags="node",
                            activeoutline="Orange", activewidth=3)
        # register point for the click event
        self.tag_bind(point, "<Button-1>", lambda e: self.nodeSelected(index))
        self.points[index] = point
        self.drawCenterOfMass()
        self.drawGeometricalCenter()

    def indToCoord(self, index):
        """ Converts an index to X,Y coordinates """
        y = math.floor(index / self.cols)
        x = index - y * self.cols
        return (x, y)

    def nodeSelected(self, index):
        """ Selects the point at the index position.
        If the point is already selected, it is deselected.
        In both cases the event is passed to the other modules"""
        self.delete("selector")
        if self.selectedNode == index:
            self.selectedNode = None
            self.parent.nodeDeselected()
        else:
            self.selectedNode = index
            self.parent.nodeSelected(self.indToCoord(index))
            self.drawSelectionIndicator(index)

    def drawSelectionIndicator(self, index):
        """ Draws a red ring around the selected point """
        coords = self.indToCoord(index)
        self.circle(coords[0], coords[1], 0.5, outline="#f44", width=3,
                    fill="", tags="selector")

    def drawCenterOfMass(self):
        """ Draws a small blue ring at the center of mass position """
        self.delete("com")
        result = [0, 0]
        nodes = self.parent.getNodes()
        for n in nodes:
            result = [result[0] + n.x, result[1] + n.y]
        x = result[0] / len(nodes)
        y = result[1] / len(nodes)
        self.circle(
            x, y, 0.2, outline="#44f", width=3, fill="", tags="com")
        self.tag_lower("com")

    def drawGeometricalCenter(self):
        """ Draws a small blue ring at the geometrical center """
        self.delete("cog")
        maxima = [0, 0]
        minima = [float("Inf"), float("Inf")]
        nodes = self.parent.getNodes()
        for n in nodes:
            maxima = [max(n.x, maxima[0]), max(n.y, maxima[1])]
            minima = [min(n.x, minima[0]), min(n.y, minima[1])]
        x = (maxima[0] + minima[0]) / 2
        y = (maxima[1] + minima[1]) / 2
        self.circle(
            x, y, 0.2, outline="#f44", width=3, fill="", tags="cog")
        self.tag_lower("cog")

    def line(self, x1, y1, x2, y2):
        """ Draws a line from cell x1,y1 to cell x2,y2 """
        line = self.create_line(
            (x1 * self.fieldsize + (self.fieldsize / 2)) * self.wscale,
            (y1 * self.fieldsize + (self.fieldsize / 2)) *
            self.hscale,
            (x2 * self.fieldsize + (self.fieldsize / 2)) *
            self.wscale,
            (y2 * self.fieldsize + (self.fieldsize / 2)) *
            self.hscale,
            fill="#444", tags="path_line",
            activefill="black", width=3)
        self.move(
            line, self.padding * self.wscale, self.padding * self.hscale)

    def circle(self, x, y, _radius, **options):
        """ Draws a circle at the center of cell x,y with radius _radius """
        radius = _radius * self.fieldsize * 0.7071
        # math.sin(math.radians(45) = 0.7071
        x1 = ((x + 0.5) * self.fieldsize - radius) * self.wscale
        y1 = ((y + 0.5) * self.fieldsize - radius) * self.hscale
        x2 = ((x + 0.5) * self.fieldsize + radius) * self.wscale
        y2 = ((y + 0.5) * self.fieldsize + radius) * self.hscale
        circ = self.create_oval(x1, y1, x2, y2, **options)
        self.move(
            circ, self.padding * self.wscale, self.padding * self.hscale)
        return circ

    def deleteNode(self, x, y):
        """ Delete the point at cell x,y"""
        ind = y * self.cols + x
        if ind == self.selectedNode:
            self.nodeSelected(ind)
        self.delete(self.points[ind])
        self.points[y * self.cols + x] = None

    def setCom(self, value):
        "Dis-/Enables the drawing of the center of mass"
        self.com = value
        if self.com:
            self.drawCenterOfMass()
        else:
            self.delete("com")

    def setCog(self, value):
        "Dis-/Enables the drawing of the geometrical center"
        self.cog = value
        if self.cog:
            self.drawGeometricalCenter()
        else:
            self.delete("cog")
