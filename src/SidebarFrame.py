try:
    # for Python2
    import Tkinter as tk
except ImportError:
    # for Python3
    import tkinter as tk
import tsputil
from FileInfoWidget import *
from PathWidget import *
from EditWidget import *


class SidebarFrame(tk.Frame):

    """ The SidebarFrame Module handles the communication between UI on the
    sidebar and the mainapplication. """

    def __init__(self, parent, datacontroller, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)

        self.parent = parent

        # Hack: Label to keep the frame at a minimum width
        ttk.Label(
            self, text="-------------------------------------------").pack(side=tk.TOP, fill=tk.X)

        # File info widget
        self.fileInfo = FileInfoWidget(self, datacontroller)
        self.fileInfo.pack(fill=tk.X, side=tk.TOP)
        self.fileInfo.toggle()

        # Editing widget
        self.editWidget = EditWidget(self, datacontroller)
        self.editWidget.pack(fill=tk.X, side=tk.TOP)
        self.editWidget.toggle()

        # Path widget
        self.pathWidget = PathWidget(self, datacontroller)
        self.pathWidget.pack(fill=tk.X, side=tk.TOP)
        self.pathWidget.toggle()
