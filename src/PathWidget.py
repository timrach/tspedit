from SidebarWidget import *
from SolverModule import *
import tsputil


class PathWidget(SidebarWidget):

    def __init__(self, parent, datacontroller, **options):
        SidebarWidget.__init__(self, parent, text='Path', **options)

        """ Public vars """
        self.keywords = ['path']

        """ Private vars """
        self._datacontroller = datacontroller
        self._solverModule = SolverModule(self, datacontroller)

        self._solvers = ['None', 'Optimal Tour', 'Convex Hull']

        self._methods = {'None': self._solverModule.emptySolution,
                         'Optimal Tour': self._solverModule.concorde,
                         'Convex Hull': self._solverModule.convexHull}

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
            self._infoLabelFrame, orient=tk.VERTICAL)
        self._infoListBox = tk.Listbox(
            self._infoLabelFrame, bd=0, yscrollcommand=self._scrollbar.set,
            selectmode=tk.EXTENDED, width=25, height=5)
        self._infoListBox.pack(side=tk.LEFT, anchor=tk.W)
        self._scrollbar.config(command=self._infoListBox.yview)
        # SCROLLBAR NOT NEEDED YET
        #self._scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self._datacontroller.registerObserver(self, self.keywords)

    def _onDropdownSelect(self, *args):
        method = str(self._solverVar.get())
        self._methods[method]()
        pass

    def dataUpdate(self, key, data):
        if key is 'path':
            self._infoListBox.delete(0, tk.END)
            for (index, key) in enumerate(data):
                self._infoListBox.insert(index, str(key) + ": " + str(data[key]))
