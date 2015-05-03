#!/usr/local/bin/python3

import tkinter as tk
from CanvasFrame import *
from SidebarFrame import *
from node import *
import tsputil
import tspio


class MainApplication(tk.Frame):

    """ The MainApplication Module holds references to all frames drawn
    in the main window. It holds all atomic data and acts as an
    interface for the communication between modules. 
    That way all events are initially passed to this module which
    distributes the data to the other modules"""

    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)

        """ DATA """
        self.scale = 100  # factor coordinates are scaled with
        self.selectedColor = 0  # active colorid
        self.nodes = []  # internal node representation
        self.solution = []  # container for the drawn solution

        """ GUI """
        self.configure(padx=10, pady=10)
        self.canvas = CanvasFrame(self, relief=tk.SUNKEN)
        self.sidebar = SidebarFrame(self, relief=tk.SUNKEN)

        self.sidebar.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        """ MENU BAR """
        menubar = tk.Menu(parent)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Import .tsp", command=self.importTSP,
                             accelerator="Ctrl+I")
        self.bind_all("<Control-i>", self.importTSP)
        filemenu.add_command(label="Export .tsp", command=self.exportTSP,
                             accelerator="Ctrl+E")
        self.bind_all("<Control-e>", self.exportTSP)
        filemenu.add_separator()
        filemenu.add_command(label="Export TIKZ", command=self.exportTIKZ,
                             accelerator="Ctrl+T")
        self.bind_all("<Control-t>", self.exportTIKZ)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=parent.quit)

        tspmenu = tk.Menu(menubar, tearoff=0)
        tspmenu.add_command(label="Solve tsp", command=self.solveTSP,
                            accelerator="Ctrl+P")
        self.bind_all("<Control-p>", self.solveTSP)
        tspmenu.add_command(label="Clear path", command=self.clearPath,
                            accelerator="Ctrl+Shift+P")
        self.bind_all("<Control-Shift-p>", self.clearPath)

        editormenu = tk.Menu(menubar, tearoff=0)
        editormenu.add_command(label="Clear Data", command=self.clear,
                               accelerator="Ctrl+C")
        self.bind_all("<Control-c>", self.clear)

        menubar.add_cascade(label="File", menu=filemenu)
        menubar.add_cascade(label="TSP", menu=tspmenu)
        menubar.add_cascade(label="Editor", menu=editormenu)
        parent.config(menu=menubar)

    """ CLASS METHODS """

    def clear(self, event=None):
        """ Clears all problem data from the program and resets the UI """
        self.nodes = []
        self.canvas.clear()
        self.sidebar.clear()

    def solveTSP(self, event=None):
        """ Call the util module to solve the currently drawn
        problem and pass self.putSolution as the callback.
        As the util module uses an external program which works
        on .tsp files, the drawn problem is exported to a temporary file"""
        dummy = tsputil.FilenameWrapper("tmpfile.tsp")
        tspio.exportTSP(
            self.nodes, self.scale,
            lambda f: tsputil.solveTSP(f, self.putSolution), dummy)

    def clearPath(self, event=None):
        """ Erase all solution data """
        self.solution = []
        self.sidebar.removePathInfo()
        self.canvas.clearPath()

    def putSolution(self, solution):
        """ Update the solution data and pass it to the sidebar and canvas """
        solution.append(solution[0])  # append startnode to make tour circular
        self.solution = solution
        self.canvas.putSolution(self.nodes, solution)
        self.sidebar.addPathInfo(self.nodes, solution)

    def exportTSP(self, event=None):
        """ Export the loaded problem via the IO module in .tsp format"""
        tspio.exportTSP(
            self.nodes, self.scale, lambda f: self.sidebar.setFilename(f))

    def exportTIKZ(self, event=None):
        """ Export the loaded problem via the IO module as a tikz graphic
        in .tex format"""
        tspio.exportTIKZ(self.nodes, self.scale)

    def importTSP(self, event=None):
        """ Load data from a .tsp file via the IO module """
        tspio.importTSP(self.putLoadedData)

    def nodeSelected(self, coords):
        """ Gets called when the user selects node in the canvas.
        Passes the node coordinates to the sidebar module"""
        self.sidebar.nodeSelected(coords)

    def nodeDeselected(self):
        """ Gets called when the user deselects node in the canvas.
        Calls the corresponding method in the sidebar module"""
        self.sidebar.nodeDeselected()

    def putLoadedData(self, filename, nodes, groups):
        """ Fills the internal data structures with the loaded data.
            !!! No error handling or validity checks !!!"""
        self.clear()
        self.sidebar.setFilename(filename)
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

    def addNode(self, xc, yc):
        """ Add a node to the nodes array
        and pass it to the canvas and sidebar"""
        # update data
        new_node = Node(len(self.nodes), xc, yc, self.selectedColor)
        self.nodes.append(new_node)
        # pass data to frames
        self.canvas.addNode(xc, yc, tsputil.colors[self.selectedColor])
        self.sidebar.addNode(new_node)

    def deleteNode(self, xc, yc):
        """ removes a node form the data structures and the canvas.
        As the nodes are stored as a list, the ids of the nodes after
        the delted one have to be updated """
        self.canvas.deleteNode(xc, yc)
        # find nodeobject in nodes list
        found = False
        target = None
        for n in self.nodes:
            if not found:
                if n.x == xc and n.y == yc:
                    target = n
                    found = True
            else:
                # update id
                n.id = n.id - 1
        self.nodes.remove(target)
        self.sidebar.deleteNode(target.id)

    def getNodes(self):
        return self.nodes


if __name__ == '__main__':
    root = tk.Tk()
    MainApplication(root).pack(fill=tk.BOTH, expand=True)
    root.mainloop()
