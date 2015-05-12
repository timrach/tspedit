try:
    # for Python2
    import Tkinter as tk
except ImportError:
    # for Python3
    import tkinter as tk

from ResizingCanvas import *
from BottomBarWidget import *


class CanvasFrame(tk.Frame):

    """ The CanvasFrame Module handles the UI for the canvas and passes
    events and data between the MainApplication and the Canvas"""

    def __init__(self, parent, datacontroller, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        """ DATA """
        self.width = 1070  # Canvaswidth
        self.height = 650  # Canvasheight

        """ GUI """
        self.canvas = ResizingCanvas(self, datacontroller,
                                     width=self.width, height=self.height)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.bottomBar = BottomBarWidget(self, datacontroller)
        self.bottomBar.pack(side=tk.BOTTOM, anchor=tk.E, fill=tk.X)
