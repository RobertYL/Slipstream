import csv
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
import numpy as np
from numpy import *
import os
import re
from scipy.signal import argrelmin, argrelmax
import sys
import tkinter as tk
import tkinter.filedialog

from engine import Engine

class MainApplication(tk.Frame):
    def __init__(self, root):
        self.root = root
        self.engine = Engine(self.root)

        self.init_main_frame()
        self.init_variable_frame()
        self.init_graph_frame()
        self.init_menu()

    def config_root(self):
        self.root.title("Slipstream")
        self.root.attributes('-zoomed', True)

    def init_main_frame(self):
        self.mainF = tk.Frame(self.root)
        self.config_root()
        self.mainF.grid_columnconfigure(0, weight=1)
        self.mainF.grid_columnconfigure(1, weight=3)
        self.mainF.grid_rowconfigure(0, weight=1)
        self.mainF.pack(expand=1, fill=tk.BOTH)

    def init_variable_frame(self):
        self.varF = tk.Frame(self.mainF)
        self.varF.grid_columnconfigure(0, weight=1)
        self.varF.grid_rowconfigure(0, weight=3)
        self.varF.grid_rowconfigure(1, weight=4)
        self.varF.grid_rowconfigure(2, weight=1)
        self.varF.grid_propagate(0)
        self.varF.grid(row=0, column=0, sticky="NESW")

        #Variable Frames: (Files:Elements:Sensitivity)
        self.engine.init_file_dis(self.varF)
        self.engine.init_ele_dis(self.varF)
        self.engine.init_sen_dis(self.varF)
        self.blankF = tk.Frame(self.varF, bg="#BFBFBF", borderwidth=5, relief=tk.RIDGE)
        self.blankF.grid(row=3, column=0, sticky="NESW")

    def init_graph_frame(self):
        self.graphF = tk.Frame(self.mainF, bg="#BFBFBF", borderwidth=5, relief=tk.RIDGE)
        self.graphF.grid_propagate(0)
        self.engine.init_plot(self.graphF)
        self.graphF.grid(row=0, column=1, sticky="NESW")

    def init_menu(self):
        self.menu = tk.Menu(self.root)
        self.root.config(menu=self.menu)

        #File Submenu
        self.fileMenu = tk.Menu(self.menu)
        self.fileMenu.add_command(label="Open Files", command=self.engine.select_files)
        self.fileMenu.add_command(label="Find Peaks", command=self.engine.find)
        self.fileMenu.add_command(label="Analyze", command=self.engine.analyze)
        self.menu.add_cascade(label="File", menu=self.fileMenu)

        #Settings Submenu
        self.settingsMenu = tk.Menu(self.menu)
        self.settingsMenu.add_command(label="Elements", command=self.engine.select_eles)
        self.settingsMenu.add_command(label="Energy Shift", command=self.engine.select_shift)
        self.menu.add_cascade(label="Settings", menu=self.settingsMenu)

if __name__ == '__main__':
   root = tk.Tk()
   main_app = MainApplication(root)
   root.mainloop()
