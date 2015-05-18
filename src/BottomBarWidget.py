"""
BottomBarWidget.py
See class description
"""
try:
    # for Python2
    import Tkinter as tk
except ImportError:
    # for Python3
    import tkinter as tk


class BottomBarWidget(tk.Frame):

    """Handles the UI for the bar below the canvas area.
       The mouse position is displayed by a Label on the right side
       and a label displaying information propagated through the
       'info' keyword on the left side"""

    def __init__(self, parent, datacontroller, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)

        self._parent = parent
        self._datacontroller = datacontroller

        self.keywords = ['mouseGridPosition', 'info']

        # POSITION LABEL
        self.position_label = tk.Label(self, text="( X:0 , Y:0 )")
        self.position_label.pack(side=tk.RIGHT)
        # Info LABEL
        self.info_label = tk.Label(self, text="")
        self.info_label.pack(side=tk.LEFT)

        self._datacontroller.register_data('info', "")
        self._datacontroller.register_observer(self, self.keywords)

    def data_update(self, key, data):
        """ Handles updates for registered data"""
        if key is 'mouseGridPosition':
            if data:
                (x_value, y_value) = data
                self.position_label.config(
                    text=("( X:" + str(x_value) + " , "
                          + "Y:" + str(y_value)) + ")")
        if key is 'info':
            self.info_label.config(text=str(data))
