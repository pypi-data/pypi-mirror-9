import sys

if not('.' in sys.path): sys.path.append('.')
import math

from Tkinter import *
from tkFileDialog import *
from tkSimpleDialog import askstring
import math

# thinking in tkinter http://www.ferg.org/thinking_in_tkinter/all_programs.html

class TheGui:
    def __init__(self, parent):
       
        #------- frmIn ----------#
        # http://effbot.org/tkinterbook/tkinter-widget-styling.htm
        self.frmOut = Frame(parent, bd=5)
        self.frmOut.pack()

        self.lblS = Label(self.frmOut, text='Occupation point[grid coords]', bg = 'red', width=450)
        self.lblS.pack() 

        self.xs = Label(self.frmOut, text='x:', width=2)
        self.xs.pack(side=LEFT)
        self.xs = StringVar() # coord x of occupation point
        self.entSx = Entry(self.frmOut, width=20, textvariable=self.xs)
        self.xs.set('6020279.50')
        self.entSx.pack(side=LEFT)

        self.ys = Label(self.frmOut, text='y:', width=2)
        self.ys.pack(side=LEFT)
        self.ys = StringVar() # coord y of occupation point
        self.entSy = Entry(self.frmOut, width=20, textvariable=self.ys)
        self.entSy.pack(side=LEFT)
        self.ys.set('6430432.70')

        

   ###########################################################################################     
        self.frmOut = Frame(parent, bd=5)
        self.frmOut.pack()

        self.lblOut = Label(self.frmOut, text='Base point[grid coords]', bg = 'red', width=450)
        self.lblOut.pack() 

        self.xa = Label(self.frmOut, text='x:', width=2)
        self.xa.pack(side=LEFT)
        self.xa = StringVar() # coord x of base point
        self.entIn = Entry(self.frmOut, width=20, textvariable=self.xa)
        self.entIn.pack(side=LEFT)
        self.xa.set('6020273.90')

        self.ya = Label(self.frmOut, text='y:', width=2)
        self.ya.pack(side=LEFT)
        self.ya = StringVar() # coord y of base point
        self.entIn = Entry(self.frmOut, width=20, textvariable=self.ya)
        self.entIn.pack(side=LEFT)
        self.ya.set('6430341.40')



##################################################################################################
        self.frmOut = Frame(parent, bd=5)
        self.frmOut.pack()

        self.lblOut = Label(self.frmOut, text='Control point[grid coords]', bg = 'red', width=450)
        self.lblOut.pack() 

        self.xb = Label(self.frmOut, text='x:', width=2)
        self.xb.pack(side=LEFT)
        self.xb = StringVar() # coord x of control point
        self.entIn = Entry(self.frmOut, width=20, textvariable=self.xb)
        self.entIn.pack(side=LEFT)
        self.xb.set('6020296.10')

        self.yb = Label(self.frmOut, text='y:', width=2)
        self.yb.pack(side=LEFT)
        self.yb = StringVar() # coord y of control point
        self.entIn = Entry(self.frmOut, width=20, textvariable=self.yb)
        self.entIn.pack(side=LEFT)
        self.yb.set('6430482.80')
        
        
