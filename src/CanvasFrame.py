"""
CanvasFrame.py
See class description
"""
try:
    # for Python2
    import Tkinter as tk
except ImportError:
    # for Python3
    import tkinter as tk

from ResizingCanvas import ResizingCanvas
from BottomBarWidget import BottomBarWidget


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

        self.bottombar = BottomBarWidget(self, datacontroller)
        self.bottombar.pack(side=tk.BOTTOM, anchor=tk.E, fill=tk.X)
