try:
    # for Python2
    import Tkinter as tk
except ImportError:
    # for Python3
    import tkinter as tk


class BottomBarWidget(tk.Frame):

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

        self._datacontroller.registerData('info', "")
        self._datacontroller.registerObserver(self, self.keywords)

    def dataUpdate(self, key, data):
        if key is 'mouseGridPosition':
            if data:
                (q, r) = data
                self.position_label.config(
                    text=("( X:" + str(q) + " , " + "Y:" + str(r)) + ")")
        if key is 'info':
            self.info_label.config(text=str(data))
