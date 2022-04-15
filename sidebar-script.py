import requests
import pandas as pd
import numpy as np
import configparser
from selenium.common.exceptions import NoSuchElementException
import tkinter
import tkinter.filedialog
from selenium.webdriver import Chrome
import PIL
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from tkinter import ttk
from tkinter.messagebox import showinfo

def find_key(dic, val):
    return [k for k, v in dic.items() if v == val][0]
    
def explorarRuta():
    filename = tkinter.filedialog.askdirectory()
    folder_path.set(filename)
    if folder_path.get() == '':
        folder_path.set('./')
    print(filename)
    

def generarImagen(event=None):
    img = Image.open('./assets/pieces/base_sidebar.png')
    
    heroid = find_key(namelist,myname.get())
    temp = Image.open('./assets/heroes/' + herolist[heroid] + '.png')
    temp = temp.resize((218,119))
    img.paste(temp, (1685,365))
    
    picked = str(dblist[heroid]['picks'])
    banned = str(dblist[heroid]['bans'])
    winrate = '{0:.2f}'.format((dblist[heroid]['wins']/dblist[heroid]['picks'])*100)+'%'

    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype('./assets/fonts/AvenirNext-DemiBold-03.ttf',30)
    W = 1708
    H = 490
    w, h = draw.textsize('WINRATE')
    draw.text((W+w/2,H+h/2), 'WINRATE', font=font)
    
    W = 1800
    H = 553
    font = ImageFont.truetype('./assets/fonts/AvenirNext-DemiBold-03.ttf',55)
    w, h = draw.textsize(winrate,font=font)
    draw.text((W-w/2,H-h/2),winrate,font=font)
    
    W = 1708
    H = 574
    font = ImageFont.truetype('./assets/fonts/AvenirNext-DemiBold-03.ttf',25)
    w, h = draw.textsize('PICKED',font=font)
    draw.text((W+w/2,H+h/2),'PICKED',font=font)
    
    W = 1798
    H = 632
    font = ImageFont.truetype('./assets/fonts/AvenirNext-DemiBold-03.ttf',43)
    w, h = draw.textsize(picked,font=font)
    draw.text((W-w/2,H-h/2),picked,font=font)
    
    W = 1688
    H = 648
    font = ImageFont.truetype('./assets/fonts/AvenirNext-DemiBold-03.ttf',25)
    w, h = draw.textsize('BANNED',font=font)
    draw.text((W+w/2,H+h/2),'BANNED',font=font)
    
    W = 1798
    H = 706
    font = ImageFont.truetype('./assets/fonts/AvenirNext-DemiBold-03.ttf',43)
    w, h = draw.textsize(banned,font=font)
    draw.text((W-w/2,H-h/2),banned,font=font)

    img.save(folder_path.get()+'/sidebar.png')
    showinfo('Éxito','Imagen grabada en la ruta\n'+folder_path.get())
    config['SIDEBAR']['LastPath'] = folder_path.get()
    with open('pawbot.ini','w') as configfile:
        config.write(configfile)
    return

def main():

    master = tkinter.Tk()
    global folder_path
    folder_path = tkinter.StringVar()
    
    global config
    config = configparser.ConfigParser()
    config.read('pawbot.ini')
    if config['SIDEBAR']['LastInsteadOfDefault']:
        folder_path.set(config['SIDEBAR']['LastPath'])
    else:
        folder_path.set(config['SIDEBAR']['DefaultPath'])

    db = []

    response = requests.get("https://api.stratz.com/api/v1/Hero")
    json = response.json()

    global herolist
    herolist = dict()
    for key,item in json.items():
        herolist[item['id']] = item['shortName']

    response = requests.get('https://api.opendota.com/api/heroStats')
    json = response.json()

    for elem in json:
        temp = dict()
        temp['id'] = elem['hero_id']
        temp['name'] = elem['name']
        temp['fullname'] = elem['localized_name']
        temp['active'] = elem['cm_enabled']
        temp['bans'] = elem['pro_ban']
        temp['wins'] = elem['pro_win']
        temp['picks'] = elem['pro_pick']
        db.append(temp)

    names = []
    for elem in db:
        names.append(elem['fullname'])
    ids = []
    for elem in db:
        ids.append(elem['id'])
    global namelist
    namelist = dict(zip(ids,names))
    global dblist
    dblist = dict(zip(ids,db))
    global myname
    myname = tkinter.StringVar()

    del response
    del json

    master.bind('<Return>',generarImagen)

    master.title("Generar Stats Stream")
    tkinter.Label(master,text='Elige el héroe').grid(row=1,column=0)
    tkinter.Label(master,text='Ubicación').grid(row=2,column=0)
    ttk.Entry(master,textvariable=folder_path,width=30).grid(row=2,column=1)
    tkinter.Button(text='Explorar',command=explorarRuta).grid(row=2,column=2)
    tkinter.Button(text='Generar',command=generarImagen).grid(row=3,column=1)

    combobox = ttk.Combobox(master,height=20,width=28,textvariable = myname,state='readonly')
    combobox.grid(row=1,column=1)
    names.sort()
    combobox['values'] = names
    combobox.current(0)

    tkinter.mainloop()

if __name__ == '__main__':
    main()