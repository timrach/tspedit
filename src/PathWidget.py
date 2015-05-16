from SidebarWidget import *
from SolverModule import *
import tsputil


class PathWidget(SidebarWidget):

    def __init__(self, parent, datacontroller, **options):
        SidebarWidget.__init__(self, parent, text='Path', **options)

        """ Public vars """
        self.keywords = ['path', 'pathsteps']

        """ Private vars """
        self._datacontroller = datacontroller
        self._solverModule = SolverModule(self, datacontroller)

        self._solvers = ['None', 'Optimal Tour', 'Convex Hull', 'Convex Human Model' ]

        self._methods = {'None': self._solverModule.emptySolution,
                         'Optimal Tour': self._solverModule.concorde,
                         'Convex Hull': self._solverModule.convexHull,
                         'Convex Human Model': self._solverModule.convexHullModel}
        self._step = 0
        self._pathSteps = []

        """ UI """
        self._solverContainer = tk.Frame(self.subFrame)
        self._solverContainer.pack(side=tk.TOP, anchor=tk.W)
        # FILENAME LABEL
        self._solverLabel = tk.Label(
            self._solverContainer, text="Chose Path: ")
        self._solverLabel.pack(side=tk.LEFT)
        # Path Solvers Dropdown
        self._solversFrame = tk.Frame(self._solverContainer)
        self._solversFrame.pack(side=tk.RIGHT, anchor=tk.W)
        self._solverVar = tk.StringVar(self._solversFrame)
        self._solverVar.set(self._solvers[0])
        self._solverVar.trace("w", self._onDropdownSelect)
        self._solverOption = tk.OptionMenu(
            *((self._solversFrame, self._solverVar) + tuple(self._solvers)))
        self._solverOption.pack(side=tk.RIGHT, anchor=tk.W)

        # INFO FRAME
        self._infoLabelFrame = tk.LabelFrame(
            self.subFrame, text="Info", padx=5, pady=5)
        self._infoLabelFrame.pack(side=tk.TOP, fill=tk.X, anchor=tk.W)
        self._scrollbar = tk.Scrollbar(
            self._infoLabelFrame, orient=tk.HORIZONTAL)
        self._infoListBox = tk.Listbox(
            self._infoLabelFrame, bd=0, xscrollcommand=self._scrollbar.set,
            selectmode=tk.EXTENDED, width=25, height=5)
        self._infoListBox.pack(side=tk.TOP, anchor=tk.W, expand=1, fill=tk.X)
        self._scrollbar.config(command=self._infoListBox.xview)
        self._scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        #Stepper Controls
        self._stepperFrame = tk.Frame(self.subFrame)
        self._stepperFrame.pack(side=tk.BOTTOM, fill=tk.X, anchor=tk.W)

        self._firstStepButton = tk.Button(self._stepperFrame, text="<<",
                                       command=lambda: self._doStep("first"),
                                       state=tk.DISABLED)
        self._firstStepButton.pack(side=tk.LEFT)
        self._prevStepButton = tk.Button(self._stepperFrame, text="<",
                                       command=lambda: self._doStep("prev"),
                                       state=tk.DISABLED)
        self._prevStepButton.pack(side=tk.LEFT)

        self._lastStepButton = tk.Button(self._stepperFrame, text=">>",
                                       command=lambda: self._doStep("last"),
                                       state=tk.DISABLED)
        self._lastStepButton.pack(side=tk.RIGHT)
        self._nextStepButton = tk.Button(self._stepperFrame, text=">",
                                       command=lambda: self._doStep("next"),
                                       state=tk.DISABLED)
        self._nextStepButton.pack(side=tk.RIGHT)

        self._datacontroller.registerObserver(self, self.keywords)

    def _onDropdownSelect(self, *args):
        method = str(self._solverVar.get())
        self._methods[method]()
        pass


    def _doStep(self, key):
        if key is 'first':
            self._step = 0
        elif key is 'prev':
            self._step = max(0, self._step - 1)
        elif key is 'next':
            self._step = min(len(self._pathSteps) - 1, self._step + 1)
        elif key is 'last':
            self._step = len(self._pathSteps) - 1

        if self._step > 0:
            self._firstStepButton.config(state=tk.NORMAL)
            self._prevStepButton.config(state=tk.NORMAL)
        else:
            self._firstStepButton.config(state=tk.DISABLED)
            self._prevStepButton.config(state=tk.DISABLED)

        if self._step < len(self._pathSteps) - 1:
            self._lastStepButton.config(state=tk.NORMAL)
            self._nextStepButton.config(state=tk.NORMAL)
        else:
            self._lastStepButton.config(state=tk.DISABLED)
            self._nextStepButton.config(state=tk.DISABLED)

        self._datacontroller.commitChange('path', self._pathSteps[self._step])


    def dataUpdate(self, key, data):
        if key is 'path':
            self._infoListBox.delete(0, tk.END)
            if data:
                for (index, key) in enumerate(data):
                    self._infoListBox.insert(index, str(key) + ": " + str(data[key]))
        elif key is 'pathsteps':
            self._pathSteps = data
            self._step = len(data) - 1
            if data:
                self._firstStepButton.config(state=tk.NORMAL)
                self._prevStepButton.config(state=tk.NORMAL)
            else:
                self._firstStepButton.config(state=tk.DISABLED)
                self._prevStepButton.config(state=tk.DISABLED)
                self._lastStepButton.config(state=tk.DISABLED)
                self._nextStepButton.config(state=tk.DISABLED)

