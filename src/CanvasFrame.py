import tkinter as tk
from ResizingCanvas import *
import math


class CanvasFrame(tk.Frame):

	def __init__(self, parent, *args, **kwargs):
		tk.Frame.__init__(self, parent, *args, **kwargs)
		self.parent = parent

		""" DATA """
		self.width = 1080  # Canvaswidth
		self.height = 660  # Canvasheight

		""" GUI """

		self.canvas = ResizingCanvas(
			self, width=self.width, height=self.height, relief=tk.SUNKEN)
		

		# POSITION LABEL
		self.position_label = tk.Label(
			self, text="Position:( X:0 , Y:0 )", anchor=tk.W)

		self.canvas.pack(fill=tk.BOTH,expand=True)
		self.position_label.pack()
		# oval objects on the canvas
		#self.points = [None for i in range(cols * rows)]


	def updatePositionLabel(self,q,r):
		""" update the position indicator label to show the selected
		field on the canvas"""
		# update label
		self.position_label.config(
			text=("Position:( X:" + str(q) + " , " + "Y:" + str(r)) + ")")

	
	def addNode(self,x,y,color):
		self.canvas.addNode(x,y,color)

	
		

	def deleteNode(self,x,y):
		self.canvas.deleteNode(x,y)


	def clear(self):
		self.canvas.clear()