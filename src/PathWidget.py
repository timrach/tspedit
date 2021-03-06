"""
    PathWidget.py
    See class description
"""
from SidebarWidget import SidebarWidget
from SolverModule import SolverModule
from collections import OrderedDict
try:
    # for Python2
    import Tkinter as tk
except ImportError:
    # for Python3
    import tkinter as tk


class PathWidget(SidebarWidget):

    """ The Pathwidget provides a dropdown with different solving
        methods. If a method is slected, the corresponding algorithm is
        executed and the path info is displayed in a information list box"""

    def __init__(self, parent, datacontroller, **options):
        SidebarWidget.__init__(self, parent, text='Path', **options)

        # Private vars
        self._datacontroller = datacontroller
        self._step = 0
        self._path_steps = []
        self._solver_var = None
        solver_module = SolverModule(self, datacontroller)
        self._methods = OrderedDict([('None', solver_module.empty_solution),
                                     ('Optimal Tour', solver_module.concorde),
                                     ('Convex Hull',
                                      solver_module.convex_hull),
                                     ('Convex Human Model',
                                      solver_module.convex_hull_model),
                                     ('Nearest Neighbor',
                                      solver_module.nearest_neighbor)])
        # setup the ui
        self._setup_gui()
        # register as observer
        self._datacontroller.register_observer(self, ['path', 'pathsteps'])

    def _setup_gui(self):
        """ UI """
        solvers = [key for key in self._methods]
        solver_container = tk.Frame(self._sub_frame)
        solver_container.pack(side=tk.TOP, anchor=tk.W)
        # SOLVER LABEL
        tk.Label(solver_container, text="Chose Path: ").pack(side=tk.LEFT)
        # Path Solvers Dropdown
        solvers_frame = tk.Frame(solver_container)
        solvers_frame.pack(side=tk.RIGHT, anchor=tk.W)
        self._solver_var = tk.StringVar(solvers_frame)
        self._solver_var.set(solvers[0])
        self._solver_var.trace("w", lambda a, b, c: self._on_dropdown_select())
        tk.OptionMenu(*((solvers_frame, self._solver_var) +
                        tuple(solvers))).pack(side=tk.RIGHT, anchor=tk.W)

        # INFO FRAME
        info_labelframe = tk.LabelFrame(
            self._sub_frame, text="Info", padx=5, pady=5)
        info_labelframe.pack(side=tk.TOP, fill=tk.X, anchor=tk.W)
        scrollbar = tk.Scrollbar(
            info_labelframe, orient=tk.HORIZONTAL)
        self._info_listbox = tk.Listbox(
            info_labelframe, bd=0, xscrollcommand=scrollbar.set,
            selectmode=tk.EXTENDED, width=25, height=5)
        self._info_listbox.pack(side=tk.TOP, anchor=tk.W, expand=1, fill=tk.X)
        scrollbar.config(command=self._info_listbox.xview)
        scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        # Stepper Controls
        stepper_frame = tk.Frame(self._sub_frame)
        stepper_frame.pack(side=tk.BOTTOM, fill=tk.X, anchor=tk.W)
        self._stepper_controls = [None, None, None, None]

        self._stepper_controls[0] = tk.Button(
            stepper_frame, text="<<", command=lambda: self._do_step("first"),
            state=tk.DISABLED)
        self._stepper_controls[1] = tk.Button(
            stepper_frame, text="<", command=lambda: self._do_step("prev"),
            state=tk.DISABLED)
        self._stepper_controls[2] = tk.Button(
            stepper_frame, text=">", command=lambda: self._do_step("next"),
            state=tk.DISABLED)
        self._stepper_controls[3] = tk.Button(
            stepper_frame, text=">>", command=lambda: self._do_step("last"),
            state=tk.DISABLED)
        self._stepper_controls[0].pack(side=tk.LEFT)
        self._stepper_controls[1].pack(side=tk.LEFT)
        self._stepper_controls[3].pack(side=tk.RIGHT)
        self._stepper_controls[2].pack(side=tk.RIGHT)

    def _on_dropdown_select(self):
        """Gets called when the user selects a method from the dropdown.
           Looks up the corresponding solving method and executes it"""
        method = str(self._solver_var.get())
        self._methods[method]()

    def _do_step(self, key):
        """ Is called when the user clicks a control button.
            The key identifies the number of steps to go through
            the path steps array. The path at that position is commited
            to the datacontroller to notify observers of 'path'."""
        if key is 'first':
            self._step = 0
        elif key is 'prev':
            self._step = max(0, self._step - 1)
        elif key is 'next':
            self._step = min(len(self._path_steps) - 1, self._step + 1)
        elif key is 'last':
            self._step = len(self._path_steps) - 1

        if self._step > 0:
            self._stepper_controls[0].config(state=tk.NORMAL)
            self._stepper_controls[1].config(state=tk.NORMAL)
        else:
            self._stepper_controls[0].config(state=tk.DISABLED)
            self._stepper_controls[1].config(state=tk.DISABLED)

        if self._step < len(self._path_steps) - 1:
            self._stepper_controls[3].config(state=tk.NORMAL)
            self._stepper_controls[2].config(state=tk.NORMAL)
        else:
            self._stepper_controls[3].config(state=tk.DISABLED)
            self._stepper_controls[2].config(state=tk.DISABLED)

        self._datacontroller.commit_change(
            'path', self._path_steps[self._step])

    def data_update(self, key, data):
        """handles updates in observed data"""
        if key is 'path':
            self._info_listbox.delete(0, tk.END)
            if data:
                for (index, key) in enumerate(data):
                    self._info_listbox.insert(
                        index, str(key) + ": " + str(data[key]))
        elif key is 'pathsteps':
            self._path_steps = data
            self._step = len(data) - 1
            if data:
                self._stepper_controls[0].config(state=tk.NORMAL)
                self._stepper_controls[1].config(state=tk.NORMAL)
            else:
                self._stepper_controls[0].config(state=tk.DISABLED)
                self._stepper_controls[1].config(state=tk.DISABLED)
                self._stepper_controls[3].config(state=tk.DISABLED)
                self._stepper_controls[2].config(state=tk.DISABLED)
