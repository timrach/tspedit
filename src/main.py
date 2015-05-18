#!/usr/local/bin/python3
"""
	Bootstrapper for the tspedit program
"""

try:
    # for Python2
    import Tkinter as tk
except ImportError:
    # for Python3
    import tkinter as tk
from MainApplication import MainApplication

if __name__ == '__main__':
    ROOT = tk.Tk()
    MainApplication(ROOT).pack(fill=tk.BOTH, expand=True)
    ROOT.title("tspedit")
    ROOT.mainloop()
