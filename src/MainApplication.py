"""
    MainApplication.py
    See class description
"""
try:
    # for Python2
    import Tkinter as tk
except ImportError:
    # for Python3
    import tkinter as tk
import copy
from SidebarFrame import SidebarFrame
from CanvasFrame import CanvasFrame
from IOModule import IOModule


class MainApplication(tk.Frame):

    """ The MainApplication Module holds references to all frames drawn
    in the main window. It holds all atomic data and acts as an
    interface for the communication between modules.
    That way all events are initially passed to this module which
    distributes the data to the other modules"""

    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)

        # Private vars
        self._parent = parent
        """The data dictionary holding all global application data
           self._data = {'key1' : data1, 'key2' : data2}"""
        self._data = {}
        """ The _nullvalues dictionary holds all default values for the
        registered data. It is used when the program data is reset."""
        self._nullvalues = {}
        """The observer dictionary describing bindings of observers to data
           self._observers = {'key1' : [observer1,observer2],
                             'key2' : [observer3]}"""
        self._observers = {}

        self._setup_data()
        self._setup_gui()
        self._setup_menu()

    def register_data(self, key, value):
        """Adds a new entry to the data dictionary """
        if key not in self._data:
            self._nullvalues.update({key: copy.deepcopy(value)})
            self._data.update({key: copy.deepcopy(value)})
            self._observers.update({key: []})

    def unregister_data(self, key):
        """Removes a data entry from the data dictionary """
        del self._data[key]

    def register_observer(self, observer, keys):
        """Adds an object to the observers array for a given set of keys."""
        for key in keys:
            if key not in self._data:
                self.register_data(key, None)
            self._observers[key].append(observer)

    def unregister_observer(self, observer):
        """ Removes an observer from all observer lists"""
        for key in self.keys:
            self._observers[key].remove(observer)

    def commit_change(self, key, value):
        """ Observers call this method to commit changes in a data set
        registered under the given key. No type or validity checking
        for the value is done! Calling instances are responsible
        for validity"""
        self._data[key] = value
        self.notify(key)

    def notify(self, key):
        """ The method is called when the dataset of a given key has changed.
        All observers registered for that key are notified about the change."""
        ndata = self._data[key]
        for observer in self._observers[key]:
            observer.data_update(key, ndata)

    def clear(self):
        """ Clears all problem data from the program and resets the UI """
        self._nullvalues['nodes'] = []
        for key in self._data:
            self.commit_change(key, self._nullvalues[key])

    def get_data(self, key):
        """ Returns the dataset for a given key """
        return self._data[key]

    def _setup_data(self):
        """ Private: sets up globally used data """
        self.register_data('scale', 100)
        self.register_data('nodes', [])

    def _setup_gui(self):
        """ Private: Sets up the main components of the program:
        sidebar fame, canvas frame"""
        self.configure(padx=10, pady=10)

        self.sidebar = SidebarFrame(self, self, width=50)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y, expand=False)

        self.canvas = CanvasFrame(self, self)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # no gui component
        self.iomodule = IOModule(self, self)

    def _setup_menu(self):
        """ Private: Sets up the Main Menu for the program"""
        menubar = tk.Menu(self._parent)
        self._parent.config(menu=menubar)

        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="New file",
                             command=self.clear,
                             accelerator="Ctrl+N")
        self.bind_all("<Control-n>", lambda e: self.clear())
        filemenu.add_command(label="Import .tsp file",
                             command=self.iomodule.import_tsp,
                             accelerator="Ctrl+O")
        self.bind_all("<Control-o>", lambda e: self.iomodule.import_tsp())
        filemenu.add_command(label="Save .tsp file",
                             command=self.iomodule.export_tsp,
                             accelerator="Ctrl+S")
        self.bind_all("<Control-s>", lambda e: self.iomodule.export_tsp())
        menubar.add_cascade(label="File", menu=filemenu)
