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

        self.keywords = ['mouseGridPosition']

        # POSITION LABEL
        self.position_label = tk.Label(
            self, text="( X:0 , Y:0 )")

        # CENTER OF MASS SETTING
        enableComDrawing = tk.IntVar(self)
        enableComDrawing.set(0)
        self.comCheckButton = tk.Checkbutton(self, text="Draw center of mass ",
                                             variable=enableComDrawing,
                                             onvalue=1, offvalue=0)

        # CENTER OF GEOMETRY SETTING
        enableCogDrawing = tk.IntVar(self)
        enableCogDrawing.set(1)
        self.cogCheckButton = tk.Checkbutton(self,
                                             text="Draw geometrical center",
                                             variable=enableCogDrawing,
                                             onvalue=1, offvalue=0)

        self.position_label.pack(side=tk.RIGHT)
        # self.comCheckButton.pack(side=tk.LEFT)
        # self.cogCheckButton.pack(side=tk.LEFT)

        self._datacontroller.registerObserver(self, self.keywords)

    def dataUpdate(self, key, data):
        if key is 'mouseGridPosition':
            if data:
                (q, r) = data
                self.position_label.config(
                    text=("( X:" + str(q) + " , " + "Y:" + str(r)) + ")")
