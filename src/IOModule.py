import tspio


class IOModule:

    def __init__(self, parent, datacontroller):

        self._parent = parent
        self._datacontroller = datacontroller

    def importTSP(self, event=None):
        """ Load data from a .tsp file via the IO module """

        (n, c, s, ns, g) = tspio.importTSP(
            self._datacontroller.getData('scale'))

        self._datacontroller.commitChange(
            'fileinfo', {'filename': n, 'comment': c})
        # clear existing node data
        self._datacontroller.commitChange('nodes', [])
        # TODO: COMMIT STARTNODE INFO
        self._datacontroller.commitChange('nodes', ns)
        self._datacontroller.commitChange('startnode', ns)

    def exportTSP(self, event=None):
        """ Export the loaded problem via the IO module in .tsp format"""
        nodes = self._datacontroller.getData('nodes')
        scale = self._datacontroller.getData('scale')
        info = self._datacontroller.getData('fileinfo')
        comment = None
        if info:
            comment = info['comment']
        filename = tspio.exportTSP(nodes, scale, comment)
        self._datacontroller.commitChange(
            'fileinfo', {'filename': filename, 'comment': comment})
