import tkinter as tk
import tsputil


class SidebarFrame(tk.Frame):

    """ The SidebarFrame Module handles the communication between UI on the
    sidebar and the mainapplication. """

    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)

        self.configure(padx=10, pady=10)
        self.parent = parent

        """ GUI """
        # FILENAMELABEL
        self.filename_label = tk.Label(self, text="Filename: UNNAMED")

        # COLOR OPTION FRAME
        colorFrame = tk.Frame(self)

        # COLOR LIST LABEL
        color_list_label = tk.Label(colorFrame, text="Color:")
        color_list_label.pack(side=tk.LEFT, anchor=tk.W)

        # COLOR OPTIONMENU
        self.colorVar = tk.StringVar(colorFrame)
        self.colorVar.set(tsputil.colors[0])  # default value
        # register color option for the selection event
        # if a color is selected, the global color will be
        # switched by the switchColor method
        self.colorVar.trace("w", self.switchColor)
        self.colorOption = tk.OptionMenu(
            *((colorFrame, self.colorVar) + tuple(tsputil.colors)))
        self.colorOption.pack(side=tk.RIGHT, anchor=tk.W)

        # NODE LIST Frame
        self.nodeListLabelFrame = tk.LabelFrame(
            self, text="Coordinates (0):", padx=5, pady=10)

        # NODE LIST BOX
        scrollbar = tk.Scrollbar(self.nodeListLabelFrame, orient=tk.VERTICAL)
        self.node_listBox = tk.Listbox(
            self.nodeListLabelFrame, bd=0, yscrollcommand=scrollbar.set,
            selectmode=tk.EXTENDED)
        scrollbar.config(command=self.node_listBox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # BUTTON FRAME AND BUTTONS
        buttonFrame = tk.Frame(self.nodeListLabelFrame)
        deleteButton = tk.Button(
            buttonFrame, text="-", command=self.deleteButtonClicked)
        deleteButton.pack(side=tk.LEFT)

        # INFO FRAME
        infoLabelFrame = tk.LabelFrame(
            self, text="Info", padx=5, pady=5)
        scrollbar = tk.Scrollbar(infoLabelFrame, orient=tk.VERTICAL)
        self.infoListBox = tk.Listbox(
            infoLabelFrame, bd=0, yscrollcommand=scrollbar.set,
            selectmode=tk.EXTENDED, width=25)
        scrollbar.config(command=self.infoListBox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # GUI POSITIONING
        self.filename_label.pack(anchor=tk.W)
        colorFrame.pack(anchor=tk.W)
        infoLabelFrame.pack(side=tk.BOTTOM, fill=tk.X, anchor=tk.W)
        self.infoListBox.pack(anchor=tk.W)
        self.nodeListLabelFrame.pack(side=tk.BOTTOM, anchor=tk.W, fill=tk.X)
        self.node_listBox.pack(anchor=tk.W)
        buttonFrame.pack(side=tk.BOTTOM, fill=tk.X)

    def deleteButtonClicked(self):
        """ Gets called when the delete button is clicked.
            Deletes the entry from the listbox and passes the
            event to the mainapplication """
        toDelete = self.node_listBox.curselection()
        for id in toDelete:
            for n in self.parent.nodes:
                if n.id == id:
                    self.parent.deleteNode(n.x, n.y)

    def clear(self):
        """ removes all entries from all ui elements """
        self.node_listBox.delete(0, tk.END)  # delete all entries
        self.removePathInfo()

    def addNode(self, new_node):
        """ Adds the node data to corresponding UI elements  """
        self.node_listBox.insert(new_node.id, new_node.toString())
        self.nodeListLabelFrame.config(text="Coordinates (" +
                                       str(self.node_listBox.size()) + "):")

    def deleteNode(self, nid):
        """ Removes the point with id nid corresponding UI elements  """
        self.node_listBox.delete(nid, tk.END)
        for i in range(nid, len(self.parent.nodes)):
            node = self.parent.nodes[i]
            self.node_listBox.insert(node.id, node.toString())
        self.nodeListLabelFrame.config(text="Coordinates (" +
                                       str(self.node_listBox.size()) + "):")

    def nodeSelected(self, coords):
        """ Determines the id of the node at the given position
            and updates UI elements displaying node data   """
        nodes = self.parent.nodes
        target = None
        for n in nodes:
            if n.x == coords[0] and n.y == coords[1]:
                target = n
                break
        self.node_listBox.selection_clear(0, tk.END)
        self.node_listBox.selection_set(n.id)
        self.putNodeInfo(coords, nodes, target)

    def nodeDeselected(self):
        """ Removes node info drom the info box"""
        self.addPathInfo(self.parent.nodes, self.parent.solution)

    def switchColor(self, *args):
        """ changes the colorvariable according to the selected item in the
        color listbox"""
        self.parent.selectedColor = tsputil.colors.index(self.colorVar.get())

    def setFilename(self, filename):
        """ Sets the text of the filename label"""
        self.filename_label.config(text="Filename: " + filename)

    def addPathInfo(self, nodes, path):
        """ Adds info of the drawn path to the infobox"""
        par = self.parent
        self.removePathInfo()
        if path:
            self.infoListBox.insert(0, "Tour: " + str(path))
            self.infoListBox.insert(1, "Tourlength: " +
                                    str(tsputil.getPathLength(nodes, par.scale,
                                                              path)))

    def removePathInfo(self):
        """ Clears the infobox """
        self.infoListBox.delete(0, tk.END)

    def putNodeInfo(self, coords, nodes, target):
        """ Adds info of the selected node to the infobox"""
        hull = tsputil.get_convex_hull(nodes)
        n = tsputil.nearestNeighbor(nodes, target)
        self.removePathInfo()
        self.infoListBox.insert(0, "Coordinates: " + str(coords))
        self.infoListBox.insert(1, "Color: " + tsputil.colors[target.color])
        self.infoListBox.insert(2, "On Convex Hull: " + str(target in hull))
        self.infoListBox.insert(3, "Nearest Neighbor: " + str(n))
