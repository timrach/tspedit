import tkinter as tk
import tsputil


class SidebarFrame(tk.Frame):

    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)

        self.configure(padx=10, pady=10)
        self.parent = parent

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

        buttonFrame = tk.Frame(self.nodeListLabelFrame)
        deleteButton = tk.Button(
            buttonFrame, text="-", command=self.deleteButtonClicked)
        deleteButton.pack(side=tk.LEFT)

        infoLabelFrame = tk.LabelFrame(
            self, text="Info", padx=5, pady=5)

        scrollbar = tk.Scrollbar(infoLabelFrame, orient=tk.VERTICAL)
        self.infoListBox = tk.Listbox(
            infoLabelFrame, bd=0, yscrollcommand=scrollbar.set,
            selectmode=tk.EXTENDED, width=25)
        scrollbar.config(command=self.infoListBox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.filename_label.pack(anchor=tk.W)
        colorFrame.pack(anchor=tk.W)
        infoLabelFrame.pack(side=tk.BOTTOM, fill=tk.X, anchor=tk.W)
        self.infoListBox.pack(anchor=tk.W)
        self.nodeListLabelFrame.pack(side=tk.BOTTOM, anchor=tk.W,
                                     fill=tk.X)
        self.node_listBox.pack(anchor=tk.W)
        buttonFrame.pack(side=tk.BOTTOM, fill=tk.X)

    def deleteButtonClicked(self):
        toDelete = self.node_listBox.curselection()
        for id in toDelete:
            for n in self.parent.nodes:
                if n.id == id:
                    self.parent.deleteNode(n.x, n.y)

    def clear(self):
        self.node_listBox.delete(0, tk.END)  # delete all entries

    def addNode(self, new_node):
        self.node_listBox.insert(new_node.id, new_node.toString())
        self.nodeListLabelFrame.config(text="Coordinates (" +
                                       str(self.node_listBox.size()) + "):")

    def deleteNode(self, nid):
        self.node_listBox.delete(nid, tk.END)
        for i in range(nid, len(self.parent.nodes)):
            node = self.parent.nodes[i]
            self.node_listBox.insert(node.id, node.toString())
        self.nodeListLabelFrame.config(text="Coordinates (" +
                                       str(self.node_listBox.size()) + "):")

    def switchColor(self, *args):
        """ changes the colorvariable according to the selected item in the
        color listbox"""
        self.parent.selectedColor = tsputil.colors.index(self.colorVar.get())

    def setFilename(self, filename):
        self.filename_label.config(text="Filename: " + filename)

    def addPathInfo(self, nodes, path):
        self.removePathInfo()
        self.infoListBox.insert(0, "Minimal tourlength: " +
                                str(tsputil.getPathLength(nodes,
                                                          self.parent.scale,
                                                          path)))
        self.infoListBox.insert(1, "Tour: " + str(path))

    def removePathInfo(self):
        self.infoListBox.delete(0, tk.END)
