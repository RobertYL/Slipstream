import csv
from collections import defaultdict
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
from tkinter import font

class Engine():
    _files = []
    _eles = []
    _sens = 0

    _root = 0
    def __init__(self, root):
        self.__class__._root = root
        self.__class__._sens = tk.IntVar()
        self.__class__._sens.set(0)
        self.init_ref()

    _ref_ele = 0
    _ref_ele_peak = 0
    _ref_ele_sens = 0
    def init_ref(self):
        #Input and configure reference table
        with open('data/reference.csv', 'r') as f:
            self.reader = csv.reader(f)
            self.ref = list(self.reader)

        self.ref = np.array(self.ref)
        self.ref = self.ref.transpose()

        #List of elements
        self.__class__._ref_ele = self.ref[0:1].astype(str)

        #Differential peak locations and ranges for each element
        #DiffPeak : PeakLow : PeakHigh
        self.__class__._ref_ele_peak = self.ref[2:5].astype(int)

        #Sensitivity constants for each element
        #3eV : 5eV : 10eV
        self.__class__._ref_ele_sens = self.ref[-3:].astype(float)

    _l = 0
    _ax = 0
    _canvas = 0
    def init_plot(self, parent):
        self.parent = parent
        matplotlib.use('TkAgg')
        matplotlib.rc('font', size=10)

        self.fig = Figure(figsize=(5, 4), dpi=100)
        self.__class__._ax = self.fig.add_subplot(111)

        self.__class__._l, = self.__class__._ax.plot(0, 0)

        self.__class__._canvas = FigureCanvasTkAgg(self.fig, master=self.parent)
        self.__class__._canvas.show()
        self.__class__._canvas.get_tk_widget().pack(expand=1, fill=tk.BOTH)

        self.toolbar = NavigationToolbar2TkAgg(self.__class__._canvas, self.parent)
        self.toolbar.update()
        self.__class__._canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        self.__class__._canvas.mpl_connect('key_press_event', self.press)
        self.__class__._canvas.mpl_connect('button_press_event', self.click)

    _plot_select = 0
    _ele_select = 0
    _p_v_select = 0;
    def press(self, event):
        if event.key is not None:
            if not len(self.__class__._files) == 0:
                if(event.key == "right"):
                    self.__class__._plot_select += 1;
                elif(event.key == "left"):
                    self.__class__._plot_select -= 1;
                self.__class__._plot_select %= len(self.__class__._files)
                self.update_plot()
                self.update_fileF()
                self.update_eleF()
            if(event.key.isdigit()):
                self.__class__._ele_select = int(event.key)
                self.update_eleF()
            elif(event.key == "p"):
                self.__class__._p_v_select = 0
                self.update_eleF()
            elif(event.key == "v"):
                self.__class__._p_v_select = 1
                self.update_eleF()
            elif(event.key == "escape"):
                self.__class__._ele_select = 0
                self.update_eleF()

    def click(self, event):
        if event.dblclick and event.button == 1:
            self.__class__._points[(self.__class__._plot_select, self.__class__._eles[self.__class__._ele_select -
                1])][self.__class__._p_v_select][0] = self.__class__._data[self.__class__._plot_select][0][int(((event.xdata -
                self.__class__._data[self.__class__._plot_select][0][0])/(self.__class__._data[self.__class__._plot_select][0][1] -
                self.__class__._data[self.__class__._plot_select][0][0])) - 0.5)]
            self.__class__._points[(self.__class__._plot_select, self.__class__._eles[self.__class__._ele_select -
                1])][self.__class__._p_v_select][1] = self.__class__._data[self.__class__._plot_select][1][int(((event.xdata -
                self.__class__._data[self.__class__._plot_select][0][0])/(self.__class__._data[self.__class__._plot_select][0][1] -
                self.__class__._data[self.__class__._plot_select][0][0])) - 0.5)]
            self.update_eleF()

    _fileT = 0
    def init_file_dis(self, parent):
        self.parent = parent
        self.fileF = tk.Frame(self.parent, bg="#BFBFBF", borderwidth=5, relief=tk.RIDGE)
        self.fileLF = tk.LabelFrame(self.fileF, text="File(s) Selected", bg="#BFBFBF")
        self.fileLF.bind("<Enter>", lambda event:self.fileLF.config(fg="red"))
        self.fileLF.bind("<Leave>", lambda event:self.fileLF.config(fg="black"))
        self.fileLF.bind("<Button-1>", self.select_files)

        self.__class__._fileT = tk.Text(self.fileLF, bg="lightgray", relief=tk.FLAT)
        self.__class__._fileT.pack(expand=1, fill=tk.BOTH, padx=20, pady=20)
        self.__class__._fileT.config(highlightthickness=0, state=tk.DISABLED)
        self.__class__._fileT.bind("<Enter>", lambda event:self.fileLF.config(fg="black"))
        self.__class__._fileT.bind("<Leave>", lambda event:self.fileLF.config(fg="red"))

        self.fileLF.pack(expand=1, fill=tk.BOTH, padx=10, pady=10)
        self.fileLF.pack_propagate(0)
        self.fileF.grid(row=0, column=0, sticky="NESW")

    _eleT = 0
    def init_ele_dis(self, parent):
        self.parent = parent
        self.eleF = tk.Frame(self.parent, bg="#BFBFBF", borderwidth=5, relief=tk.RIDGE)
        self.eleLF = tk.LabelFrame(self.eleF, text="Element(s) Selected", bg="#BFBFBF")
        self.eleLF.bind("<Enter>", lambda event:self.eleLF.config(fg="red"))
        self.eleLF.bind("<Leave>", lambda event:self.eleLF.config(fg="black"))
        self.eleLF.bind("<Button-1>", self.select_eles)

        self.__class__._eleT = tk.Text(self.eleLF, bg="lightgray", relief=tk.FLAT)
        self.__class__._eleT.pack(expand=1, fill=tk.BOTH, padx=20, pady=20)
        self.__class__._eleT.config(highlightthickness=0, state=tk.DISABLED)
        self.__class__._eleT.bind("<Enter>", lambda event:self.eleLF.config(fg="black"))
        self.__class__._eleT.bind("<Leave>", lambda event:self.eleLF.config(fg="red"))

        self.eleLF.pack(expand=1, fill=tk.BOTH, padx=10, pady=10)
        self.eleLF.pack_propagate(0)
        self.eleF.grid(row=1, column=0, sticky="NESW")

    def init_sen_dis(self, parent):
        self.parent = parent
        self.senF = tk.Frame(self.parent, bg="#BFBFBF", borderwidth=5,
            relief=tk.RIDGE)
        self.senLF = tk.LabelFrame(self.senF, text="Sensitivity", bg="#BFBFBF")
        self.senLF.grid_columnconfigure(0, weight=1)
        self.senLF.grid_columnconfigure(1, weight=1)
        self.senLF.grid_columnconfigure(2, weight=1)
        self.senLF.grid_rowconfigure(0, weight=1)

        self.rb1 = tk.Radiobutton(self.senLF, text="3 eV", indicatoron=0,
            padx=20, pady=20, variable=self.__class__._sens, value=0,
            command=self.update_eleF)
        self.rb1.grid(row=0, column=0, padx=10, pady=10)
        self.rb2 = tk.Radiobutton(self.senLF, text="5 eV", indicatoron=0,
            padx=20, pady=20, variable=self.__class__._sens, value=1,
            command=self.update_eleF)
        self.rb2.grid(row=0, column=1, padx=10, pady=10)
        self.rb3 = tk.Radiobutton(self.senLF, text="10 eV", indicatoron=0,
            padx=20, pady=20, variable=self.__class__._sens, value=2,
            command=self.update_eleF)
        self.rb3.grid(row=0, column=2, padx=10, pady=10)

        self.senLF.pack(expand=1, fill=tk.BOTH, padx=10, pady=10)
        self.senLF.grid_propagate(0)
        self.senF.grid(row=2, column=0, sticky="NESW")

    def update_plot(self):
        self.__class__._l.set_data(self.__class__._data[self.__class__._plot_select][0],
            self.__class__._data[self.__class__._plot_select][1])

        self.__class__._ax.relim()
        self.__class__._ax.autoscale_view(True,True,True)
        self.__class__._ax.margins(x = .1, y = .1)

        self.__class__._canvas.draw()

    def update_fileF(self):
        self.__class__._fileT.config(state=tk.NORMAL)
        self.__class__._fileT.delete(1.0, tk.END)
        for i, f in enumerate(self.__class__._files):
            if(self.__class__._plot_select == i):
                self.__class__._fileT.insert(tk.END, os.path.basename(f) + "\n", "highlight")
                self.__class__._fileT.tag_config("highlight", foreground="red")
            else:
                self.__class__._fileT.insert(tk.END, os.path.basename(f) + "\n")
        self.__class__._fileT.config(state=tk.DISABLED)

    def update_eleF(self):
        self.__class__._eleT.config(state=tk.NORMAL)
        self.__class__._eleT.delete(1.0, tk.END)
        for i, e in enumerate(self.__class__._eles):
            self.__class__._eleT.insert(tk.END, str(i + 1) + ") " +
                self.__class__._ref_ele[0][e] + ":" + "\n")
            self.__class__._eleT.insert(tk.END, "\t" + "S: " +
                str(self.__class__._ref_ele_sens[self.__class__._sens.get()][e]) + "\n")
            self.__class__._eleT.insert(tk.END, "\t" + "P: " + "[" +
                str(self.__class__._points[(self.__class__._plot_select, e)][0][0]) + ", " +
                str(round(self.__class__._points[(self.__class__._plot_select, e)][0][1], 3)) + "]" + "\n")
            self.__class__._eleT.insert(tk.END, "\t" + "V: " + "[" +
                str(self.__class__._points[(self.__class__._plot_select, e)][1][0]) + ", " +
                str(round(self.__class__._points[(self.__class__._plot_select, e)][1][1], 3)) + "]" + "\n")
            self.__class__._eleT.insert(tk.END, "\t" + "C: " +
                str(100.0 * self.__class__._points[(self.__class__._plot_select, e)][2]) + "%" + "\n")
            if(self.__class__._ele_select - 1 == i):
                self.__class__._eleT.tag_add("highlight", "%d.%d" % (1 + (i * 5), 0), "%d.%d" % (1 + (i * 5), 1000))
                self.__class__._eleT.tag_add("highlight", "%d.%d" % (3 + (i * 5) + self.__class__._p_v_select, 1), "%d.%d" % (3 + (i * 5) + self.__class__._p_v_select, 1000))
                self.__class__._eleT.tag_config("highlight", foreground="red")
        self.__class__._eleT.config(state=tk.DISABLED)

    _data = np.array([])
    def select_files(self, event=None):
        self.filez = tk.filedialog.askopenfilenames(parent=self.__class__._root, title='Choose File(s)')
        self.temp = self.__class__._root.tk.splitlist(self.filez)
        if(len(self.temp) == 0):
            return
        for f in self.temp:
            if not f.endswith(".txt"):
                print("File(s) must all be .txt")
                return

        self.__class__._files = self.temp
        self.__class__._data = [[] for i in range(len(self.__class__._files))]
        for i in range(len(self.__class__._files)):
            self.__class__._data[i] = self.input_file(self.__class__._files[i])

        self.__class__._plot_select = 0
        self.update_fileF()
        self.update_plot()

    def select_eles(self, event=None):
        if(len(self.__class__._files) == 0):
            return
        self.eleW = tk.Toplevel(self.__class__._root)
        self.eleW.wm_title("Pick Element(s)")
        self.eleW.bind('<Escape>', lambda event: self.eleW.destroy())

        self.lbEleName = tk.Listbox(self.eleW, height=20, selectmode=tk.MULTIPLE)
        self.bSubmit = tk.Button(self.eleW, text="Submit", command=self.submit_eles, pady=10)

        self.bSubmit.pack(side=tk.BOTTOM, fill=tk.X)
        self.lbEleName.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        for e in self.__class__._ref_ele[0]:
            self.lbEleName.insert(tk.END, e)

        self.sb = tk.Scrollbar(self.eleW,orient=tk.VERTICAL)
        self.sb.pack(side=tk.RIGHT, fill=tk.Y)
        self.sb.configure(command=self.lbEleName.yview)
        self.lbEleName.configure(yscrollcommand=self.sb.set)

    def submit_eles(self):
        self.__class__._eles = self.lbEleName.curselection()
        for i, e in enumerate(self.__class__._data):
            for ele in self.__class__._eles:
                self.__class__._points[(i, ele)] = [[-1, -1],[-1, -1], -1.0]
        self.update_eleF()
        self.eleW.destroy()

    _shift = 0
    def select_shift(self):
        if(len(self.__class__._files) == 0):
            return
        self.shiftW = tk.Toplevel(self.__class__._root)
        tk.Label(self.shiftW, text="Energy Shift").grid(row=0)
        self.shiftEntry = tk.Entry(self.shiftW)
        self.shiftEntry.grid(row=1)
        tk.Button(self.shiftW, text="Submit", command=self.submit_shift).grid(row=2)

    def submit_shift(self):
        self.__class__._shift = self.shiftEntry.get()
        self.shiftW.destroy()

    def input_file(self, loc):
        #Input and configure differentiated dataset
        with open(loc, 'r') as f:
            self.data = f.readlines()

        self.data.pop(0)

        for x in range(len(self.data)):
            self.point = self.data[x]
            self.data[x] = re.split(r'\t+', self.point.rstrip('\t'))

        self.data = np.array(self.data)
        self.data = self.data.transpose()
        self.data = self.data.astype(float)

        return self.data

    _points = {}
    def find(self):
        if(len(self.__class__._eles) == 0):
            print("Select Element(s)")
            return

        for dataset, data in enumerate(self.__class__._data):
            for ele in self.__class__._eles:
                self.points = self.find_peaks(data, ele)
                self.__class__._points[(dataset, ele)][0] = self.points[0]
                self.__class__._points[(dataset, ele)][1] = self.points[1]
        self.update_eleF()

    def analyze(self):
        if(len(self.__class__._eles) == 0):
            print("Select Element(s)")
            return

        for dataset in range(len(self.__class__._files)):
            for ele in self.__class__._eles:
                if self.__class__._points[(dataset, ele)][0][0] == -1 or self.__class__._points[(dataset, ele)][1][0] == -1:
                    print("Missing peaks and/or valleys")
                    return

        for dataset, data in enumerate(self.__class__._data):
            self.composition(dataset)
        self.update_eleF()

    def find_peaks(self, graph, ele):
        self.high = 0
        self.low = 0
        self.lowX = 0

        self.adjPeak = int((self.__class__._ref_ele_peak[0][ele] - graph[0][0])/(graph[0][1] - graph[0][0]))
        self.adjPeakLow = int((self.__class__._ref_ele_peak[1][ele] - graph[0][0])/(graph[0][1] - graph[0][0]))
        self.adjPeakHigh = int((self.__class__._ref_ele_peak[2][ele] - graph[0][0])/(graph[0][1] - graph[0][0]))

        self.x_range = np.array(graph[0][self.adjPeakLow : self.adjPeakHigh + 1 : 1])
        self.y_range = np.array(graph[1][self.adjPeakLow : self.adjPeakHigh + 1 : 1])

        self.range = np.vstack((self.x_range, self.y_range))

        self.valleys = argrelmin(np.array(self.range[1]))

        for x in self.valleys[0]:
            if(self.low > self.range[1][x]):
                self.low = self.range[1][x]
                self.lowX = self.adjPeakLow + x

        self.highX = self.lowX

        while True:
            self.highX = self.highX - 1
            self.larger = False
            for x in range(5):
                if(graph[1][self.highX - x] > graph[1][self.highX]):
                    self.larger = True
            if not self.larger:
                break

        self.high = graph[1][self.highX]

        self.highX *= graph[0][1] - graph[0][0]
        self.highX += graph[0][0]
        self.lowX *= graph[0][1] - graph[0][0]
        self.lowX += graph[0][0]

        return [[self.highX, self.high], [self.lowX, self.low]]

    def composition(self, dataset):
        total = 0.0
        comp = np.array([])

        for i, ele in enumerate(self.__class__._eles):
            comp = np.append(comp, (self.__class__._points[(dataset, ele)][0][1] - self.__class__._points[(dataset, ele)][1][1]) / self.__class__._ref_ele_sens[self.__class__._sens.get()][ele])
            total = total + comp[i]

        if(total == 0):
            print("Error in composition calculation for file " + self.__class__._files[dataset])
            return

        for i, ele in enumerate(self.__class__._eles):
            self.__class__._points[(dataset, ele)][2] = comp[i] / total

        return
    '''
    def annotate_plot(self):
        for ele in self.__class__._eles:
            self.__class__._ax.annotate("", xy=tuple(self.__class__._points[ele][0]),
                xycoords='data', xytext=tuple(self.__class__._points[ele][1]),
                textcoords='data', arrowprops=dict(facecolor="red", arrowstyle="-",
                connectionstyle="arc3,rad=0.1"),)

        self.update_plot()
    '''
