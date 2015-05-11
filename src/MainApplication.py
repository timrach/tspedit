#!/usr/local/bin/python3

import tkinter as tk
import tspio
from SidebarFrame import *
from CanvasFrame import *
from IOModule import *


class MainApplication(tk.Frame):

    """ The MainApplication Module holds references to all frames drawn
    in the main window. It holds all atomic data and acts as an
    interface for the communication between modules.
    That way all events are initially passed to this module which
    distributes the data to the other modules"""

    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)

        """ DATA """
        self._parent = parent

        """The data dictionary holding all global application data
           self._data = {'key1' : data1, 'key2' : data2}"""
        self._data = {}

        """The observer dictionary describing bindings of observers to data
           self._observers = {'key1' : [observer1,observer2],
                             'key2' : [observer3],
                             'all'  : [observer4, observer5]}"""
        self._observers = {'all': []}

        self._setupData()
        self._setupGui()
        self._setupMenu()

    """ CLASS METHODS """

    def registerData(self, key, value):
        """Adds a new entry to the data dictionary """
        if key not in self._data:
            self._data.update({key: value})
            self._observers.update({key: []})

    def unregisterData(self, key):
        """Removes a data entry from the data dictionary """
        del self._data[key]

    def registerObserver(self, observer, keys=['all']):
        for key in keys:
            if key not in self._data:
                self.registerData(key, None)
            self._observers[key].append(observer)

    def unregisterObserver(self, observer):
        for key in keys:
            self._observers[key].remove(observer)

    def commitChange(self, key, value):
        self._data[key] = value
        self.notify(key)

    def notify(self, key='all'):
        ndata = self._data
        if key is not 'all':
            ndata = self._data[key]
        for o in self._observers[key]:
            o.dataUpdate(key, ndata)

    def clear(self, event=None):
        """ Clears all problem data from the program and resets the UI """
        self._data = {}
        for key in self._observers:
            self._observers[key].clear()

    def getData(self, key):
        return self._data[key]

    def _setupData(self):
        self.registerData('scale', 100)
        self.registerData('nodes', [])

    def _setupGui(self):
        self.configure(padx=10, pady=10)

        self.sidebar = SidebarFrame(self, self)
        self.sidebar.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.canvas = CanvasFrame(self, self)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # no gui component
        self.iomodule = IOModule(self, self)

    def _setupMenu(self):
        menubar = tk.Menu(self._parent)
        self._parent.config(menu=menubar)

        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Import .tsp",
                             command=self.iomodule.importTSP,
                             accelerator="Ctrl+I")
        self.bind_all("<Control-i>", self.iomodule.importTSP)
        filemenu.add_command(label="Export .tsp",
                             command=self.iomodule.exportTSP,
                             accelerator="Ctrl+E")
        self.bind_all("<Control-e>", self.iomodule.exportTSP)
        filemenu.add_separator()

        menubar.add_cascade(label="File", menu=filemenu)
