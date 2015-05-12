from SidebarWidget import *
import tspio


class FileInfoWidget(SidebarWidget):

    def __init__(self, parent, datacontroller, **options):
        SidebarWidget.__init__(self, parent, text='File', **options)

        """ Public vars """
        self.keywords = ['fileinfo', 'nodes', 'startnode']

        """ Private vars """
        self._datacontroller = datacontroller

        # FILENAME LABEL
        self._filenameLabel = tk.Label(
            self.subFrame, text="Filename: Undefined")
        self._filenameLabel.pack(side=tk.TOP, anchor=tk.W)
        # COMMENT TEXT
        self._commentText = tk.Text(self.subFrame, width=30, height=1)
        self._commentText.pack(side=tk.TOP, anchor=tk.W)
        self._commentText.insert(0.0, 'TYPE PROBLEM DESCRIPTION HERE')
        self._commentText.bind("<Return>", self.onTextChange)
        self._commentText.bind("<FocusOut>", self.onTextChange)
        # STARTNODE LABEL
        self._startnodeLabel = tk.Label(self.subFrame, text="Startnodes: []")
        self._startnodeLabel.pack(side=tk.TOP, anchor=tk.W)
        # GROUPS LABEL
        self._groupsLabel = tk.Label(self.subFrame, text="Groups: None")
        self._groupsLabel.pack(side=tk.TOP, anchor=tk.W)
        # DIMENSION LABEL
        self._dimensionLabel = tk.Label(self.subFrame, text="Dimension: 0")
        self._dimensionLabel.pack(side=tk.TOP, anchor=tk.W)

        self._datacontroller.registerData('fileinfo', {'filename': None,
                                                       'comment': None})
        self._datacontroller.registerData('startnode', [])
        self._datacontroller.registerObserver(self, self.keywords)

    def onTextChange(self, event):
        filename = self._datacontroller.getData('fileinfo')['filename']
        comment = self._commentText.get(
            0.0, tk.END).replace('\n', '').strip(' \t\n\r')
        self._datacontroller.commitChange(
            'fileinfo',
            {'filename': filename,
             'comment': comment})

    def dataUpdate(self, key, data):
        if key is 'startnode':
            if data:
                res = []
                for node in data:
                    if node.start:
                        res.append(node.id)
                self._startnodeLabel.config(text="Startnodes: " + str(res))
        elif key is 'nodes':
            self._dimensionLabel.config(text="Dimension: " + str(len(data)))
            self._groupsLabel.config(
                text="Groups: " + str(len(tspio.getGroups(data))))
        elif key is 'fileinfo':
            self._filenameLabel.config(
                text="Filename: " + str(data['filename']))
            self._commentText.delete(0.0, tk.END)
            self._commentText.insert(0.0, str(data['comment']))
