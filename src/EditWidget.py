from SidebarWidget import *
import tsputil


class EditWidget(SidebarWidget):

    def __init__(self, parent, datacontroller, **options):
        SidebarWidget.__init__(self, parent, text='Edit', **options)

        """ Public vars """
        self.keywords = ['nodes', 'startnode', 'selectedNode']

        """ Private vars """
        self._datacontroller = datacontroller

        """ GUI """
        # COLOR OPTION FRAME
        self._colorFrame = tk.Frame(self.subFrame)
        self._colorFrame.pack(side=tk.TOP, anchor=tk.W)
        # COLOR LIST LABEL
        self._color_list_label = tk.Label(self._colorFrame, text="Color:")
        self._color_list_label.pack(side=tk.LEFT, anchor=tk.W)
        # COLOR OPTIONMENU
        self._colorVar = tk.StringVar(self._colorFrame)
        self._colorVar.set(tsputil.colors[0])  # default value
        # register color option for the selection event
        # if a color is selected, the global color will be
        # switched by the switchColor method
        self._colorVar.trace("w", self._onDropdownSelect)
        self._colorOption = tk.OptionMenu(
            *((self._colorFrame, self._colorVar) + tuple(tsputil.colors)))
        self._colorOption.pack(side=tk.RIGHT, anchor=tk.W)

        # NODE LIST Frame
        self._nodeListLabelFrame = tk.LabelFrame(
            self.subFrame, text="Coordinates (0):", padx=5, pady=10)
        # NODE LIST BOX
        self._scrollbar = tk.Scrollbar(
            self._nodeListLabelFrame, orient=tk.VERTICAL)
        self._nodeListBox = tk.Listbox(
            self._nodeListLabelFrame, bd=0, yscrollcommand=self._scrollbar.set,
            selectmode=tk.SINGLE)
        self._nodeListBox.bind('<<ListboxSelect>>', self._onListBoxSelect)
        self._nodeListBox.pack(side=tk.LEFT, fill=tk.X, anchor=tk.W)
        self._scrollbar.config(command=self._nodeListBox.yview)
        self._scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self._nodeListLabelFrame.pack(side=tk.TOP, fill=tk.X, anchor=tk.W)

        # BUTTON FRAME AND BUTTONS
        self._buttonFrame = tk.Frame(self.subFrame)
        self._buttonFrame.pack(side=tk.BOTTOM, fill=tk.X, anchor=tk.W)
        self._deleteButton = tk.Button(self._buttonFrame, text="Delete",
                                       command=self._deleteButtonClicked)
        self._deleteButton.pack(side=tk.LEFT)

        self._datacontroller.registerData('nodecolor', tsputil.colors[0])
        self._datacontroller.registerObserver(self, self.keywords)

    def _deleteButtonClicked(self):
        nodes = self._datacontroller.getData('nodes')
        selection = self._nodeListBox.curselection()
        if len(selection):
            # remove node from nodes array
            index = int(selection[0])
            del nodes[index]
            tsputil.reindexNodes(nodes)
            self._datacontroller.commitChange('nodes', nodes)
            # reset selection
            listlen = self._nodeListBox.size()
            if listlen:
                newindex = index
                if index > (listlen - 1):
                    newindex = (listlen - 1)
                self._datacontroller.commitChange(
                    'selectedNode', nodes[newindex])

    def _onListBoxSelect(self, *args):
        nodes = self._datacontroller.getData('nodes')
        index = int(self._nodeListBox.curselection()[0])
        self._datacontroller.commitChange('selectedNode', nodes[index])

    def _onDropdownSelect(self, *args):
        self._datacontroller.commitChange('nodecolor', self._colorVar.get())

    def dataUpdate(self, key, data):
        if key is 'nodes':
            # remember selection
            selection = self._nodeListBox.curselection()
            # clear data
            self._nodeListBox.delete(0, tk.END)
            # insert new data
            for node in data:
                self._nodeListBox.insert(node.id, node.toString())
            self._nodeListLabelFrame.config(
                text="Coordinates (" +
                str(self._nodeListBox.size()) + "):")
            # reset old selection
            if len(selection):
                self._nodeListBox.selection_set(selection[0])
        elif key is 'selectedNode':
            self._nodeListBox.selection_clear(0, tk.END)
            if data:
                self._nodeListBox.selection_set(data.id)
