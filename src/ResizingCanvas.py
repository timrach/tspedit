import tkinter as tk
import math


class ResizingCanvas(tk.Canvas):

    def __init__(self, parent, **kwargs):
        tk.Canvas.__init__(self, parent, **kwargs)
        self.parent = parent
        self.configure(highlightthickness=0)
        self.height = self.winfo_reqheight()
        self.width = self.winfo_reqwidth()
        self.hscale = 1.0
        self.wscale = 1.0
        self.fieldsize = 30
        self.rows = math.floor(self.height / self.fieldsize)
        self.cols = math.floor(self.width / self.fieldsize)
        self.points = [None for i in range(0, self.rows * self.cols)]

        # register the canvas area for click and hover events.
        # If the user clicks on the canvas call the canvas_clicked method
        # when the user hovers over the canvas, the position indicator label
        # is updated to show the coordinates of the selected field
        self.bind("<Button-1>", self.canvas_clicked)
        self.bind("<Motion>", self.onMotion)
        self.bind("<Configure>", self.on_resize)

        self.drawGrid()

    def on_resize(self, event):
        # determine the ratio of old width/height to new width/height
        wscale = float(event.width) / self.width
        hscale = float(event.height) / self.height
        #bscale = max(wscale,hscale)
        self.width = event.width
        self.height = event.height
        # resize the canvas
        self.config(width=self.width, height=self.height)
        # rescale all the objects tagged with the "all" tag
        self.hscale *= hscale
        self.wscale *= wscale
        self.scale("all", 0, 0, wscale, hscale)
        # self.drawGrid()

    def drawGrid(self):
        """Draws the grid for the node positions on the canvas"""
        # draw vertical lines
        for x in range(0, self.cols + 1):
            xcoord = x * self.fieldsize
            self.create_line(
                xcoord, 0, xcoord, self.rows * self.fieldsize, fill="#ddd")
        # draw horizontal lines
        for y in range(0, self.rows + 1):
            ycoord = y * self.fieldsize
            self.create_line(
                0, ycoord, self.cols * self.fieldsize, ycoord, fill="#ddd")

    def onMotion(self, event):
        # get relative field coordinates
        q = math.floor(event.x / (self.fieldsize * self.wscale))
        r = math.floor(event.y / (self.fieldsize * self.hscale))
        self.parent.updatePositionLabel(q, r)

    def canvas_clicked(self, event):
        """Callback for the click-event on the canvas area
        Draws a point at the clicked position"""
        # get relative field coordinates
        q = math.floor(event.x / (self.fieldsize * self.wscale))
        r = math.floor(event.y / (self.fieldsize * self.hscale))
        # only do something if the clicked position is within bounds
        if(q < self.cols and r < self.rows and q >= 0 and r >= 0):
            point = self.points[r * self.cols + q]
            # if there is no node already add one
            if(point == None):
                self.parent.parent.addNode(q, r)
            # else delete it if there is one
            else:
                self.parent.parent.deleteNode(q, r)

    def clear(self):
        self.delete(tk.ALL)
        self.drawGrid()
        self.scale("all", 0, 0, self.wscale, self.hscale)

    def addNode(self, x, y, color):
        """ draws a point on the specified position on the canvas and adds
        the data to the nodes and points arrays and the nodes listbox"""
        index = y * self.cols + x
        self.points[index] = self.create_oval(
            (x * self.fieldsize + 2) * self.wscale,
            (y * self.fieldsize + 2) * self.hscale,
            ((x + 1) * self.fieldsize - 2) * self.wscale,
            ((y + 1) * self.fieldsize - 2) * self.hscale,
            fill=color)

    def deleteNode(self, x, y):
        self.delete(self.points[y * self.cols + x])
        self.points[y * self.cols + x] = None
