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

        # COLOR OPTION FRAME
        colorFrame = tk.Frame(self)
        # COLOR LIST LABEL
        color_list_label = tk.Label(colorFrame, text="Colors:").pack(side=tk.LEFT,anchor=tk.W)

        # COLOR OPTIONMENU
        self.colorVar = tk.StringVar(colorFrame)
        self.colorVar.set(colors[0]) # default value
        # register color option for the selection event
        # if a color is selected, the global color will be
        # switched by the switchColor method
        self.colorVar.trace("w", self.switchColor)
        self.colorOption = tk.OptionMenu(*((colorFrame, self.colorVar) + tuple(colors))).pack(side=tk.RIGHT,anchor=tk.W)
        
        

        # NODE LIST LABEL
        self.node_list_label = tk.Label(self, text="Coordinates (0):")
        # NODE LIST BOX
        self.node_listBox = tk.Listbox(self)

        colorFrame.pack(anchor=tk.W)
        self.node_list_label.pack(anchor=tk.W)
        self.node_listBox.pack(anchor=tk.W)
        clear_button.pack(anchor=tk.W)
        import_tsp_button.pack(anchor=tk.W)
        export_tsp_button.pack(anchor=tk.W)
        export_tikz_button.pack(anchor=tk.W)

    def clear(self):
        self.node_listBox.delete(0, tk.END)  # delete all entries

    def addNode(self, new_node):
        self.node_listBox.insert(new_node.id, new_node.toString())
        self.node_list_label.config(text="Coordinates (" +
                                    str(self.node_listBox.size()) + "):")

    def deleteNode(self, nid):
        self.node_listBox.delete(nid)

    def switchColor(self, *args):
        """ changes the colorvariable according to the selected item in the
        color listbox"""
        self.parent.selectedColor = colors.index(self.colorVar.get())
