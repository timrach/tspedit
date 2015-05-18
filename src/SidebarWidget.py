"""
    SidebarWidget.py
    See class description
"""
try:
    # for Python2
    import Tkinter as tk
    import ttk
except ImportError:
    # for Python3
    import tkinter as tk
    import tkinter.ttk as ttk


class SidebarWidget(tk.Frame):

    """ The SidebarWidget is an abstract class for widgets located on the
        sidebar. It abstracts the collapse, expand functionality and displays
        the name of the widget."""

    def __init__(self, parent, text='', **options):
        tk.Frame.__init__(self, parent, **options)

        self.configure(pady=10)

        self._parent = parent
        self._titel_label = None
        self._toggle_button = None
        self._show = False

        title_frame = ttk.Frame(self)
        title_frame.pack(fill=tk.X, expand=1)
        self._titel_label = ttk.Label(title_frame, text=text).pack(
            side=tk.LEFT, fill=tk.X, expand=1)
        self._toggle_button = ttk.Checkbutton(
            title_frame, width=2, text='+',
            command=self.toggle, style='Toolbutton')
        self._toggle_button.pack(side=tk.LEFT)
        self._sub_frame = tk.Frame(self, relief=tk.SUNKEN, borderwidth=1)

    def toggle(self):
        """ Toggles the show bit and accordingly expands or collapses the
            widgets contents by packing or forgetting the elements"""
        self._show = not self._show
        if self._show:
            self._sub_frame.pack(fill=tk.X, expand=1)
            self._toggle_button.configure(text='-')
        else:
            self._sub_frame.forget()
            self._toggle_button.configure(text='+')
