import tkinter as tk
from tsputil import *


class SidebarFrame(tk.Frame):

    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)

        self.configure(padx=10, pady=10)
        self.parent = parent

        # EXPORT TSP BUTTON
        export_tsp_button = tk.Button(
            self, text="Export .tsp File", command=self.parent.exportTSP)

        # IMPORT TSP BUTTON
        import_tsp_button = tk.Button(
            self, text="Import .tsp File", command=self.parent.importTSP)

        # EXPORT TIKZ BUTTON
        export_tikz_button = tk.Button(
            self, text="Export tikz", command=self.parent.exportTIKZ)

        # CLEAR BUTTON
        clear_button = tk.Button(self, text="Clear", command=self.parent.clear)

        # FILENAMELABEL
        self.filename_label = tk.Label(self, text="Filename: UNNAMED")

        # COLOR OPTION FRAME
        colorFrame = tk.Frame(self)
        # COLOR LIST LABEL
        color_list_label = tk.Label(colorFrame, text="Color:").pack(
            side=tk.LEFT, anchor=tk.W)

        # COLOR OPTIONMENU
        self.colorVar = tk.StringVar(colorFrame)
        self.colorVar.set(colors[0])  # default value
        # register color option for the selection event
        # if a color is selected, the global color will be
        # switched by the switchColor method
        self.colorVar.trace("w", self.switchColor)
        self.colorOption = tk.OptionMenu(
            *((colorFrame, self.colorVar) + tuple(colors))).pack(side=tk.RIGHT, anchor=tk.W)

        # NODE LIST Frame
        self.nodeListLabelFrame = tk.LabelFrame(self, text="Coordinates (0):", padx=5,pady=10)
        # NODE LIST BOX
        
        scrollbar = tk.Scrollbar(self.nodeListLabelFrame, orient=tk.VERTICAL)
        self.node_listBox = tk.Listbox(self.nodeListLabelFrame,borderwidth=0,yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.node_listBox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.filename_label.pack(anchor=tk.W)
        colorFrame.pack(anchor=tk.W)
        self.nodeListLabelFrame.pack(anchor=tk.W,fill=tk.X, expand=1)
        self.node_listBox.pack(anchor=tk.W)
        clear_button.pack(anchor=tk.W, fill=tk.X,side=tk.TOP)
        export_tikz_button.pack(anchor=tk.W, fill=tk.X,side=tk.BOTTOM)
        export_tsp_button.pack(anchor=tk.W, fill=tk.X,side=tk.BOTTOM)
        import_tsp_button.pack(anchor=tk.W, fill=tk.X,side=tk.BOTTOM)
        
        

    def clear(self):
        self.node_listBox.delete(0, tk.END)  # delete all entries

    def addNode(self, new_node):
        self.node_listBox.insert(new_node.id, new_node.toString())
        self.nodeListLabelFrame.config(text="Coordinates (" +
                                    str(self.node_listBox.size()) + "):")

    def deleteNode(self, nid):
        self.node_listBox.delete(nid)

    def switchColor(self, *args):
        """ changes the colorvariable according to the selected item in the
        color listbox"""
        self.parent.selectedColor = colors.index(self.colorVar.get())

    def setFilename(self,filename):
        self.filename_label.config(text = "Filename: " + filename)
