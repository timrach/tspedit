"""
    IOModule.py
    See class description
"""
import tspio


class IOModule:

    """ The IOModule handles the io operations of the program:
        File import, file export
    """

    def __init__(self, parent, datacontroller):

        self._parent = parent
        self._datacontroller = datacontroller

    def import_tsp(self):
        """ Load data from a .tsp file via the IO module """

        data = tspio.import_tsp(self._datacontroller.get_data('scale'))
        if data:
            name = data[0]
            comment = data[1]
            nodes = data[3]
            # clear existing node data
            self._datacontroller.commit_change('nodes', [])
            # commit new data
            self._datacontroller.commit_change(
                'fileinfo', {'filename': name, 'comment': comment})
            self._datacontroller.commit_change('nodes', nodes)
            self._datacontroller.commit_change('startnode', nodes)

    def export_tsp(self):
        """ Export the loaded problem via the IO module in .tsp format"""
        nodes = self._datacontroller.get_data('nodes')
        scale = self._datacontroller.get_data('scale')
        info = self._datacontroller.get_data('fileinfo')
        comment = None
        if info:
            comment = info['comment']
        filename = tspio.export_tsp(nodes, scale, comment)
        self._datacontroller.commit_change(
            'fileinfo', {'filename': filename, 'comment': comment})
