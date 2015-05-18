"""
    FileInfoWidget.py
    See class description
"""
from SidebarWidget import SidebarWidget
import tspio
try:
    # for Python2
    import Tkinter as tk
except ImportError:
    # for Python3
    import tkinter as tk


class FileInfoWidget(SidebarWidget):

    """ The file info widget displays all data for the currently loaded problem
        except for the node positions. It provides a textbox to change or add
        the comment describing the problem. Other data is shown in labels"""

    def __init__(self, parent, datacontroller, **options):
        SidebarWidget.__init__(self, parent, text='File', **options)

        # Public vars
        self.keywords = ['fileinfo', 'nodes', 'startnode']

        # Private vars
        self._datacontroller = datacontroller
        self._filename_label = None
        self._comment_text = None
        self._startnode_label = None
        self._groups_label = None
        self._dimension_label = None

        # draw ui
        self._setup_gui()

        # register data and register as observers
        self._datacontroller.register_data('fileinfo', {'filename': None,
                                                        'comment': None})
        self._datacontroller.register_data('startnode', [])
        self._datacontroller.register_observer(self, self.keywords)

    def _setup_gui(self):
        """ Setsup the shown gui:
            | - filename label
            | - comment text box
            | - startnode label
            | - groups label
            | - dimension label
        """
        # FILENAME LABEL
        self._filename_label = tk.Label(
            self._sub_frame, text="Filename: Undefined")
        self._filename_label.pack(side=tk.TOP, anchor=tk.W)
        # COMMENT TEXT
        self._comment_text = tk.Text(self._sub_frame, width=30, height=1)
        self._comment_text.pack(side=tk.TOP, anchor=tk.W)
        self._comment_text.insert(0.0, 'TYPE PROBLEM DESCRIPTION HERE')
        self._comment_text.bind("<Return>", lambda e: self.on_text_change())
        self._comment_text.bind("<FocusOut>", lambda e: self.on_text_change())
        # STARTNODE LABEL
        self._startnode_label = tk.Label(
            self._sub_frame, text="Startnodes: []")
        self._startnode_label.pack(side=tk.TOP, anchor=tk.W)
        # GROUPS LABEL
        self._groups_label = tk.Label(self._sub_frame, text="Groups: None")
        self._groups_label.pack(side=tk.TOP, anchor=tk.W)
        # DIMENSION LABEL
        self._dimension_label = tk.Label(self._sub_frame, text="Dimension: 0")
        self._dimension_label.pack(side=tk.TOP, anchor=tk.W)

    def on_text_change(self):
        """ Gets called when the user hits return in the comment text box,
            or the keyboard focus leaves the box. Updates the
            comment information and notifies the datacontroller
            about the change"""
        filename = self._datacontroller.get_data('fileinfo')['filename']
        comment = self._comment_text.get(
            0.0, tk.END).replace('\n', '').strip(' \t\n\r')
        self._datacontroller.commit_change(
            'fileinfo',
            {'filename': filename,
             'comment': comment})

    def data_update(self, key, data):
        """ Handles updates for registered data"""
        if key is 'startnode':
            if data:
                res = []
                for node in data:
                    if node.start:
                        res.append(node.nid)
                self._startnode_label.config(text="Startnodes: " + str(res))
        elif key is 'nodes':
            self._dimension_label.config(text="Dimension: " + str(len(data)))
            self._groups_label.config(
                text="Groups: " + str(len(tspio.get_groups(data))))
        elif key is 'fileinfo':
            self._filename_label.config(
                text="Filename: " + str(data['filename']))
            self._comment_text.delete(0.0, tk.END)
            self._comment_text.insert(0.0, str(data['comment']))
