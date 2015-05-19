"""
    SidebarFrame.py
    See class description
"""
try:
    # for Python2
    import Tkinter as tk
    import ttk as ttk
except ImportError:
    # for Python3
    import tkinter as tk
    import tkinter.ttk as ttk
from FileInfoWidget import FileInfoWidget
from PathWidget import PathWidget
from EditWidget import EditWidget


class SidebarFrame(tk.Frame):

    """ The SidebarFrame Module handles the communication between UI on the
    sidebar and the mainapplication. """

    def __init__(self, parent, datacontroller, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)

        self.parent = parent

        # Hack: Label to keep the frame at a minimum width
        ttk.Label(
            self,
            text="-------------------------------------------").pack(
                side=tk.TOP, fill=tk.X)

        # File info widget
        file_info = FileInfoWidget(self, datacontroller)
        file_info.pack(fill=tk.X, side=tk.TOP)
        file_info.toggle()

        # Editing widget
        edit_widget = EditWidget(self, datacontroller)
        edit_widget.pack(fill=tk.X, side=tk.TOP)
        edit_widget.toggle()

        # Path widget
        path_widget = PathWidget(self, datacontroller)
        path_widget.pack(fill=tk.X, side=tk.TOP)
        path_widget.toggle()
