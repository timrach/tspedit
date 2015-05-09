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
        self._parent = parent
        self._data = {}
        self._observer = {}

        self._setupData()
        self._setupGui()
        self._setupMenu()

    """ CLASS METHODS """

    def _setupData(self):
        self._data.update({'scale': 100,
                           'nodes': []})

    def _setupGui(self):
        self.configure(padx=10, pady=10)
        self.canvas = CanvasFrame(self, relief=tk.SUNKEN)
        self.sidebar = SidebarFrame(self, relief=tk.SUNKEN)

        self.sidebar.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    def _setupMenu(self):
        menubar = tk.Menu(self._parent)
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
        filemenu.add_command(label="Exit", command=self._parent.quit)

        tspmenu = tk.Menu(menubar, tearoff=0)
        tspmenu.add_command(label="Solve tsp", command=self.solveTSP,
                            accelerator="Ctrl+P")
        self.bind_all("<Control-p>", self.solveTSP)
        tspmenu.add_command(label="Show convex hull",
                            command=self.showConvexHull,
                            accelerator="Ctrl+H")
        self.bind_all("<Control-h>", self.showConvexHull)
        tspmenu.add_command(label="Clear path",
                            command=lambda: self.commitChange('solution', []),
                            accelerator="Ctrl+Shift+P")
        self.bind_all("<Control-Shift-p>",
                      lambda: self.commitChange('solution', []))

        editormenu = tk.Menu(menubar, tearoff=0)
        editormenu.add_command(label="Clear Data", command=self.clear,
                               accelerator="Ctrl+C")
        self.bind_all("<Control-c>", self.clear)

        menubar.add_cascade(label="File", menu=filemenu)
        menubar.add_cascade(label="TSP", menu=tspmenu)
        menubar.add_cascade(label="Editor", menu=editormenu)
        self._parent.config(menu=menubar)

    def registerData(self, key, value):
        """Adds a new entry to the data dictionary """
        self._data.update({key: value})

    def unregisterData(self, key):
        """Removes a data entry from the data dictionary """
        del self._data[key]

    def registerObserver(self, observer):
        self._observer.append(observer)

    def unregisterObserver(self, observer):
        self._observer.remove(observer)

    def commitChange(self, key, value):
        self._data[key] = value
        self.notify(key)

    def notify(self, key='all'):
        ndata = self._data
        if key is not 'all':
            ndata = self._data[key]

        for o in self._observer:
            o.update(ndata)

    def clear(self, event=None):
        """ Clears all problem data from the program and resets the UI """
        self._data = {}
        for o in self._observer:
            o.clear()

    def putSolution(self, solution):
        """ Update the solution data and pass it to the sidebar and canvas.
        The solution is a list of indices."""
        solution.append(solution[0])  # append startnode to make tour circular
        self.commitChange('solution', solution)

    def addNode(self, xc, yc):
        """ Add a node to the nodes array
        and pass it to the GUI"""
        # update data
        node_list = self._data['nodes']
        color = self._data['selectedColor']

        new_node = Node(len(node_list), xc, yc, color)
        new_nodelist = node_list.append(new_node)

        self.commitChange('nodes', new_nodelist)

    def solveTSP(self, event=None):
        """ Call the util module to solve the currently drawn
        problem and pass self.putSolution as the callback.
        As the util module uses an external program which works
        on .tsp files, the drawn problem is exported to a temporary file"""
        dummy = tsputil.FilenameWrapper("tmpfile.tsp")
        tspio.exportTSP(
            self._data['nodes'], self._data['scale'],
            lambda f: tsputil.solveTSP(f, self.putSolution), dummy)

    def showConvexHull(self, event=None):
        """ Call the util module to calculate the convex hull and
        pass self.putSolution as the callback."""
        solution = tsputil.get_convex_hull(self._data['nodes'])
        # map nodes to their ids
        solution = list(map(lambda n: n.id, solution))
        self.putSolution(solution)

    def exportTSP(self, event=None):
        """ Export the loaded problem via the IO module in .tsp format"""
        tspio.exportTSP(
            self._data['nodes'], self._data['scale'],
            lambda f: self.commitChange('filename', f))

    def exportTIKZ(self, event=None):
        """ Export the loaded problem via the IO module as a tikz graphic
        in .tex format"""
        tspio.exportTIKZ(self._data['nodes'], self._data['scale'])

    def importTSP(self, event=None):
        """ Load data from a .tsp file via the IO module """
        tspio.importTSP(self.putLoadedData)

    def putLoadedData(self, filename, nodes, groups):
        """ Fills the internal data structures with the loaded data.
            !!! No error handling or validity checks !!!"""
        self.clear()

        node_list = []
        # If the nodes are not grouped, draw them in the currently
        # selected color
        if groups == []:
            color = self._data['selectedColor']
            for node in nodes:
                new_node = Node(len(node_list),
                                int(node[0] / self._data['scale']),
                                int(node[1] / self._data['scale']), color)
                node_list.append(new_node)
        # if the nodes are grouped, draw nodes from the same group in the same
        # color
        else:
            # iterate over groups
            for (i, g) in enumerate(groups):
                # iterate over node ids in the group
                for e in g:
                    # get node coordinates
                    node = nodes[e - 1]
                    new_node = Node(len(node_list),
                                    int(node[0] / self._data['scale']),
                                    int(node[1] / self._data['scale']), i)
                    node_list.append(new_node)

        self.commitChange('filename', filename)
        self.commitChange('nodes', node_list)

    def deleteNode(self, xc, yc):
        """ removes a node form the data structures and the canvas.
        As the nodes are stored as a list, the ids of the nodes after
        the deleted one have to be updated """
        # find nodeobject in nodes list
        found = False
        target = None
        node_list = self._data['nodes']
        for n in node_list:
            if not found:
                if n.x == xc and n.y == yc:
                    target = n
                    found = True
            else:
                # update id
                n.id = n.id - 1
        node_list.remove(target)
        self.commitChange('nodes', node_list)

    def getData(self, key):
        return self._data[key]


if __name__ == '__main__':
    root = tk.Tk()
    MainApplication(root).pack(fill=tk.BOTH, expand=True)
    root.mainloop()
