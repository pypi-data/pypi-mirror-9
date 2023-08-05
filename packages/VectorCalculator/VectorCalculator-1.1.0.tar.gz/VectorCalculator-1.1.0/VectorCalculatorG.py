'''This is a graphical calculator for vectors
author: Noah Rossignol
date:1/1/2014'''

from Vector import *
from Tkinter import *
import tkMessageBox

top=Tk()
top.title("Vector Calculator")

'''There will be three frames packed into the screen.  The top frame will
obtain the information about the vectors, while the middle frame will
be where the user chooses which operation to perform.  The bottom frame
will display the result'''
#first make the top frame

frame1=Frame(top)
#make the first round of labels
x1label=Label(frame1, text="x1")
x1label.grid(row=0, column=0)
y1label=Label(frame1, text="y1")
y1label.grid(row=1, column=0)
z1label=Label(frame1, text="z1")
z1label.grid(row=2, column=0)
#make the entry boxes
getx1=Entry(frame1)
getx1.grid(row=0, column=1)
gety1=Entry(frame1)
gety1.grid(row=1, column=1)
getz1=Entry(frame1)
getz1.grid(row=2, column=1)
#make the second round of labels
x2label=Label(frame1, text="x2")
x2label.grid(row=0, column=2)
y2label=Label(frame1, text="y2")
y2label.grid(row=1, column=2)
z2label=Label(frame1, text="z2")
z2label.grid(row=2, column=2)
#make the second set of entry boxes
getx2=Entry(frame1)
getx2.grid(row=0, column=3)
gety2=Entry(frame1)
gety2.grid(row=1, column=3)
getz2=Entry(frame1)
getz2.grid(row=2, column=3)
#pack the frame
frame1.pack()

#I need to make functions for the buttons to call
#I first need to be able to update the result
def updater(s1):
	resultP.delete("1.0",END)
	resultP.insert("1.0",s1)
def adder():
	try:
		v1=Vector(float(getx1.get()), float(gety1.get()), float(getz1.get()))
		v2=Vector(float(getx2.get()), float(gety2.get()), float(getz2.get()))
		v3=v1.add(v2)
		updater(v3.__str__())
	except ValueError:
		tkMessageBox.showinfo(title="Error", message="Important fields are empty")
def subtracter():
	try:
		v1=Vector(float(getx1.get()), float(gety1.get()), float(getz1.get()))
		v2=Vector(float(getx2.get()), float(gety2.get()), float(getz2.get()))
		v3=v1.add(v2.scalarProduct(-1))
		updater(v3.__str__())
	except ValueError:
		tkMessageBox.showinfo(title="Error", message="Important fields are empty")
def multiplier():
	try:
		v1=Vector(float(getx1.get()), float(gety1.get()), float(getz1.get()))
		scalarFrame=Toplevel()
		scalarLabel=Label(scalarFrame,text="Enter the scalar to multiply v1 by")
		scalarLabel.pack()
		scalarEntry=Entry(scalarFrame, width=10)
		scalarEntry.pack()
		def getScalar():
			try:
				v3=v1.scalarProduct(float(scalarEntry.get()))
				updater(v3.__str__())
				scalarFrame.withdraw()
			except:
				tkMessageBox.showinfo(title="Error", message="Enter a valid decimal number")
		scalarButton=Button(scalarFrame, text="OK", command=getScalar)
		scalarButton.pack()
	except ValueError:
		tkMessageBox.showinfo(title="Error", message="Important fields are empty")
def dotter():
	try:
		v1=Vector(float(getx1.get()), float(gety1.get()), float(getz1.get()))
		v2=Vector(float(getx2.get()), float(gety2.get()), float(getz2.get()))
		v3=v1.dotProduct(v2)
		updater(v3.__str__())
	except ValueError:
		tkMessageBox.showinfo(title="Error", message="Important fields are empty")
def getCrossProduct():
	try:
		v1=Vector(float(getx1.get()), float(gety1.get()), float(getz1.get()))
		v2=Vector(float(getx2.get()), float(gety2.get()), float(getz2.get()))
		v3=v1.crossProduct(v2)
		updater(v3.__str__())
	except ValueError:
		tkMessageBox.showinfo(title="Error", message="Important fields are empty")
#Now frame 2: The options
frame2=Frame(top)
#This will take a bunch of buttons
B1=Button(frame2, text="Add", command=adder)
B1.grid(row=0, column=0, sticky="NESW")

B2=Button(frame2, text="Subtract", command=subtracter)
B2.grid(row=0, column=1, sticky="NESW")

B3=Button(frame2, text="Scalar Product", command=multiplier)
B3.grid(row=1, column=0, sticky="NESW")

B4=Button(frame2, text="Dot Product", command=dotter)
B4.grid(row=1, column=1, sticky="NESW")

B5=Button(frame2, text="Cross Product", command=getCrossProduct)
B5.grid(row=2, columnspan=2, sticky="NESW")

frame2.pack()
#Frame 3 will display the result
frame3=Frame(top)

resultL=Label(frame3,text="Result")
resultP=Text(frame3, height=1, width=25)
resultL.pack(side=LEFT)
resultP.pack(side=RIGHT)

frame3.pack()
top.mainloop()
