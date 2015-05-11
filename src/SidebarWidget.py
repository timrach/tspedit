import tkinter as tk
import tkinter.ttk as ttk


class SidebarWidget(tk.Frame):
	def __init__(self, parent, text='',**options):
		tk.Frame.__init__(self, parent, **options)
		self.configure(pady=10)

		self._parent = parent

		self.show = False

		self.titleFrame=ttk.Frame(self)
		self.titleFrame.pack(fill=tk.X, expand=1)

		ttk.Label(self.titleFrame, text=text).pack(
			side=tk.LEFT, fill=tk.X, expand=1)

		self.toggleButton=ttk.Checkbutton(self.titleFrame, width=2, text='+', 
			command=self.toggle, style='Toolbutton')
		self.toggleButton.pack(side=tk.LEFT)

		self.subFrame=tk.Frame(self, relief=tk.SUNKEN,borderwidth=1)

	def toggle(self):
		self.show = not self.show
		if self.show:
			self.subFrame.pack(fill=tk.X, expand=1)
			self.toggleButton.configure(text='-')
		else:
			self.subFrame.forget()
			self.toggleButton.configure(text='+')

	def dataUpdate(self, key, data):
		""" Is implemented by inheriting classes """
		print("Note: A SidebarWidget observing " + key + " is not implementing dataUpdate.")
