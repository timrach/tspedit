"""
EditWidget.py
See class description
"""
from SidebarWidget import SidebarWidget
import tsputil
try:
    # for Python2
    import Tkinter as tk
except ImportError:
    # for Python3
    import tkinter as tk


class EditWidget(SidebarWidget):

    """ The EditWidget shows a list of all nodes in the currently loaded
        problem and a listbox where the current node color can be selected.
    """

    def __init__(self, parent, datacontroller, **options):
        SidebarWidget.__init__(self, parent, text='Edit', **options)

        # Public vars
        self.keywords = ['nodes', 'startnode', 'selectedNode']

        # Private vars
        self._datacontroller = datacontroller
        self._node_listbox = None
        self._colorvar = None
        self._nodelist_labelframe = None

        # setup ui elements
        self._setup_gui()

        # Register Data and register as observer
        self._datacontroller.register_data('nodecolor', tsputil.COLORS[0])
        self._datacontroller.register_observer(self, self.keywords)

    def _setup_gui(self):
        """ Initializes and positions the ui elements:
            | - color option frame
                | - color list label
                | - color option menu
            | - node list label frame
                | node list box
                | vertical scrollbar
            | - button frame
                | - delete button
                | - toggle start button"""

        # COLOR OPTION FRAME
        color_frame = tk.Frame(self._sub_frame)
        color_frame.pack(side=tk.TOP, anchor=tk.W)
        # COLOR LIST LABEL
        color_list_label = tk.Label(color_frame, text="Color:")
        color_list_label.pack(side=tk.LEFT, anchor=tk.W)
        # COLOR OPTIONMENU
        self._colorvar = tk.StringVar(color_frame)
        self._colorvar.set(tsputil.COLORS[0])  # default value
        # register color option for the selection event
        # if a color is selected, the global color will be
        # switched by the switchColor method
        self._colorvar.trace("w", lambda a, b, c: self._on_dropdown_select())
        color_option = tk.OptionMenu(*((color_frame, self._colorvar)
                                       + tuple(tsputil.COLORS)))
        color_option.pack(side=tk.RIGHT, anchor=tk.W)

        # NODE LIST Frame
        self._nodelist_labelframe = tk.LabelFrame(
            self._sub_frame, text="Coordinates (0):", padx=5, pady=10)
        # NODE LIST BOX
        self._scrollbar = tk.Scrollbar(
            self._nodelist_labelframe, orient=tk.VERTICAL)
        self._node_listbox = tk.Listbox(
            self._nodelist_labelframe, bd=0,
            yscrollcommand=self._scrollbar.set,
            selectmode=tk.SINGLE)
        self._node_listbox.bind('<<ListboxSelect>>',
                                lambda e: self._on_listbox_select())
        self._node_listbox.pack(side=tk.LEFT, expand=1, fill=tk.X, anchor=tk.W)
        self._scrollbar.config(command=self._node_listbox.yview)
        self._scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self._nodelist_labelframe.pack(side=tk.TOP, fill=tk.X, anchor=tk.W)

        # BUTTON FRAME AND BUTTONS
        button_frame = tk.Frame(self._sub_frame)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, anchor=tk.W)
        delete_button = tk.Button(button_frame, text="Delete",
                                  command=self._delete_button_clicked)
        delete_button.pack(side=tk.LEFT)
        startnode_button = tk.Button(button_frame, text="Toggle Start",
                                     command=self._startnode_button_clicked)
        startnode_button.pack(side=tk.LEFT)

    def _startnode_button_clicked(self):
        """ Gets called when the startnode button was clicked.
            Toggles the start bit on the node entry from the global node list
            representing the currently selected node and notifies the
            datacontroller about the change"""
        nodes = self._datacontroller.get_data('nodes')
        selection = self._node_listbox.curselection()
        if len(selection):
            # remove node from nodes array
            index = int(selection[0])
            nodes[index].start = not nodes[index].start
            self._datacontroller.commit_change('startnode', nodes)

    def _delete_button_clicked(self):
        """ Gets called when the delete button was clicked.
            Removes the node entry from the global node list representing the
            currently selected node and notifies the datacontroller about
            the change"""
        nodes = self._datacontroller.get_data('nodes')
        selection = self._node_listbox.curselection()
        if len(selection):
            # remove node from nodes array
            index = int(selection[0])
            del nodes[index]
            tsputil.reindex_nodes(nodes)
            self._datacontroller.commit_change('nodes', nodes)
            # reset selection
            listlen = self._node_listbox.size()
            if listlen:
                newindex = index
                if index > (listlen - 1):
                    newindex = (listlen - 1)
                self._datacontroller.commit_change(
                    'selectedNode', nodes[newindex])

    def _on_listbox_select(self):
        """ Gets called when the selected entry in the listbox changed.
            Identifies the selected node and notifies the datacontroller
            about the change."""
        nodes = self._datacontroller.get_data('nodes')
        index = int(self._node_listbox.curselection()[0])
        self._datacontroller.commit_change('selectedNode', nodes[index])

    def _on_dropdown_select(self):
        """Gets called when the user selects a color from the dropdown.
           Notifies the datacontroller about the change."""
        self._datacontroller.commit_change('nodecolor', self._colorvar.get())

    def data_update(self, key, data):
        """ Handles updates for registered data"""
        if key is 'nodes' or key is 'startnode':
            # remember selection
            selection = self._node_listbox.curselection()
            # clear data
            self._node_listbox.delete(0, tk.END)
            # insert new data
            for node in data:
                self._node_listbox.insert(node.nid, node.to_string())
            self._nodelist_labelframe.config(
                text="Coordinates (" +
                str(self._node_listbox.size()) + "):")
            # reset old selection
            if len(selection):
                self._node_listbox.selection_set(selection[0])
        elif key is 'selectedNode':
            self._node_listbox.selection_clear(0, tk.END)
            if data:
                self._node_listbox.selection_set(data.nid)
