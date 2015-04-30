#!/usr/local/bin/python3

from node import *
from tspio import *
from tkinter import *
from tsputil import *
from tkinter.filedialog import asksaveasfile, askopenfile
import math


cols = 27
rows = 22
linewidth = 3
linewidth2 = linewidth * 2


class MainApplication:

    def __init__(self, master):
        """APPLICATION SETTINGS"""
        self.scale = 100  # factor coordinates are scaled with
        self.selectedColor = 0  # active colorid
        self.canvas_width = 810  # Canvaswidth
        self.canvas_height = 660  # Canvasheight
        # Fieldwidth
        self.offsetx = (self.canvas_width - linewidth) / cols
        # Fieldheight
        self.offsety = (self.canvas_height - linewidth) / rows
        
        # oval objects on the canvas
        self.points = [None for i in range(cols * rows)]
        self.nodes = []  # internal node representation

        """GUI SETUP"""
        # CANVAS
        self.canvas = Canvas(master,
                             width=self.canvas_width,
                             height=self.canvas_height)
        # draw the grid on the canvas
        self.drawGrid()
        # register the canvas area for click and hover events.
        # If the user clicks on the canvas call the canvas_clicked method
        # when the user hovers over the canvas, the position indicator label
        # is updated to show the coordinates of the selected field
        self.canvas.bind("<Button-1>", self.canvas_clicked)
        self.canvas.bind("<Motion>", self.updatePositionLabel)

        # POSITION LABEL
        self.position_label = Label(
            master, text="Position:( X:0 , Y:0 )", anchor=W)

        # EXPORT TSP BUTTON
        export_tsp_button = Button(
            master, text="Export .tsp File",
            command=lambda: exportTSP(self.nodes, self.scale))

        # IMPORT TSP BUTTON
        import_tsp_button = Button(
            master, text="Import .tsp File", command=self.importTSP)

        # EXPORT TIKZ BUTTON
        export_tikz_button = Button(
            master, text="Export tikz",
            command=lambda: exportTIKZ(self.nodes, self.scale))

        # CLEAR BUTTON
        clear_button = Button(master, text="Clear", command=self.clear)

        # COLOR LIST LABEL
        color_list_label = Label(master, text="Colors:", anchor=W)

        # COLOR LISTBOX
        self.color_listBox = Listbox(master, selectmode=SINGLE)
        # Fill color listbox with colors from the colors array
        for (i, c) in enumerate(colors):
            self.color_listBox.insert(i, c)
        # register color listbox for the selection even
        # if a color is selected, the global color variable will be
        # switched by the switchColor method
        self.color_listBox.bind('<<ListboxSelect>>', self.switchColor)

        # NODE LIST LABEL
        node_list_label = Label(master, text="Point Coordinates:")
        # NODE LIST BOX
        self.node_listBox = Listbox(master)

        """ GUI POSITIONING """
        # RIGHT COLUMN
        self.canvas.grid(column=1, rowspan=20, sticky=N + S)

        # LEFT COLUMN
        # set 10px padding to all rows in the column
        master.columnconfigure(0, pad=10)
        color_list_label.grid(column=0, row=1)
        self.color_listBox.grid(column=0, row=2, rowspan=5)
        self.color_listBox.selection_set(first=0)

        node_list_label.grid(column=0, row=8)
        self.node_listBox.grid(column=0, row=9, rowspan=5)

        self.position_label.grid(column=1, row=21, sticky=E + W)
        clear_button.grid(column=0, row=16, sticky=E + W)
        import_tsp_button.grid(column=0, row=17, sticky=E + W)
        export_tsp_button.grid(column=0, row=18, sticky=E + W)
        export_tikz_button.grid(column=0, row=19, sticky=E + W)

    """ CLASS METHODS """

    def clear(self):
        """ Clears all problem data from the program and resets the UI """
        self.nodes = []  # reset nodes array
        self.points = [None for i in range(cols * rows)]  # reset points array
        # delete all objects on the canvas, includes the grid -> we need to
        # redraw it afterwards
        self.canvas.delete("all")
        self.drawGrid()  # redraw the grid
        self.node_listBox.delete(0, END)  # delete all entries

    def importTSP(self):
        """ Parses a file and feeds the data to the program.
            Before the new data is loaded, all old program data
            are deleted. 
            !!! The file is not checked for validity and no
            error handling is done !!! """
        # show a open-file-dialog
        filename = askopenfile()
        # if the user selected a file, delete old data,parse the file and
        # load the new data. If the user canceled the selection, do nothing.
        if filename:
            self.clear()
            nodes, groups = parseTSPFile(filename.name)
            self.putLoadedData(nodes, groups)

    def putLoadedData(self, nodes, groups):
        """ Fills the internal data structures with the loaded data.
            !!! No error handling or validity checks !!!"""
        # If the nodes are not grouped, draw them in the currently
        # selected color
        if groups == []:
            for node in nodes:
                # node[0] holds the x-coordinate, node[1] holds the
                # y-coordinate
                self.addNode(
                    int(node[0] / self.scale), int(node[1] / self.scale))
        # if the nodes are grouped, draw nodes from the same group in the same
        # color
        else:
            color_old = self.selectedColor  # remember selected color
            # iterate over groups
            for (i, g) in enumerate(groups):
                # iterate over node ids in the group
                for e in g:
                    # set color
                    self.selectedColor = i
                    # get node coordinates
                    node = nodes[e - 1]
                    # draw the node
                    self.addNode(
                        int(node[0] / self.scale), int(node[1] / self.scale))
            self.selectedColor = color_old

    def switchColor(self, event):
        """ changes the colorvariable according to the selected item in the
        color listbox"""
        self.selectedColor = self.color_listBox.curselection()[0]

    def updatePositionLabel(self, event):
        """ update the position indicator label to show the selected
        field on the canvas"""
        # get relative field coordinates
        xc = math.floor(event.x / self.offsetx)
        yc = math.floor(event.y / self.offsety)
        # update label
        self.position_label.config(
            text=("Position:( X:" + str(xc) + " , " + "Y:" + str(yc)) + ")")

    def drawGrid(self):
        """Draws the grid for the node positions on the canvas"""
        # draw vertical lines
        for x in range(0, cols + 1):
            xcoord = x * self.offsetx + linewidth
            self.canvas.create_line(xcoord, 0,
                                    xcoord, self.canvas_height,
                                    fill="#ddd")
        # draw horizontal lines
        for y in range(0, rows + 1):
            ycoord = y * self.offsety + linewidth
            self.canvas.create_line(0, ycoord,
                                    self.canvas_width, ycoord,
                                    fill="#ddd")

    def canvas_clicked(self, event):
        """Callback for the click-event on the canvas area
        Draws a point at the clicked position"""
        # get relative field coordinates
        xc = math.floor(event.x / self.offsetx)
        yc = math.floor(event.y / self.offsety)
        # only do something if the clicked position is within bounds
        if(xc < cols and yc < rows and xc >= 0 and yc >= 0):
            point = self.points[yc * cols + xc]
            # if there is no node already add one
            if(point == None):
                self.addNode(xc, yc)
            # else delete it if there is one
            else:
                self.deleteNode(xc, yc, point)

    def addNode(self, xc, yc):
        """ draws a point on the specified position on the canvas and adds
        the data to the nodes and points arrays and the nodes listbox"""
        index = yc * cols + xc
        self.points[index] = self.canvas.create_oval(
            xc * self.offsetx + linewidth2,
            yc * self.offsety + linewidth2,
            (xc + 1) * self.offsetx,
            (yc + 1) * self.offsety,
            fill=colors[self.selectedColor])
        new_node = Node(len(self.nodes), xc, yc, self.selectedColor)
        self.nodes.append(new_node)
        self.node_listBox.insert(new_node.id, new_node.toString())

    def deleteNode(self, xc, yc, point):
        """ removes a node form the data structures and the canvas.
        As the nodes are stored as a list, the ids of the nodes after 
        the delted one have to be updated """
        self.canvas.delete(point)
        self.points[yc * cols + xc] = None
        # find nodeobject in nodes list
        found = False
        target = None
        for n in self.nodes:
            if not found:
                if n.x == xc and n.y == yc:
                    target = n
                    self.node_listBox.delete(n.id)
                    found = True
            else:
                # update id
                n.id = n.id - 1
        self.nodes.remove(target)


if __name__ == '__main__':
    root = Tk()
    app = MainApplication(root)
    root.mainloop()