############################################################################
        self.frmOut = Frame(parent, bd=5)
        self.frmOut.pack()
        
        
        self.AngleSA = Label(self.frmOut, text='Base point angle[gons]:', width=20)
        self.AngleSA.pack(side=LEFT)
        self.AngleSA = StringVar()
        self.entIn = Entry(self.frmOut, width=20, textvariable=self.AngleSA)
        self.entIn.pack(side=LEFT)
        self.AngleSA.set('0.0000')


        self.frmOut = Frame(parent, bd=5)
        self.frmOut.pack()
        
        
        
        self.AngleSB = Label(self.frmOut, text='Control point angle[gons]:', width=20)
        self.AngleSB.pack(side=LEFT)
        self.AngleSB = StringVar()
        self.entIn = Entry(self.frmOut, width=20, textvariable=self.AngleSB)
        self.entIn.pack(side=LEFT)
        self.AngleSB.set('183.5311')


        self.frmOut = Frame(parent, bd=5)
        self.frmOut.pack()
        
        
        
        self.AngleSP = Label(self.frmOut, text='Calculated point angle[gons]', width=20)
        self.AngleSP.pack(side=LEFT)
        self.AngleSP = StringVar()
        self.entIn = Entry(self.frmOut, width=20, textvariable=self.AngleSP)
        self.entIn.pack(side=LEFT)
        self.AngleSP.set('91.2643')


        self.frmOut = Frame(parent, bd=5)
        self.frmOut.pack()             
        
        self.dSP = Label(self.frmOut, text='Horizontal distance[m]:', width=20)
        self.dSP.pack(side=LEFT)
        self.dSP = StringVar()
        self.entIn = Entry(self.frmOut, width=20, text='x', textvariable=self.dSP)
        self.entIn.pack(side=LEFT)
        self.dSP.set('54.26')
        


        
        
        #------- frmButtons ----------#
        self.frmOut = Frame(parent, bd=5)
        self.frmOut.pack()
        
        self.btnConvert = Button(self.frmOut, 
            text='Calculate', command=self.btnConvertClick)
        self.btnConvert.pack()
        

        self.frmOut = Frame(parent, bd=5)
        self.frmOut.pack()

        self.lblOut = Label(self.frmOut, text='Calculated point coordinates',bg = 'red', width=450)
        self.lblOut.pack() 

        self.xp = Label(self.frmOut, text='x:', width=2)
        self.xp.pack(side=LEFT)
        self.xp = StringVar()
        self.entIn = Entry(self.frmOut, width=20, textvariable=self.xp)
        self.entIn.pack(side=LEFT)

        self.yp = Label(self.frmOut, text='y:', width=2)
        self.yp.pack(side=LEFT)
        self.yp = StringVar()
        self.entIn = Entry(self.frmOut, width=20, textvariable=self.yp)
        self.entIn.pack(side=LEFT)
  
    #------- handle commands ----------#
            
    def btnConvertClick(self):
        xs = float(self.xs.get())
        ys = float(self.ys.get())

        xa = float(self.xa.get())
        ya = float(self.ya.get())

        xb = float(self.xb.get())
        yb = float(self.yb.get())


        ka = float(self.AngleSA.get())
        kb = float(self.AngleSB.get())
        kp = float(self.AngleSP.get())

        dsp = float(self.dSP.get())

        pi = math.pi

        dx = xa - xs
        dy = ya - ys

        bdx = xb - xs
        bdy = yb - ys

        n = dy/dx# in radians

        if dy ==0:
            if dy>0:
                A1 = pi/2
            else:
                A1 = 1.5 * pi
        else:
            A1 = math.atan(dy/dx)
            if dx < 0:
                A1 = A1 + pi
            elif dy < 0:
                A1 = A1 + 2 * pi

        dd = A1 *200/pi

        if bdy ==0:
            if bdy>0:
                A2 = pi/2
            else:
                A2 = 1.5 * pi
        else:
            A2 = math.atan(bdy/bdx)
            if bdx < 0:
                A2 = A2 + pi
            elif bdy < 0:
                A2 = A2 + 2 * pi
        ss = A2 *200/pi

        y1 = (A1 * 200/pi) - ka
        y2 = (A2 * 200/pi) - kb
        if y2 < 0:
            y2 = y2 +400
    

        Y = (y1 + y2)/2

        A3 = (Y + kp)
        aa = A3 * pi/200.0

        xp = xs + dsp * math.cos(aa)
        yp = ys + dsp * math.sin(aa)

        print xp, yp

        self.xp.set(str(xp))
        self.yp.set(str(yp))
        
        
 
  
root = Tk()
root.title("Obliczenia biegunowe v.0.2")
#http://infohost.nmt.edu/tcc/help/pubs/tkinter/std-attrs.html#geometry
#http://infohost.nmt.edu/tcc/help/pubs/tkinter/toplevel.html
root.geometry("450x500+10+10")
gui = TheGui(root)
root.mainloop()
