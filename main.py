import csv
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
import numpy as np
from numpy import *
import re
from scipy.signal import argrelmin, argrelmax
import sys
import tkinter as tk
from tkinter import *
import tkinter.filedialog

#def on_key_event(event):
#    print('you pressed %s' % event.key)
#    key_press_handler(event, canvas, toolbar)

#canvas.mpl_connect('key_press_event', on_key_event)

class MenuBar(Frame):
  
    def __init__(self):
        super().__init__()   
         
        self.initMenuBar()
        
    def initMenuBar(self):
        menubar = Menu(root)
        root.config(menu=menubar)
        
        fileMenu = Menu(menubar)
        fileMenu.add_command(label="Open Files", command=self.selectFiles)
        fileMenu.add_command(label="Draw", command=self.draw)
        fileMenu.add_command(label="Analyze", command=self.analyzeElements)
        menubar.add_cascade(label="File", menu=fileMenu)
        
        settingsMenu = Menu(menubar)
        settingsMenu.add_command(label="Elements", command=self.selectElements)
        settingsMenu.add_command(label="Sensitivity", command=self.selectSensitivity)
        menubar.add_cascade(label="Settings", menu=settingsMenu)

    def selectFiles(self):
        global root
        filez = tk.filedialog.askopenfilenames(parent=root,title='Choose File(s)')
        
        global dataF
        dataF = root.tk.splitlist(filez)
        
        for x in dataF:
            if not x.endswith(".txt"):
                print("File(s) must all be .txt")
                dataF = []
                break
        
    def draw(self):
        if(len(dataF) == 0):
            print("Select File(s) First")
            return
        
        fileData = self.inputData(dataF[0])
        
        l.set_data(fileData[0], fileData[1])

        ax.relim()
        ax.autoscale_view(True,True,True)
        ax.margins(x = .1, y = .1)
        
        canvas.draw()
        
    def analyzeElements(self):
        if(len(dataE) == 0):
            print("Select Element(s)")
            return
    
        for f in dataF:
            heights = np.array([])
            
            data = self.inputData(f)
            for ele in dataE:
                heights = np.append(heights, self.findPeakHeight(data, elePeak[0][ele], elePeak[1][ele], elePeak[2][ele]))
                
            composition = self.calculateComp(heights)
            if(composition[0] == -1):
                return
            
            #self.drawComp(data, composition)
            self.outputToFile(f, composition)
        
    
    def findPeakHeight(self, graph, diffPeak, peakLow, peakHigh):
        high = 0
        low = 0
        lowX = 0
    
        adjPeak = int((diffPeak - graph[0][0])/(graph[0][1] - graph[0][0]))
        adjPeakLow = int((peakLow - graph[0][0])/(graph[0][1] - graph[0][0]))
        adjPeakHigh = int((peakHigh - graph[0][0])/(graph[0][1] - graph[0][0]))
    
        selection = np.array(graph[0][adjPeakLow : adjPeakHigh + 1 : 1])
        selection2 = np.array(graph[1][adjPeakLow : adjPeakHigh + 1 : 1])
    
        selection = np.vstack((selection, selection2))
    
        valleys = argrelmin(np.array(selection[1]))
        transformed = np.array([])
    
        for x in valleys[0]:
            if(low > selection[1][x]):
                low = selection[1][x]
                lowX = adjPeakLow + x
                
        for x in valleys[0]:
            transformed = np.append(transformed, selection[1][x] / low)
    
        maxX = lowX
     
        while True:
            maxX = maxX - 1
            larger = False
            for x in range(5):
                if(graph[1][maxX - x] > graph[1][maxX]):
                    larger = True
            if not larger:
                break
            
        high = graph[1][maxX]
    
        return (high - low)
        
    def calculateComp(self, heights):
        total = 0.0
        comp = np.array([])
        
        for x in range(len(heights)):
            comp = np.append(comp, heights[x] * eleSensitivity[dataS.get()][dataE[x]])
            total = total + comp[x]
        
        if(total == 0):
            print("Error in Composition Calculation")
            return np.array([-1])
        
        for x in range(len(heights)):
            comp[x] = comp[x] / total
            
        return comp
        

    def outputToFile(self, fileName, comp):
        fileName = fileName[:-4]
        
        f = open(fileName + "_comp.txt", "w")
        
        for x in range(len(comp)):
            f.write(str(ele[0][dataE[x]]) + "\t" + str(comp[x]) + "\n")
        
        f.close()
    
    
    #def drawComp(self, graph, comp):
        
        
    def inputData(self, loc):
        #Input and configure differentiated dataset
        with open(loc, 'r') as f:
            data = f.readlines()

        data.pop(0)

        for x in range(len(data)):
            point = data[x]
            data[x] = re.split(r'\t+', point.rstrip('\t'))

        data = np.array(data)
        data = data.transpose()
        data = data.astype(float)
    
        return data
        
    def selectElements(self):
        global elementWindow
        elementWindow = tk.Toplevel(self)
        elementWindow.wm_title("Pick Element(s)")
        
        bSubmit = Button(elementWindow, text="Submit", command=self.submitEle, pady=10)
        bSubmit.pack(side=BOTTOM, fill=X)
        
        global lbEleName
        lbEleName = Listbox(elementWindow, height=20, selectmode=MULTIPLE)
        lbEleName.pack(side=LEFT, fill="both", expand=True)
        
        for element in ele[0]:
            lbEleName.insert(END, element)
            
        sb = Scrollbar(elementWindow,orient=VERTICAL)
        sb.pack(side=RIGHT, fill=Y)
        sb.configure(command=lbEleName.yview)
        lbEleName.configure(yscrollcommand=sb.set)
        
    def submitEle(self):
        global dataE
        dataE = np.array(lbEleName.curselection())
        elementWindow.destroy()
        
    def selectSensitivity(self):
        global sensitivityWindow
        sensitivityWindow = tk.Toplevel(self)
        sensitivityWindow.wm_title("Pick Sensitivity")
        
        label = Label(sensitivityWindow, text="Select Energy Level")
        label.pack(side=TOP, pady=10)
        
        global dataS
        rb1 = Radiobutton(sensitivityWindow, text="3 eV", indicatoron=0, width=20, padx=20, pady=10, variable=dataS,value=0)
        rb1.pack(side=TOP)
        rb2 = Radiobutton(sensitivityWindow, text="5 eV", indicatoron=0, width=20, padx=20, pady=10, variable=dataS,value=1)
        rb2.pack(side=TOP)
        rb3 = Radiobutton(sensitivityWindow, text="10 eV", indicatoron=0, width=20, padx=20, pady=10, variable=dataS,value=2)
        rb3.pack(side=TOP)

