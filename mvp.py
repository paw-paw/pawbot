import requests
import pandas as pd
import numpy as np
import configparser
import tkinter
import tkinter.filedialog
import PIL
import json
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from tkinter import ttk
from tkinter.messagebox import showinfo


def explorarRuta():
	filename = tkinter.filedialog.askdirectory()
	folder_path.set(filename)
	if folder_path.get() == '':
		folder_path.set('./')
	print(filename)

def generarImagen(event=None):
    if bool_lpg.get():
        with open('league-query.txt', 'r') as file:
            aea = file.read()
        response = requests.get(aea)
        myjson = response.json()
        matchid = str(max(myjson['rows'], key=lambda x:x['match_id'])['match_id'])
    else:
        matchid = matchid_var.get()
    response = requests.get("https://api.opendota.com/api/matches/"+matchid)
    myjson = response.json()
    saltar = False
    i = 0
    for player in myjson['players']:
        
        # cargar imagen xd
        text = 'testeo'
        if str(player['account_id']) in players:
            text = players[str(player['account_id'])].upper()
        else:
            if player['name'] is not None:
                text = player['name'].upper()
            else:
                text = player['personaname'].upper()
        heroname = herolist[player['hero_id']]
        # cargar artwork
        img = Image.open(get_hero(heroname)).resize((1920, 1080))
        draw = ImageDraw.Draw(img)
        # cargar plantilla
        temp = Image.open('./assets/pieces/mvp-overlay.png')
        img.paste(temp,(0,0),mask=temp)
        # logo
        if i < 5:
            temp = Image.open('./assets/logo/squared/'+teamlist[myjson['radiant_team']['team_id']]+'.png')
        else:
            temp = Image.open('./assets/logo/squared/'+teamlist[myjson['dire_team']['team_id']]+'.png')
        temp = temp.resize((375, 375))
        W = 1650
        H = 725
        w, h = temp.size
        img.paste(temp,(int(W-w/2),int(H-h/2)),mask=temp)
        
        # texto
        font = ImageFont.truetype('./assets/fonts/AvenirNext-DemiBold-03.ttf',100)
        W = 1650
        H = 975
        w, h = draw.textsize(text,font=font)
        draw.text((W-w/2,H-h/2), text, font=font)
        print('miau')
        img.save(folder_path.get()+'/mvp_'+heroname+'.png')
        i = i+1
    showinfo('Éxito','Imágenes grabadas en la ruta\n'+folder_path.get())
    config['MVP']['LastPath'] = folder_path.get()
    with open('./pawbot.ini','w') as configfile:
        config.write(configfile)
    return
    
    

def activateCheck():
    if bool_lpg.get() == 0:
        matchid_entry.config(state=tkinter.NORMAL)
        print('vacia')
    elif bool_lpg.get() == 1:
        matchid_entry.config(state=tkinter.DISABLED)
        print('llena')

def get_hero(name):
    return './assets/heroes_wallpaper/' + name + '.jpg'
    
def main():

    master = tkinter.Tk()
    global folder_path
    folder_path = tkinter.StringVar()
    
    global config
    config = configparser.ConfigParser()
    config.read('pawbot.ini')
    if config['MVP']['LastInsteadOfDefault']:
        folder_path.set(config['MVP']['LastPath'])
    else:
        folder_path.set(config['MVP']['DefaultPath'])

    response = requests.get("https://api.stratz.com/api/v1/Hero")
    myjson = response.json()
    
    global herolist
    herolist = dict()
    for key,item in myjson.items():
        herolist[item['id']] = item['shortName']

    global players
    
    with open('players.json', 'r') as fp:
        players = json.load(fp)
    
    global teamlist
    teamlist = dict()
    teamlist[7121518] = 'Unknown Team'
    teamlist[7640799] = 'Cream Esports Blanco'
    teamlist[5992560] = 'Infamous Young'
    teamlist[6382242] = 'Thunder Predator'
    teamlist[6266565] = '0-900'
    teamlist[2672298] = 'Infamous'
    teamlist[5229568] = 'Vicious Gaming'
    teamlist[7119077] = 'Egoboys'
    teamlist[7310385] = 'Luxor Gaming'
    teamlist[5055770] = 'G-Pride'
    
    master.bind('<Return>',generarImagen)
    master.title("Generar Pantallas MVP")
    global bool_lpg
    bool_lpg = tkinter.BooleanVar()
    global matchid_var
    matchid_var = tkinter.StringVar()
    tkinter.Checkbutton(master, text="Buscar Ultima Partida LPG", variable=bool_lpg,command=activateCheck).grid(row=0, column=1)
    tkinter.Label(master,text='Match ID').grid(row=1,column=0)
    matchid_entry = ttk.Entry(master,textvariable=matchid_var,width=30)
    matchid_entry.grid(row=1,column=1)
    tkinter.Label(master,text='Ubicación').grid(row=2,column=0)
    ttk.Entry(master,textvariable=folder_path,width=30).grid(row=2,column=1)
    tkinter.Button(text='Explorar',command=explorarRuta).grid(row=2,column=2)
    tkinter.Button(text='Generar',command=generarImagen).grid(row=3,column=1)
    tkinter.mainloop()

if __name__ == '__main__':
    main()
