import tkinter as tk
from ResizingCanvas import *


class CanvasFrame(tk.Frame):

    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        """ DATA """
        self.width = 1070  # Canvaswidth
        self.height = 650  # Canvasheight

        """ GUI """

        self.canvas = ResizingCanvas(
            self, width=self.width, height=self.height, relief=tk.SUNKEN)

        # BOTTOM BAR FRAME
        bottomBarFrame = tk.Frame(self)
        # POSITION LABEL
        self.position_label = tk.Label(
            bottomBarFrame, text="( X:0 , Y:0 )")

        # CENTER OF MASS SETTING
        enableComDrawing = tk.IntVar(bottomBarFrame)
        enableComDrawing.set(1)
        self.comCheckButton = tk.Checkbutton(
            bottomBarFrame, text="Draw center of mass ",
            variable=enableComDrawing, onvalue=1, offvalue=0,
            command=lambda: self.canvas.setCom(enableComDrawing.get()))

        # CENTER OF GEOMETRY SETTING
        enableCogDrawing = tk.IntVar(bottomBarFrame)
        enableCogDrawing.set(1)
        self.cogCheckButton = tk.Checkbutton(
            bottomBarFrame, text="Draw geometrical center",
            variable=enableCogDrawing, onvalue=1, offvalue=0,
            command=lambda: self.canvas.setCog(enableCogDrawing.get()))

        bottomBarFrame.pack(side=tk.BOTTOM, anchor=tk.E, fill=tk.X)
        self.position_label.pack(side=tk.RIGHT)
        self.comCheckButton.pack(side=tk.LEFT)
        self.cogCheckButton.pack(side=tk.LEFT)
        self.canvas.pack(fill=tk.BOTH, expand=True)

    def updatePositionLabel(self, q, r):
        """ update the position indicator label to show the selected
        field on the canvas"""
        # update label
        self.position_label.config(
            text=("( X:" + str(q) + " , " + "Y:" + str(r)) + ")")

    def addNode(self, x, y, color):
        self.canvas.addNode(x, y, color)

    def deleteNode(self, x, y):
        self.canvas.deleteNode(x, y)

    def clear(self):
        self.canvas.clear()

    def getNodes(self):
        return self.parent.getNodes()

    def putSolution(self, nodes, solution):
        self.canvas.delete("path_line")
        solution.append(solution[0])
        for c in range(0, len(solution) - 1):
            start = nodes[int(solution[c])]
            end = nodes[int(solution[c + 1])]
            self.canvas.line(start.x, start.y, end.x, end.y)
        self.canvas.tag_raise("node")

    def clearPath(self):
        self.canvas.delete("path_line")