def initTk():
    global root
    root = tk.Tk()
    root.wm_title("Slipstream")
    root.attributes('-zoomed', True)
    
def initMatplotlib():
    matplotlib.use('TkAgg')
    matplotlib.rc('font', size=10)

    global ax
    fig = Figure(figsize=(5, 4), dpi=100)
    ax = fig.add_subplot(111)

    global l
    l, = ax.plot(0, 0)
    
    global canvas
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.show()
    canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)

    toolbar = NavigationToolbar2TkAgg(canvas, root)
    toolbar.update()
    canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
    
def initVar():
    #Input and configure reference table
    with open('data/reference.csv', 'r') as f:
        reader = csv.reader(f)
        reference = list(reader)

    reference = np.array(reference)
    reference = reference.transpose()

    global ele
    ele = reference[0:1].astype(str)

    #Differential peak locations and ranges
    #DiffPeak : PeakLow : PeakHigh
    global elePeak
    elePeak = reference[2:5].astype(int)
    
    #Sensitivity constants for each element
    #3eV : 5eV : 10eV
    global eleSensitivity
    eleSensitivity = reference[-3:].astype(float)

    global dataS
    dataS = tk.IntVar()
    dataS.set(0)

    global dataE
    dataE = []

    global dataF
    dataF = ['data/W-Mo 5_post plasma_post TDS_bottom row 2 center_AES 1.txt']

def main():
    initTk()
    initMatplotlib()
    initVar()
    
    app = MenuBar()
    
    root.mainloop()

if __name__ == '__main__':
    main()
