import matplotlib as mpl
import visa
import numpy as np
import sys
if sys.version_info[0] < 3:
   import Tkinter as tk
else:
   import tkinter as tk
import matplotlib.backends.tkagg as tkagg
from matplotlib.backends.backend_agg import FigureCanvasAgg
from tkinter import Tk, Label, Button, Entry, IntVar, END, W, E
from win32api import GetSystemMetrics
from scipy import signal
from scipy.signal import butter, lfilter
import math
import csv
from math import log
from matplotlib import rc
import matplotlib
from tkinter import StringVar
from tkinter import *
import matplotlib.pyplot as plt
from tkinter import ttk
from PIL import Image
import tkinter.font
import time

values=[]

global xaxis1
xaxis1=[]
xaxis1=np.asarray(xaxis1)

global yaxis1
yaxis1=[]
yaxis1=np.asarray(yaxis1)

def draw_program():

	def onclickax1():
		global xaxis1
		global yaxis1
		#print('xaxis1 is',xaxis1)
		#print('yaxis1 is',yaxis1)
		plt.figure()
		plt.plot(xaxis1,yaxis1)
		plt.grid()
		plt.xlabel('voltage (v)') # returns a Text instance
		plt.ylabel('current (A)')
		plt.show()
		#print('click registered')
	
	def StartMove(event):
		global selfx
		global selfy
		selfx = event.x
		selfy = event.y
		#print("selfx is:", (selfx));
		#print("selfy is:", (selfy));

	def StopMove(event):
		global selfx
		global selfy
		selfx = None
		selfy = None

	def OnMotion(event):
		deltax = event.x - selfx
		deltay = event.y - selfy
		x = root.winfo_x() + deltax
		y = root.winfo_y() + deltay
		#print("selfx set is:", (selfx));
		#print("selfy set is:", (selfy));
		root.geometry("+%s+%s" % (x, y))
		
	#def move_window(event):
	#	root.geometry('+{0}+{1}'.format(event.x_root, event.y_root))
	
	def restart_program():
		root.destroy()
		#window.destroy()
		draw_program()
		
	def draw_figure(canvas, figure, loc=(0, 0)):
		""" Draw a matplotlib figure onto a Tk canvas

		loc: location of top-left corner of figure on canvas in pixels.
		Inspired by matplotlib source: lib/matplotlib/backends/backend_tkagg.py
		"""
		figure_canvas_agg = FigureCanvasAgg(figure)
		figure_canvas_agg.draw()
		figure_x, figure_y, figure_w, figure_h = figure.bbox.bounds
		figure_w, figure_h = int(figure_w), int(figure_h)
		photo = tk.PhotoImage(master=canvas, width=figure_w, height=figure_h)

		# Position: convert from top-left anchor to center anchor
		canvas.create_image(loc[0] + figure_w/2, loc[1] + figure_h/2, image=photo)

		# Unfortunately, there's no accessor for the pointer to the native renderer
		tkagg.blit(photo, figure_canvas_agg.get_renderer()._renderer, colormode=2)

		# Return a handle which contains a reference to the photo object
		# which must be kept live or else the picture disappears
		return photo

	def clickedcommand():
		rm = visa.ResourceManager()
		rm.list_resources()
		#('ASRL1::INSTR', 'ASRL2::INSTR', 'GPIB0::24::INSTR')
		inst = rm.open_resource('GPIB0::24::INSTR',timeout=200000000)
		#inst.timeout(30)
		print(inst.query("*IDN?"))

		voltagestart=float(txtlowervoltage.get())
		voltagestop=float(txtuppervoltage.get())
		voltagestep=float(txtvoltagestep.get())
		currlim=float(txtcurrentlim.get())
		steps=np.floor((voltagestop-voltagestart)/voltagestep)
		steps=int(steps)
		#voltagestep=int(voltagestep)
		#inst.write(':ROUT: REAR')
		#print(inst.query(':ROUT?'))
		inst.write(':SENS:FUNC:CONC OFF')
		inst.write(':SOUR:FUNC VOLT')
		inst.write(':SENS:FUNC "CURR"')
		inst.write(':SENS:CURR:PROT %f'%currlim)
		inst.write(':SOUR:VOLT:START %f'%voltagestart)
		inst.write(':SOUR:VOLT:STOP %f'%voltagestop)
		inst.write(':SOUR:VOLT:STEP %f'%voltagestep)
		inst.write(':SOUR:VOLT:MODE SWE')
		inst.write(':SOUR:SWE:RANG AUTO')
		inst.write(':SOUR:SWE:SPAC LIN')
		print("source swept points are")
		sweptpoints=inst.query(':SOUR:SWE:POIN?')
		sweptpoints=int(sweptpoints)
		print(type(sweptpoints))
		print(sweptpoints-1)
		inst.write(':TRIG:COUN %d'%(sweptpoints))
		inst.write(':SOUR:DEL 0.1')
		inst.write(':OUTP ON')
		print("steps is")
		print(steps)
		print("currlim is")
		print(currlim)
		print("voltagestart is")
		print(voltagestart)
		print("voltagestop is")
		print(voltagestop)
		print("voltagestep is")
		print(voltagestep)
		#time.sleep(5)
		
		values=inst.query_ascii_values(':READ?')
		values = np.array(values)
		print(values)
		print(steps)
		numberofvalues=(len(values))

		spacer=int(numberofvalues/steps)

		voltagevalues=values[0::spacer]
		currentvalues=values[1::spacer]

		towrite=np.vstack((voltagevalues,currentvalues))

		towrite=np.transpose(towrite)

		inst.write(':OUTP OFF')

		print(voltagevalues)
		print(currentvalues)
		horiz_line_data = np.array([currlim for i in range(len(voltagevalues))])
		fig = mpl.figure.Figure(figsize=(5.5, 4.5))
		ax = fig.add_subplot(1,1,1)
		ax= fig.gca()	
		ax.set_xlabel('voltage (V)') # returns a Text instance
		ax.set_ylabel('current (A)')
		ax.grid()
		ax.plot(np.array(voltagevalues),np.array(currentvalues))
		global xaxis1
		global yaxis1
		xaxis1=np.array(voltagevalues)
		yaxis1=np.array(currentvalues)

		#ax.plot(np.array(voltagevalues),horiz_line_data)
		#fig.ylim(np.amax(currentvalues))
		for x in ax.get_yticklabels( ):
				x.set_fontsize( 'small' )
		for x in ax.get_xticklabels( ):
				x.set_fontsize( 'small' )
		fig.tight_layout()
		fig_x, fig_y = 100, 200
		fig_photo = draw_figure(canvas, fig, loc=(fig_x, fig_y))
		fig_w, fig_h = fig_photo.width(), fig_photo.height()
		mylabel = canvas.create_text((450, 200), text="swept signal",font=(labelfonttype,(labeltextsize))) 
		fig.savefig(txtfilename.get()+'.png')
		np.savetxt(txtfilename.get()+'.csv',towrite,delimiter=',',newline='\n'); 
		root.mainloop()

	# Create a canvas
	root = Tk()
	w, h = 1000, 700
	root.overrideredirect(True) # turns off title bar, geometry
	root.geometry('1000x700+300+300') # set new geometry

	# make a frame for the title bar
	title_bar = Frame(root, bg='#6d6e71', relief='raised', bd=3,borderwidth=0)

	# put a close button on the title bar
	close_button = Button(title_bar, text='X', command=root.destroy,borderwidth=0,bg="#6d6e71",fg="white",font=('futura md bt',(15)))
	name_label = Label(title_bar,text='Keithley Sweeper (Voltage sweep)',borderwidth=0,bg="#6d6e71",fg="white",font=('futura md bt',(15)))
	
	name_label.bind("<ButtonPress-1>", StartMove)
	name_label.bind("<ButtonRelease-1>", StopMove)
	name_label.bind("<B1-Motion>", OnMotion)
	window = Canvas(root, bg='black')
	
	title_bar.pack(expand=1, fill=X)
	close_button.pack(side=RIGHT)
	name_label.pack(side=LEFT)
	window.pack(expand=1, fill=BOTH)
	
	title_bar.bind("<ButtonPress-1>", StartMove)
	title_bar.bind("<ButtonRelease-1>", StopMove)
	title_bar.bind("<B1-Motion>", OnMotion)

	canvas = tk.Canvas(window, width=w, height=h)
	canvas.pack()
	
	labeltextsize=14
	labelfonttype='futura hv bt'
	
	textboxfontsize=15
	textboxwidth=10
	textboxfonttype='futura md bt'
	
	txtlowervoltage = Entry(canvas)
	txtlowervoltage.configure(background="#ededee",fg="#6d6e71",borderwidth=0,font=(textboxfonttype,(textboxfontsize)),width=textboxwidth,justify=CENTER)
	txtlowervoltage.insert(END, 'ENTER')
	txtuppervoltage = Entry(canvas)
	txtuppervoltage.configure(background="#ededee",fg="#6d6e71",borderwidth=0,font=(textboxfonttype,(textboxfontsize)),width=textboxwidth,justify=CENTER)
	txtuppervoltage.insert(END, 'ENTER')
	txtvoltagestep = Entry(canvas)
	txtvoltagestep.configure(background="#ededee",fg="#6d6e71",borderwidth=0,font=(textboxfonttype,(textboxfontsize)),width=textboxwidth,justify=CENTER)
	txtvoltagestep.insert(END, 'ENTER')
	txtcurrentlim = Entry(canvas)
	txtcurrentlim.configure(background="#ededee",fg="#6d6e71",borderwidth=0,font=(textboxfonttype,(textboxfontsize)),width=textboxwidth,justify=CENTER)
	txtcurrentlim.insert(END, 'ENTER')
	txtfilename = Entry(canvas)
	txtfilename.configure(background="#ededee",fg="#6d6e71",borderwidth=0,font=(textboxfonttype,(textboxfontsize)),width=textboxwidth,justify=CENTER)
	txtfilename.insert(END, 'ENTER')
	
	canvas.create_window(100,50,window = txtlowervoltage)
	canvas.create_window(250,50,window = txtuppervoltage)
	canvas.create_window(400,50,window = txtvoltagestep)
	canvas.create_window(550,50,window = txtcurrentlim)
	canvas.create_window(700,50,window = txtfilename)
	
	button1 = Button(canvas, text = "Sweep", command = clickedcommand,borderwidth=0,bg="#f04f44",fg="white",font=('futura md bt',(20)))
	button1.configure(width = 10)#, activebackground = "#33B5E5", relief = FLAT)
	button1_window = canvas.create_window(900, 275, window=button1)
	
	button2 = Button(canvas, text = "Reset", command = restart_program,borderwidth=0,bg="#d1d3d4",fg="#6d6e71",font=('futura md bt',(20)))
	button2.configure(width = 10)#, activebackground = "#33B5E5", relief = FLAT)
	button2_window = canvas.create_window(900, 200, window=button2)
	
	mylabel = canvas.create_text((100, 25), text="Start (V):",font=(labelfonttype,(labeltextsize)),justify=CENTER) 
	mylabel = canvas.create_text((250, 25), text="End (V):",font=(labelfonttype,(labeltextsize)),justify=CENTER) 
	mylabel = canvas.create_text((400, 25), text="V step (V):",font=(labelfonttype,(labeltextsize)),justify=CENTER) 
	mylabel = canvas.create_text((550, 25), text="I lim (A):",font=(labelfonttype,(labeltextsize)),justify=CENTER) 
	mylabel = canvas.create_text((700, 25), text="file name:",font=(labelfonttype,(labeltextsize)),justify=CENTER) 
	
	
	canvas.config(background='#ffffff')
	
	def printcoords(event):
	#outputting x and y coords to console
		print(event.x)
		print(event.y)
		
			
		if(event.x<630 and event.x>170 and event.y>200 and event.y<600):
			onclickax1()
			
	
	canvas.bind("<Button 1>",printcoords)
	
	root.mainloop()

draw_program()