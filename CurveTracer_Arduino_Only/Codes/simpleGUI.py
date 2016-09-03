import Tkinter
import tkMessageBox
import serial
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
import types
import time 
import glob
import sys

from matplotlib.ticker import MultipleLocator, FormatStrFormatter

#Search for available serial ports
def serial_ports():
    """ Lists serial port names
        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result

PORT = []    
def detectCOM() :
    ports = serial_ports()
    '''result = None
    tkMessageBox.showinfo("Message","REMOVE the device")
    for i in ports :
        try :
            ser = serial.Serial(i)
            ser.close()
        except (OSError, serial.SerialException) :
            result = i
            pass
    tkMessageBox.showinfo("Message","CONNECT the device")'''
    PORT.append(ports[0])
        
#scatter plot mod
def show_plot(arg1, arg2=None):
    def real_decorator(f):
        def wrapper(*args, **kwargs):
            plt.figure(figsize=(arg1, arg2))
            result = f(*args, **kwargs)
            plt.show()
            return result
        return wrapper

    if type(arg1) == types.FunctionType:
        f = arg1
        arg1, arg2 = 0, 0
        return real_decorator(f)
    return real_decorator

max_read = 1023.0 #max read of ADC
vref = 1.1 #VRef ADC

#voltage divider 1/11
def mulx(n) :
    return 11.0*n

#I.10 = n
def muly(n) :
    return n/10.0
    
#adc value to analog
def AnalogValue(n) :
    return vref*(n/max_read) 

#moving average
def avg(n) :
    t = 0.0
    for i in range(248) :
        for j in range(8) :
            t += n[i+j]
        n[i] = t/8.0
        t = 0.0
    return n

#Values of Ib
Ib = ['','','0.058','0.117','0.175','0.233','0.292','0.350']

cx = []
cy = []
dev_id = None

def mil(n) :
    return 1000*n


def plot(dev_id,dev_ter) :
    #Plotting Curves
    fig = plt.figure()
    pl = fig.add_subplot(111)
    
    colors = [x for x in cm.rainbow(np.linspace(0, 1, 8))] #color
    
    mkr = 5 #markersize
    
    #Setting ticks
    '''majorLocator = MultipleLocator(5)
    majorFormatter = FormatStrFormatter('%d')
    minorLocatorY = MultipleLocator(1)
    minorLocatorX = MultipleLocator(0.1)'''
    
    #plotting curves
    if dev_ter == '3' :
        #8 curves for 3 terminal DUT
        for i in range(8) :
            #cy[i] = map(mil,cy[i])
            pl.scatter(cx[i], cy[i], color = colors[i], s = mkr)
            pl.plot(cx[i],cy[i],color = colors[i],label = r'$ \bf{I_b =}$'+Ib[i])
        #Axis Label            
        pl.set_ylabel(r'$ \bf{I_c (A)} $',fontsize = 18)
        pl.set_xlabel(r'$ \bf{V_{be} (V)} $',fontsize = 18)
    else :
        #Averaging all 8 curves to get 1 curve for 1t DUT
        x = []
        y = []
        t1 = 0.0
        t2 = 0.0
        for j in range(256) :
            for i in range(8) :
                t1 += cx[i][j]
                t2 += cy[i][j]
            x.append(t1/8.0)
            y.append(t2/8.0)
            t1 = 0.0
            t2 = 0.0
        
        y = map(mil,y)
        pl.scatter(x, y, s = mkr*2)
        pl.plot(x,y)
        #Axis Label            
        pl.set_ylabel(r'$ \bf{I (mA)} $',fontsize = 18)
        pl.set_xlabel(r'$ \bf{V (V)} $',fontsize = 18)
        
    #Adding ticks
    '''pl.yaxis.set_major_locator(majorLocator)
    pl.yaxis.set_major_formatter(majorFormatter)
    pl.yaxis.set_minor_locator(minorLocatorY)
    pl.xaxis.set_minor_locator(minorLocatorX)'''
    
    #grid and title
    pl.grid(True)
    pl.set_title(dev_id, fontsize = 24)
    tkMessageBox.showinfo("Message","Done Plotting")
    plt.show()
    
def SCT():
    
    #Getting Device Id
    dev_id = textfield1.get()
    dev_ter = textfield2.get()
    
    #PORT = detectCOM()#Detecting COM port
    #temp = len(PORT)
    ser = serial.Serial(port = PORT[0] ,
        baudrate = 115200)
    
    time.sleep(1.5)
    ser.flush()
    
    x = []
    y = []
    sep = []
        
    ser.write(dev_ter)
    data = ser.readline()
    sep = data.split()
    del data      
    
    ser.close()
    
    m = 0
    n = 1
    
    #Seperating X and Y
    for i in range(len(sep)//2) :
        x.append(abs(float(sep[m])))
        y.append((float(sep[n])))
        m += 2
        n += 2
        
    del sep
    
    #ADC to analog
    r_x = map(AnalogValue,x)
    r_y = map(AnalogValue,y)
    
    x = []
    y = []
    
    #Real Analog (Voltage Divider and 10I)
    r_x = map(mulx,r_x)
    r_y = map(muly,r_y)
    
    #Seperating the 8 curves
    for i in range(0,len(r_x),256) :
        cx.append(r_x[i:i+256])
        cy.append(r_y[i:i+256])
    
    r_x = []
    r_y = []    
     
    #Averaging
    for j in range(12) :
        for i in range(8) :
            cx[i] = avg(cx[i])
            cy[i] = avg(cy[i])

    #Forcing (0,0)
    for i in range(8) :
        cx[i][255] = 0.0
        cy[i][255] = 0.0
        

    
    #plotting
    plot(dev_id,dev_ter)


tk=Tkinter.Tk()

frame_a= Tkinter.Frame(tk,relief='groove', borderwidth=5)
label0=Tkinter.Label(frame_a,text="Semiconductor Curve Tracer",relief='ridge',font=100,fg='red',bg='black',width=50)  
label1=Tkinter.Label(frame_a,text="Name of Device under Test(DUT)",font=70)
label2=Tkinter.Label(frame_a,text="No. of terminals of (DUT)",font=70)

textfield1=Tkinter.Entry(frame_a,width=50)
textfield2=Tkinter.Entry(frame_a,width=50)
Button1=Tkinter.Button(frame_a,text="Start",command=SCT,font=100,fg='red',bg='black',width=10)
Button2=Tkinter.Button(frame_a,text="Detect COM PORT",command=detectCOM,font=100,fg='red',bg='black',width=20)

label0.pack()
label1.pack()
textfield1.pack()
label2.pack()
textfield2.pack()
Button1.pack()
Button2.pack()
frame_a.pack(side='left',fill='both',expand=1)

tk.mainloop()
