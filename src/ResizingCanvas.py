try:
    # for Python2
    import Tkinter as tk
except ImportError:
    # for Python3
    import tkinter as tk
from Node import *
import tsputil
import math
import copy


class ResizingCanvas(tk.Canvas):

    """ The Canvas Module. All drawable data is drawn here"""

    def __init__(self, parent, datacontroller, **kwargs):
        tk.Canvas.__init__(self, parent, **kwargs)

        self.configure(highlightthickness=0)

        """ Public vars """
        self.keywords = ['nodes', 'startnode', 'path', 'selectedNode']

        """ Private vars """
        self._parent = parent
        self._datacontroller = datacontroller
        self._height = self.winfo_reqheight()
        self.width = self.winfo_reqwidth()
        self.selectedNode = None
        self.com = 1
        self.cog = 1
        self.hscale = 1.0
        self.wscale = 1.0
        self.fieldsize = 30
        self.padding = 5
        self.rows = math.floor(self._height / self.fieldsize)
        self.cols = math.floor(self.width / self.fieldsize)
        self._points = [None for i in range(0, int(self.rows * self.cols))]
        self._nodes = copy.copy(self._datacontroller.getData('nodes'))

        """ register the canvas area for click and hover events.
            If the user clicks on the canvas call the canvas_clicked method
            when the user hovers over the canvas, the position indicator label
            is updated to show the coordinates of the selected field """
        self.bind("<Button-1>", self.canvas_clicked)
        self.bind("<Motion>", self.onMotion)
        self.bind("<Configure>", self.on_resize)
        self.drawGrid()

        self._datacontroller.registerData('selectedNode', ())
        self._datacontroller.registerData('mouseGridPosition', ())
        self._datacontroller.registerObserver(self, self.keywords)

    def on_resize(self, event):
        """ Gets called whenever the window is resized.
        Handles correct item scaling and updates data fields"""
        # determine the ratio of old width/height to new width/height
        wscale = float(event.width) / self.width
        hscale = float(event.height) / self._height
        self.width = event.width
        self._height = event.height
        # resize the canvas
        self.config(width=self.width, height=self._height)
        # rescale all the objects tagged with the "all" tag
        self.hscale *= hscale
        self.wscale *= wscale
        self.scale("all", 0, 0, wscale, hscale)

    def drawGrid(self):
        """Draws the grid for the node positions on the canvas
        as gray lines."""
        # draw vertical lines
        for x in range(0, int(self.cols + 1)):
            xcoord = x * self.fieldsize
            self.create_line(
                xcoord, 0, xcoord, self.rows * self.fieldsize,
                fill="#ddd", tags="grid")
        # draw horizontal lines
        for y in range(0, int(self.rows + 1)):
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
        self._datacontroller.commitChange('mouseGridPosition', (q, r))

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
            point = self._points[int(r * self.cols + q)]
            # if there is no node yet, add one
            if point is None:
                new_nodes = self._datacontroller.getData('nodes')
                color = self._datacontroller.getData('nodecolor')
                new_nodes.append(Node(len(new_nodes), q, r, color))
                self._datacontroller.commitChange('nodes', new_nodes)

    def addNode(self, node):
        """ draws a point on the specified position on the canvas and adds
        the data to the nodes and points arrays"""
        index = int(node.y * self.cols + node.x)
        point = self.circle(node.x, node.y, 0.5, fill=node.color, tags="node",
                            activeoutline=tsputil.resColors[0], activewidth=3)
        # register point for the click event
        self.tag_bind(point, "<Button-1>", lambda e: self.nodeSelected(index))
        self._points[index] = point

    def indToCoord(self, index):
        """ Converts an index to X,Y coordinates """
        y = math.floor(index / self.cols)
        x = index - y * self.cols
        return (x, y)

    def nodeSelected(self, index):
        """ Selects the point at the index position.
        If the point is already selected, it is deselected.
        In both cases the event is passed to the other modules"""
        if self.selectedNode == index:
            self.selectedNode = None
            self._datacontroller.commitChange('selectedNode', None)
        else:
            # find node in nodes array
            (x, y) = self.indToCoord(index)
            for node in self._nodes:
                if node.x == x and node.y == y:
                    self._datacontroller.commitChange('selectedNode', node)
                    break

    def drawSelectionIndicator(self, index):
        """ Draws a red ring around the selected point """
        coords = self.indToCoord(index)
        self.circle(coords[0], coords[1], 0.5, outline=tsputil.resColors[1], 
                    width=3, fill="", tags="selector")

    def drawStartIndicator(self, index):
        """ Draws a blue ring around the selected point """
        coords = self.indToCoord(index)
        self.circle(coords[0], coords[1], 0.6, outline=tsputil.resColors[2], 
                    width=5, fill="", tags="startnode")

    def drawCenterOfMass(self):
        """ Draws a small blue ring at the center of mass position """
        self.delete("com")
        if len(self._nodes):
            result = [0, 0]
            for n in self._nodes:
                result = [result[0] + n.x, result[1] + n.y]
            x = result[0] / len(self._nodes)
            y = result[1] / len(self._nodes)
            self.circle(
                x, y, 0.2, outline="#44f", width=3, fill="", tags="com")
            self.tag_lower("com")

    def drawGeometricalCenter(self):
        """ Draws a small blue ring at the geometrical center """
        self.delete("cog")
        if len(self._nodes):
            maxima = [0, 0]
            minima = [float("Inf"), float("Inf")]
            for n in self._nodes:
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

    def deleteNode(self, node):
        """ Delete the point at cell x,y"""
        ind = int(node.y * self.cols + node.x)
        if ind == self.selectedNode:
            self.nodeSelected(ind)
        self.delete(self._points[ind])
        self._points[ind] = None

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

    def dataUpdate(self, key, data):
        if key is 'nodes':
            diffadd = list(set(data)-set(self._nodes))
            diffsub = list(set(self._nodes) - set(data))
            for node in diffadd:
                self.addNode(node)
            for node in diffsub:
                self.deleteNode(node)
            self._nodes = copy.copy(data)
            self.drawCenterOfMass()
            self.drawGeometricalCenter()
        elif key is 'selectedNode':
            # clear old selection
            self.delete("selector")
            self.selectedNode = None
            if data:
                # set new selection
                index = int(data.y * self.cols + data.x)
                self.selectedNode = index
                self.drawSelectionIndicator(index)
        elif key is 'path':
            self.delete("path_line")
            for c in range(0, len(data) - 1):
                start = self._nodes[int(data[c])]
                end = self._nodes[int(data[c + 1])]
                self.line(start.x, start.y, end.x, end.y)
            self.tag_raise("node")
        elif key is 'startnode':
            if data:
                for node in data:
                    if node.start:
                        index = int(node.y * self.cols + node.x)
                        self.drawStartIndicator(index)

