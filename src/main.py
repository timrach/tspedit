#!/usr/local/bin/python3

import tkinter as tk
from CanvasFrame import *
from SidebarFrame import *
from node import *
import tspio

from tsputil import *
from tkinter.filedialog import asksaveasfile, askopenfile
import math


class MainApplication(tk.Frame):

    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)

        """ DATA """
        self.scale = 100  # factor coordinates are scaled with
        self.selectedColor = 0  # active colorid
        self.nodes = []  # internal node representation


        """ GUI """
        self.canvas = CanvasFrame(self, relief=tk.SUNKEN)
        self.sidebar = SidebarFrame(self,relief=tk.SUNKEN)

        self.sidebar.pack(side=tk.LEFT,fill=tk.BOTH, expand=True)
        self.canvas.pack(side=tk.LEFT,fill=tk.BOTH, expand=True)


    """ CLASS METHODS """

    def clear(self):
        """ Clears all problem data from the program and resets the UI """
        self.nodes = []  # reset nodes array
        self.canvas.clear()
        self.sidebar.clear()


    def exportTSP(self):
        tspio.exportTSP(self.nodes,self.scale)

    def exportTIKZ(self):
        tspio.exportTIKZ(self.nodes,self.scale)

    def importTSP(self):
        tspio.importTSP(self.putLoadedData)
        

    def putLoadedData(self, nodes, groups):
        """ Fills the internal data structures with the loaded data.
            !!! No error handling or validity checks !!!"""
        self.clear()
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
        #pass data to frames
        self.canvas.addNode(xc,yc, colors[self.selectedColor])
        #update data
        new_node = Node(len(self.nodes), xc, yc, self.selectedColor)
        self.nodes.append(new_node)
        self.sidebar.addNode(new_node)
        

    def deleteNode(self, xc, yc):
        """ removes a node form the data structures and the canvas.
        As the nodes are stored as a list, the ids of the nodes after 
        the delted one have to be updated """
        self.canvas.deleteNode(xc,yc)
        # find nodeobject in nodes list
        found = False
        target = None
        for n in self.nodes:
            if not found:
                if n.x == xc and n.y == yc:
                    target = n
                    self.sidebar.deleteNode(n.id)
                    found = True
            else:
                # update id
                n.id = n.id - 1
        self.nodes.remove(target)


if __name__ == '__main__':
    root = tk.Tk()
    MainApplication(root).pack(fill=tk.BOTH, expand=True)
    root.mainloop()
