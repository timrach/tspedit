#!/usr/local/bin/python3

import tkinter as tk
from MainApplication import *

if __name__ == '__main__':
    root = tk.Tk()
    MainApplication(root).pack(fill=tk.BOTH, expand=True)
    root.mainloop()
