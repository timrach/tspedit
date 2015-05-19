"""
    ResizingCanvas.py
    See class description
"""
try:
    # for Python2
    import Tkinter as tk
except ImportError:
    # for Python3
    import tkinter as tk
from Node import Node
import math
import copy
import tsputil

PADDING = 5


class ResizingCanvas(tk.Canvas):

    """ The Canvas Module. All drawable data is drawn here"""

    def __init__(self, parent, datacontroller, **kwargs):
        tk.Canvas.__init__(self, parent, **kwargs)

        self.configure(highlightthickness=0, background="white")

        # Private vars
        self._datacontroller = datacontroller
        self._geom = {'width': self.winfo_reqwidth(), 'wscale': 1.0,
                      'height': self.winfo_reqheight(), 'hscale': 1.0,
                      'fieldsize': 30}
        self._selected_node = None
        self._rows = math.floor(self._geom['height'] / self._geom['fieldsize'])
        self._cols = math.floor(self._geom['width'] / self._geom['fieldsize'])
        self._points = [None for i in range(0, int(self._rows * self._cols))]
        self._nodes = copy.copy(self._datacontroller.get_data('nodes'))

        # Used Tags:
        # ["selector", "node", "startnode", "path_line", "cog", "com"]

        """ register the canvas area for click and hover events.
            If the user clicks on the canvas call the canvas_clicked method
            when the user hovers over the canvas, the position indicator label
            is updated to show the coordinates of the selected field """
        self.bind("<Button-1>", self.canvas_clicked)
        self.bind("<Motion>", self.on_motion)
        self.bind("<Configure>", self.on_resize)
        self.draw_grid()

        self._datacontroller.register_data('selectedNode', ())
        self._datacontroller.register_data('mouseGridPosition', ())
        self._datacontroller.register_observer(
            self, ['nodes', 'startnode', 'path', 'selectedNode'])

    def on_resize(self, event):
        """ Gets called whenever the window is resized.
        Handles correct item scaling and updates data fields"""
        # determine the ratio of old width/height to new width/height
        wscale = float(event.width) / self._geom['width']
        hscale = float(event.height) / self._geom['height']
        self._geom['width'] = event.width
        self._geom['height'] = event.height
        # resize the canvas
        self.config(width=self._geom['width'], height=self._geom['height'])
        # rescale all the objects tagged with the "all" tag
        self._geom['hscale'] *= hscale
        self._geom['wscale'] *= wscale
        self.scale("all", 0, 0, wscale, hscale)

    def draw_grid(self):
        """Draws the grid for the node positions on the canvas
        as gray lines."""
        # draw vertical lines
        for x_value in range(0, int(self._cols + 1)):
            xcoord = x_value * self._geom['fieldsize']
            self.create_line(xcoord, 0, xcoord,
                             self._rows * self._geom['fieldsize'],
                             fill="#ddd", tags="grid")
        # draw horizontal lines
        for y_value in range(0, int(self._rows + 1)):
            ycoord = y_value * self._geom['fieldsize']
            self.create_line(0, ycoord, self._cols * self._geom['fieldsize'],
                             ycoord, fill="#ddd", tags="grid")
        # draw 0,0 indicator
        # vertical arrow for y axis
        self.create_line(
            0, 0, 0, self._geom['fieldsize'] * 2, arrow=tk.LAST, fill="green")
        # horizontal arrow for x axis
        self.create_line(
            0, 0, self._geom['fieldsize'] * 2, 0, arrow=tk.LAST, fill="red")
        self.move("all", 5, 5)

    def get_selected_cell(self, event):
        """Returns the coordinates of the cell the mouse is pointed on"""
        x_value = math.floor(
            (event.x - PADDING) / (self._geom['fieldsize']
                                   * self._geom['wscale']))
        y_value = math.floor(
            (event.y - PADDING) / (self._geom['fieldsize']
                                   * self._geom['hscale']))
        return (x_value, y_value)

    def on_motion(self, event):
        """ Gets called whenever the mouse is moved on the canvas.
        Calls the update routine for the position indicator label"""
        # get relative field coordinates
        self._datacontroller.commit_change(
            'mouseGridPosition', self.get_selected_cell(event))

    def canvas_clicked(self, event):
        """Callback for the click-event on the canvas area.
        Draws a point at the clicked position if the position is empty.
        If the click was on an existing point, the point is selected
        and the event passed to the other modules."""
        # get relative field coordinates
        (x_value, y_value) = self.get_selected_cell(event)
        # only do something if the clicked position is within bounds
        if (x_value < self._cols and y_value < self._rows
                and x_value >= 0 and y_value >= 0):
            point = self._points[int(y_value * self._cols + x_value)]
            # if there is no node yet, add one
            if point is None:
                new_nodes = self._datacontroller.get_data('nodes')
                color = self._datacontroller.get_data('nodecolor')
                new_nodes.append(Node(len(new_nodes), x_value, y_value, color))
                self._datacontroller.commit_change('nodes', new_nodes)

    def add_node(self, node):
        """ draws a point on the specified position on the canvas and adds
        the data to the nodes and points arrays"""
        index = int(node.y_coord * self._cols + node.x_coord)
        point = self.circle(node.x_coord, node.y_coord, 0.5, fill=node.color,
                            tags="node", activeoutline=tsputil.RESCOLORS[0],
                            activewidth=3)
        # register point for the click event
        self.tag_bind(point, "<Button-1>", lambda e: self.node_selected(index))
        self._points[index] = point

    def ind_to_coord(self, index):
        """ Converts an index to X,Y coordinates """
        y_value = math.floor(index / self._cols)
        x_value = index - y_value * self._cols
        return (x_value, y_value)

    def node_selected(self, index):
        """ Selects the point at the index position.
        If the point is already selected, it is deselected.
        In both cases the event is passed to the other modules"""
        if self._selected_node == index:
            self._selected_node = None
            self._datacontroller.commit_change('selectedNode', None)
        else:
            # find node in nodes array
            (x_value, y_value) = self.ind_to_coord(index)
            for node in self._nodes:
                if node.x_coord == x_value and node.y_coord == y_value:
                    self._datacontroller.commit_change('selectedNode', node)
                    break

    def draw_selection_indicator(self, index):
        """ Draws a red ring around the selected point """
        coords = self.ind_to_coord(index)
        self.circle(coords[0], coords[1], 0.5, outline=tsputil.RESCOLORS[1],
                    width=3, fill="", tags="selector")

    def draw_start_indicator(self, index):
        """ Draws a blue ring around the selected point """
        coords = self.ind_to_coord(index)
        self.circle(coords[0], coords[1], 0.6, outline=tsputil.RESCOLORS[2],
                    width=5, fill="", tags="startnode")

    def draw_center_of_mass(self):
        """ Draws a small blue ring at the center of mass position """
        self.delete("com")
        if len(self._nodes):
            # accumulate x and y coordinates
            x_sum = sum([node.x_coord for node in self._nodes])
            y_sum = sum([node.y_coord for node in self._nodes])
            # normalize accumulated values
            x_value = x_sum / len(self._nodes)
            y_value = y_sum / len(self._nodes)
            # draw the com circle
            self.circle(x_value, y_value, 0.2, outline="#44f",
                        width=3, fill="", tags="com")
            # lower the circle in the layer hierarchy
            self.tag_lower("com")

    def draw_geometrical_center(self):
        """ Draws a small blue ring at the geometrical center """
        self.delete("cog")
        if len(self._nodes):
            x_coords = [node.x_coord for node in self._nodes]
            y_coords = [node.y_coord for node in self._nodes]
            x_value = (max(x_coords) + min(x_coords)) / 2
            y_value = (max(y_coords) + min(y_coords)) / 2
            self.circle(x_value, y_value, 0.2, outline="#f44",
                        width=3, fill="", tags="cog")
            self.tag_lower("cog")

    def line(self, x_start, y_start, x_end, y_end):
        """ Draws a line from cell start to cell end """
        line = self.create_line(
            (x_start * self._geom['fieldsize'] +
             (self._geom['fieldsize'] / 2)) * self._geom['wscale'],
            (y_start * self._geom['fieldsize'] +
             (self._geom['fieldsize'] / 2)) * self._geom['hscale'],
            (x_end * self._geom['fieldsize'] +
             (self._geom['fieldsize'] / 2)) * self._geom['wscale'],
            (y_end * self._geom['fieldsize'] +
             (self._geom['fieldsize'] / 2)) * self._geom['hscale'],
            fill="#444", tags="path_line",
            activefill="black", width=3)
        self.move(line, PADDING * self._geom['wscale'],
                  PADDING * self._geom['hscale'])

    def circle(self, x_value, y_value, _radius, **options):
        """ Draws a circle at the center of cell x,y with radius _radius """
        radius = _radius * self._geom['fieldsize'] * 0.7071
        left = (
            (x_value + 0.5) * self._geom['fieldsize'] - radius) * self._geom['wscale']
        top = (
            (y_value + 0.5) * self._geom['fieldsize'] - radius) * self._geom['hscale']
        right = (
            (x_value + 0.5) * self._geom['fieldsize'] + radius) * self._geom['wscale']
        bottom = (
            (y_value + 0.5) * self._geom['fieldsize'] + radius) * self._geom['hscale']
        circ = self.create_oval(left, top, right, bottom, **options)
        self.move(circ, PADDING * self._geom['wscale'],
                  PADDING * self._geom['hscale'])
        return circ

    def delete_node(self, node):
        """ Delete the point at cell x,y"""
        ind = int(node.y_coord * self._cols + node.x_coord)
        if ind == self._selected_node:
            self.node_selected(ind)
        self.delete(self._points[ind])
        self._points[ind] = None

    def redraw_starts(self):
        """Deletes all start markers and redraws them. Is needed when
           startnodes are deleted"""
        self.delete("startnode")
        for node in self._nodes:
            if node.start:
                index = int(node.y_coord * self._cols + node.x_coord)
                self.draw_start_indicator(index)

    def data_update(self, key, data):
        """ Handles upates in the observed data"""
        if key is 'nodes':
            diffadd = list(set(data)-set(self._nodes))
            diffsub = list(set(self._nodes) - set(data))
            for node in diffadd:
                self.add_node(node)
            for node in diffsub:
                self.delete_node(node)
            self._nodes = copy.copy(data)
            self.redraw_starts()
            self.draw_center_of_mass()
            self.draw_geometrical_center()
        elif key is 'selectedNode':
            # clear old selection
            self.delete("selector")
            self._selected_node = None
            if data:
                # set new selection
                index = int(data.y_coord * self._cols + data.x_coord)
                self._selected_node = index
                self.draw_selection_indicator(index)
        elif key is 'path':
            self.delete("path_line")
            if 'Tour' in data:
                tour = data['Tour']
                for current in range(0, len(tour) - 1):
                    start = self._nodes[int(tour[current])]
                    end = self._nodes[int(tour[current + 1])]
                    self.line(start.x_coord, start.y_coord,
                              end.x_coord, end.y_coord)
            self.tag_raise("node")
        elif key is 'startnode':
            self.redraw_starts()
