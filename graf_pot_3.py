# hello_world.py

from pathlib import Path
import PySimpleGUI as sg
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit,basinhopping
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

v0=10

def DeltaV(XY,b,r1,r2,alfa):
    xp=XY[:,0]*1e-2
    yp=XY[:,1]*1e-2
    V1=V0/((xp+b)**2 +(yp)**2)**r1
    V2=V0/((xp-b)**2 +(yp)**2)**r2
    Veff=alfa*(V2-V1)
    return Veff

def graf(Mxy,xp,yp,Vp,Vexp,val):
    fig1, ax = plt.subplots()
    
    Ey,Ex=np.gradient(-Vp)
    # Ex=Ex/np.hypot(Ex,Ey)
    # Ey=Ey/np.hypot(Ex,Ey)
    x,y=np.meshgrid(xp,yp)
    x=x[::20,::20]
    y=y[::20,::20]
    Ex=Ex[::20,::20]
    Ey=Ey[::20,::20]
    ax.quiver(x,y,Ex,Ey)
    
    CS = ax.contour(xp,yp,Vp, 5, colors='r',
                    levels=[Vexp[0],Vexp[1],0,Vexp[2],Vexp[3]])# Negative contours default to dashed.
    ax.clabel(CS,inline=True, fontsize=10)
    
    lab1=np.array_str(val,precision = 4, suppress_small = True)
    labels = [lab1]
    for i in range(len(labels)):
      CS.collections[i].set_label(labels[i])
      
    plt.scatter(Mxy[:,0],Mxy[:,1])
    plt.legend(loc='upper center',bbox_to_anchor=(0.5,1.1))
    plt.xlabel('x (cm)')
    plt.ylabel('y (cm)')
    figure_x, figure_y, figure_w, figure_h = fig1.bbox.bounds
#    print('h=',int(figure_h))
    return (fig1,figure_x, figure_y, figure_w, figure_h)

def draw_figure(canvas, figure, loc=(0, 0)):
        figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
        figure_canvas_agg.draw()
        figure_canvas_agg.get_tk_widget().pack(side='top',
                                               fill='both',
                                               expand=1)
        return figure_canvas_agg

def delete_fig_agg(fig_agg):
    fig_agg.get_tk_widget().forget()
    plt.close('all')



def popup_text(filename, text):

    layout = [
        [sg.Multiline(text, size=(80, 25)),],
    ]
    win = sg.Window(filename, layout, modal=True, finalize=True)

    while True:
        event, values = win.read()
        if event == sg.WINDOW_CLOSED:
            break
    win.close()

sg.theme("GreenMono")
sg.set_options(font=("Microsoft JhengHei", 16))



layout = [
    [
        sg.Input(key='-INPUT-'),
        sg.FileBrowse(file_types=(("TXT Files", "*.txt"),
                                  ("ALL Files", "*.*"))),
        sg.Button("Open"),
    ],
    [sg.T('Voltage', key='lbl_V',font='consalo 14'), 
     sg.I('', key='edit_V', size=(10,1),pad=(10,10))],
     [sg.T('exp. p1', key='lbl_p1', font='consalo 14'), 
      sg.I('', key='edit_p1', size=(10,1),pad=(10,20)),
      sg.T('OPT p1='),sg.T('',size=(0, 1),key='OUTPUTR1',background_color='white')
      ],
     [sg.T('exp. p2', key='lbl_p2', font='consalo 14'),
      sg.I('', key='edit_p2', size=(10,1),pad=(10,10)),
      sg.T('OPT p2='),sg.T('',size=(0, 1),key='OUTPUTR2',background_color='white')
      ],
     [sg.T('b', key='lbl_b', font='consalo 14'), 
      sg.I('', key='edit_b', size=(10,1),pad=(10,10)),
      sg.T('OPT b='),sg.T('',size=(0, 1),key='OUTPUTR3',background_color='white')
      ],
     [sg.T('a', key='lbl_a', font='consalo 14'), 
      sg.I('', key='edit_a', size=(10,1),pad=(10,10)),
      sg.T('OPT a='),sg.T('',size=(0, 1),key='OUTPUTR4',background_color='white')
      ],
     [sg.Button('Graphic',enable_events=True, key='-GRAFICA-', 
                font='Helvetica 16'),
      sg.Button('Exit',font='Helvetica 16')
      ],[sg.Canvas(size=(300,300), key='-CANVAS-', pad=(15,15))],
     [sg.T('created by Carlos L. Beltrán Ríos, cbeltran@uis.edu.co',key='author',font='consalo 10')],
]

window = sg.Window('lineas equipotenciales', layout)
fig_agg = None

while True:
    event, values = window.read()
    if event in (None, 'Exit'):
        break
    if event == sg.WINDOW_CLOSED:
        break
    elif event == 'Open':
        filename = values['-INPUT-']
        if Path(filename).is_file():
            try:
                with open(filename, "r", encoding='utf-8') as f:
                    text = f.read()
                                       
                popup_text(filename, text)
                
            except Exception as e:
                print("Error: ", e)
    dataname = Path(filename).name 
    if event == '-GRAFICA-':
                    
                    V0 = float(values['edit_V'])
              
                    r1 = float(values['edit_p1'])

                
                    r2=float(values['edit_p2'])

                
                    b=float(values['edit_b'])
                    
                    a=float(values['edit_a'])
                    
                    data=np.loadtxt(dataname)
                
                    V=data[:,0]
                    XY=data[0:4,1:9]
                    XY=XY.reshape(16,2)
                    Vz=np.zeros(16)
                    Vz[:4]=V[0]
                    Vz[4:8]=V[1]
                    Vz[8:12]=V[2]
                    Vz[12:17]=V[3]
                    p_ini=[b,r1,r2,a]
                    best_val,cov=curve_fit(DeltaV,XY,Vz,p0=p_ini,method='trf')
                    
                    b=best_val[0]
                    r1=best_val[1]
                    r2=best_val[2]
                    a=best_val[3]
                    print('err=',np.sqrt(np.diag(cov)))
                    window['OUTPUTR1'].update(value=r1)
                    window['OUTPUTR2'].update(value=r2)
                    window['OUTPUTR3'].update(value=b)
                    window['OUTPUTR4'].update(value=a)
                    
                    xp=np.linspace(min(XY[:,0]-1),max(XY[:,0]+1),200)
                    yp=np.linspace(min(XY[:,1]-1),max(XY[:,1]+1),200)

                    Vp=np.zeros((len(xp),len(yp)))
                    for j in range(len(xp)):
                        for i in range(len(yp)):
                            V2n=V0/((xp[j]*1e-2-b)**2 +(yp[i]*1e-2)**2)**r2
                            V1n=V0/((xp[j]*1e-2+b)**2 +(yp[i]*1e-2)**2)**r1
                            Vp[i,j]=a*(V2n-V1n)

                    if fig_agg is not None:
                         delete_fig_agg(fig_agg) 
                    fig1,figure_x, figure_y,figure_w, figure_h = graf(XY,xp,yp,Vp,V,best_val)
                  
                    canvas_elem = window['-CANVAS-'].TKCanvas
                    canvas_elem.Size=(int(figure_w),int(figure_h))
                    fig_agg = draw_figure(canvas_elem, fig1)
                    
window.close()

