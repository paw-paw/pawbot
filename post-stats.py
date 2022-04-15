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
    if bool_lpg:
        with open('league-query.txt', 'r') as file:
            aea = file.read()
        response = requests.get(aea)
        myjson = response.json()
        matchid = str(max(myjson['rows'], key=lambda x:x['match_id'])['match_id'])
    
    response = requests.get("https://api.opendota.com/api/matches/"+matchid)
    myjson = response.json()

    match = dict()
    match['ganador'] = myjson['radiant_win'] #True para Radiant False para Dire
    match['equipo1'] = myjson['radiant_team']['name']
    match['img1'] = myjson['radiant_team']['team_id']
    match['equipo2'] = myjson['dire_team']['name']
    match['img2'] = myjson['dire_team']['team_id']
    match['minutos'] = myjson['duration'] // 60
    match['segundos'] = myjson['duration'] % 60
    match['heroes'] = []
    match['bans'] = []
    match['picks'] = []

    for player in myjson['players']:
        hero = dict()
        hero['backpack'] = [player['backpack_0'],player['backpack_1'],player['backpack_2'],player['backpack_3']]
        hero['kills'] = player['kills']
        hero['deaths'] = player['deaths']
        hero['assists'] = player['assists']
        hero['herodmg'] = player['hero_damage']
        hero['towerdmg'] = player['tower_damage']
        hero['lasthits'] = player['last_hits']
        hero['denies'] = player['denies']
        hero['oro'] = player['total_gold']
        hero['level'] = player['level']
        hero['presenciatf'] = player['teamfight_participation']
        hero['personaname'] = player['personaname']
        hero['name'] = player['name']
        hero['id'] = player['account_id']
        hero['inv'] = [player['item_0'],player['item_1'],player['item_2'],player['item_3'],player['item_4'],player['item_5']]
        hero['hero'] = get_hero(herolist[player['hero_id']])
        match['heroes'].append(hero)


    for pickban in myjson['picks_bans']:
        if pickban['is_pick']:
            pick = dict()
            pick['hero'] = get_hero(herolist[pickban['hero_id']])
            pick['team'] = pickban['team']
            pick['order'] = pickban['order']
            match['picks'].append(pick)
        else:
            ban = dict()
            ban['hero'] = get_hero(herolist[pickban['hero_id']])
            ban['team'] = pickban['team']
            ban['order'] = pickban['order']
            match['bans'].append(ban)

    match['img1'] = get_logo(teamlist[match['img1']])
    match['img2'] = get_logo(teamlist[match['img2']])

    maxgold = max([hero['oro'] for hero in match['heroes']])

    for hero in match['heroes']:
        
        backpack = []
        for item in hero['backpack']:
            if item is None:
                continue
            backpack.append(get_item(itemlist[item]))
        hero['backpack'] = backpack
        hero['oroporc'] = hero['oro']/maxgold
        inventory = []
        for item in hero['inv']:
            if item is None:
                continue
            inventory.append(get_item(itemlist[item]))
        hero['inv'] = inventory
    
    # Carga de la plantilla

    img = Image.open('./assets/pieces/statscreen.png')
    draw = ImageDraw.Draw(img)

    # logos equipos

    temp = Image.open(match['img1'])
    temp = temp.resize((500, 500))
    img.paste(temp, (470,320),mask=temp)

    temp = Image.open(match['img2'])
    temp = temp.resize((500, 500))
    img.paste(temp, (1620,320),mask=temp)

    # Coordenadas Items
    back_y_axis_list = [392,761,1130,1498,1867,392,761,1130,1498,1867]
    back_x_axis_list = [2722,2790,2857,3635,3702,3771]

    item_y_axis_list = [290,341,659,710,1028,1079,1397,1448,1766,1817,290,341,659,710,1028,1079,1397,1448,1766,1817]
    item_x_axis_list1 = [2713, 2780, 2847]
    item_x_axis_list2 = [3625, 3692, 3759]

    hero_x_axis_list = [2762,3674]
    hero_y_axis_list = [229,598,967,1336,1705]

    banpick_x_axis_list = [3069,3342]

    ban_y_axis_list = [290,354,418,482,546,610,
                       1058,1122,1186,1250,
                       1634,1698]
    pick_y_axis_list = [674,738,866,930,
                        1378,1442,1506,1570,
                        1826,1890]

    herodmg_y_axis_list = [1003,1139,1215,1290,1366]
    towerdmg_y_axis_list = [1606,1742,1817,1893,1968]

    # total kills
    totkills = 0
    for hero in match['heroes'][0:5]:
        totkills = totkills+hero['kills']
    font = ImageFont.truetype('./assets/fonts/AvenirNext-DemiBold-03.ttf',160)
    W = 982
    H = 1858
    text = str(totkills)
    w, h = draw.textsize(text,font=font)
    draw.text((W-w/2,H-h/2), text, font=font,fill=(0,169,224,255))
    totkills = 0
    for hero in match['heroes'][5:10]:
        totkills = totkills+hero['kills']
    font = ImageFont.truetype('./assets/fonts/AvenirNext-DemiBold-03.ttf',160)
    W = 1615
    H = 1858
    text = str(totkills)
    w, h = draw.textsize(text,font=font)
    draw.text((W-w/2,H-h/2), text, font=font,fill=(0,169,224,255))

    # herodamage y kda
    sortedheroes = sorted(match['heroes'][0:5], key=lambda k: k['herodmg'],reverse=True) + sorted(match['heroes'][5:10], key=lambda k: k['herodmg'],reverse=True)
    esprimero = True

    i = 0
    for hero in sortedheroes[0:5]:
        y_axis = herodmg_y_axis_list[i]
        x_axis = 222
        temp = Image.open(hero['hero'])
        if esprimero:
            temp = temp.resize((215,124))
            font = ImageFont.truetype('./assets/fonts/AvenirNext-DemiBold-03.ttf',90)
        else:
            temp = temp.resize((122,70))
            font = ImageFont.truetype('./assets/fonts/AvenirNext-Regular-08.ttf',45)
        w,h = temp.size
        W = x_axis+w+25
        H = y_axis+3*h/7
        text = str(hero['herodmg'])
        w, h = draw.textsize(text,font=font)
        draw.text((W,H-h/2), text, font=font)
        img.paste(temp, (x_axis,y_axis))
        esprimero = False
        i = i + 1
        # KDA XDXDXDDXXDXD
        W = 850
        text = str(hero['kills'])
        w, h = draw.textsize(text,font=font)
        draw.text((W-w/2,H-h/2), text, font=font)
        
        W = 980
        text = str(hero['deaths'])
        w, h = draw.textsize(text,font=font)
        draw.text((W-w/2,H-h/2), text, font=font)
        
        W = 1110
        text = str(hero['assists'])
        w, h = draw.textsize(text,font=font)
        draw.text((W-w/2,H-h/2), text, font=font)
        
    esprimero = True
    i = 0

    for hero in sortedheroes[5:10]:
        y_axis = herodmg_y_axis_list[i]
        temp = Image.open(hero['hero'])
        if esprimero:
            x_axis = 2158
            temp = temp.resize((215,124))
            font = ImageFont.truetype('./assets/fonts/AvenirNext-DemiBold-03.ttf',90)
        else:
            x_axis = 2251
            temp = temp.resize((122,70))
            font = ImageFont.truetype('./assets/fonts/AvenirNext-Regular-08.ttf',45)
        w,h = temp.size
        W = x_axis-25
        H = y_axis+3*h/7
        text = str(hero['herodmg'])
        w, h = draw.textsize(text,font=font)
        draw.text((W-w,H-h/2), text, font=font)
        img.paste(temp, (x_axis,y_axis))
        esprimero = False
        i = i + 1
        #KDA XDDXXDDXDXXDXDXDDX
        W = 1483
        text = str(hero['kills'])
        w, h = draw.textsize(text,font=font)
        draw.text((W-w/2,H-h/2), text, font=font)
        
        W = 1613
        text = str(hero['deaths'])
        w, h = draw.textsize(text,font=font)
        draw.text((W-w/2,H-h/2), text, font=font)
        
        W = 1743
        text = str(hero['assists'])
        w, h = draw.textsize(text,font=font)
        draw.text((W-w/2,H-h/2), text, font=font)

    # towerdamage
    sortedheroes = sorted(match['heroes'][0:5], key=lambda k: k['towerdmg'],reverse=True) + sorted(match['heroes'][5:10], key=lambda k: k['towerdmg'],reverse=True)
    i = 0
    esprimero = True
    for hero in sortedheroes[0:5]:
        y_axis = towerdmg_y_axis_list[i]
        x_axis = 222
        temp = Image.open(hero['hero'])
        if esprimero:
            temp = temp.resize((215,124))
            font = ImageFont.truetype('./assets/fonts/AvenirNext-DemiBold-03.ttf',75)
        else:
            temp = temp.resize((122,70))
            font = ImageFont.truetype('./assets/fonts/AvenirNext-Regular-08.ttf',45)
        w,h = temp.size
        W = x_axis+w+25
        H = y_axis+3*h/7
        text = str(hero['towerdmg'])
        w, h = draw.textsize(text,font=font)
        draw.text((W,H-h/2), text, font=font)
        img.paste(temp, (x_axis,y_axis))
        esprimero = False
        i = i + 1
        

    i = 0
    esprimero = True
    for hero in sortedheroes[5:10]:
        y_axis = towerdmg_y_axis_list[i]
        temp = Image.open(hero['hero'])
        if esprimero:
            x_axis = 2158
            temp = temp.resize((215,124))
            font = ImageFont.truetype('./assets/fonts/AvenirNext-DemiBold-03.ttf',90)
        else:
            x_axis = 2251
            temp = temp.resize((122,70))
            font = ImageFont.truetype('./assets/fonts/AvenirNext-Regular-08.ttf',45)
        w,h = temp.size
        W = x_axis-25
        H = y_axis+3*h/7
        text = str(hero['towerdmg'])
        w, h = draw.textsize(text,font=font)
        draw.text((W-w,H-h/2), text, font=font)
        img.paste(temp, (x_axis,y_axis))
        esprimero = False
        i = i + 1

    # picks y bans equis de
    i = 0
    for ban in match['bans']:
        # ban
        y_axis = ban_y_axis_list[i]
        x_axis = banpick_x_axis_list[ban['team']]
        temp = Image.open(ban['hero']).convert('LA')
        temp = temp.resize((137,81))
        img.paste(temp, (x_axis,y_axis))
        # numerito
        multiplier = 0.5 - ban['team']
        font = ImageFont.truetype('./assets/fonts/AvenirNext-DemiBold-03.ttf',30)
        W = x_axis+68 + multiplier*95*2
        H = y_axis+40
        text = str(ban['order']+1)
        w, h = draw.textsize(text,font=font)
        draw.text((W-w/2,H-h/2), text, font=font)
        # iterador
        i = i + 1

    i = 0
    for pick in match['picks']:
        y_axis = pick_y_axis_list[i]
        x_axis = banpick_x_axis_list[pick['team']]
        temp = Image.open(pick['hero'])
        temp = temp.resize((135,80))
        img.paste(temp, (x_axis,y_axis))
        # numerito
        multiplier = 0.5 - pick['team']
        font = ImageFont.truetype('./assets/fonts/AvenirNext-DemiBold-03.ttf',30)
        W = x_axis+68 + multiplier*95*2
        H = y_axis+40
        text = str(pick['order']+1)
        w, h = draw.textsize(text,font=font)
        draw.text((W-w/2,H-h/2), text, font=font)
        # iterador
        i = i + 1

    # heroes parte derecha items oro lh y backpack

    i = -1
    black = Image.open("./assets/pieces/black.png")
    sortedheroes = sorted(match['heroes'][0:5], key=lambda k: k['oro'],reverse=True) + sorted(match['heroes'][5:10], key=lambda k: k['oro'],reverse=True)
    for hero in sortedheroes:
        i = i+1
        # hero icons y stats
        if i < 5:
            # iconos
            j = -1
            y_axis = hero_y_axis_list[i]
            x_axis = hero_x_axis_list[0]
            temp = Image.open(hero['hero'])
            temp = temp.resize((100,57))
            img.paste(temp, (x_axis,y_axis))
            # nickname
            font = ImageFont.truetype('./assets/fonts/AvenirNext-Regular-08.ttf',37)
            W = x_axis+50
            H = y_axis-30
            if str(hero['id']) in players:
                text = players[str(hero['id'])]
            else:
                if hero['name'] is not None:
                    text = hero['name']
                else:
                    text = hero['personaname']
            w, h = draw.textsize(text,font=font)
            draw.text((W-w/2,H-h/2), text, font=font)
            # oro total
            font = ImageFont.truetype('./assets/fonts/AvenirNext-Regular-08.ttf',45)
            W = x_axis+50
            H = y_axis+220
            text = str(hero['oro'])
            w, h = draw.textsize(text,font=font)
            x1 = 2713
            x2 = 2713 + 200*hero['oroporc']
            y1 = H-17
            y2 = H+28
            draw.rectangle(((x1,y1),(x1+200,y2)),fill=(80,80,80,255))
            draw.rectangle(((x1,y1),(x2,y2)),fill=(0,169,224,255))
            draw.text((W-w/2,H-h/2), text, font=font)
            # lasthits denies
            font = ImageFont.truetype('./assets/fonts/AvenirNext-Regular-08.ttf',37)
            W = x_axis+50
            H = y_axis+270
            text = 'LH/D: ' + str(hero['lasthits'])+'/'+str(hero['denies'])
            w, h = draw.textsize(text,font=font)
            draw.text((W-w/2,H-h/2), text, font=font)
        else:
            # iconos
            j = 2
            y_axis = hero_y_axis_list[i-5]
            x_axis = hero_x_axis_list[1]
            temp = Image.open(hero['hero'])
            temp = temp.resize((100,57))
            img.paste(temp, (x_axis,y_axis))
            # nickname
            font = ImageFont.truetype('./assets/fonts/AvenirNext-Regular-08.ttf',37)
            W = x_axis+50
            H = y_axis-30
            if str(hero['id']) in players:
                text = players[str(hero['id'])]
            else:
                if hero['name'] is not None:
                    text = hero['name']
                else:
                    text = hero['personaname']
            w, h = draw.textsize(text,font=font)
            draw.text((W-w/2,H-h/2), text, font=font)
            # oro total
            font = ImageFont.truetype('./assets/fonts/AvenirNext-Regular-08.ttf',45)
            W = x_axis+50
            H = y_axis+220
            text = str(hero['oro'])
            w, h = draw.textsize(text,font=font)
            x1 = 3625
            x2 = 3625 + 200*hero['oroporc']
            y1 = H-17
            y2 = H+28
            draw.rectangle(((x1,y1),(x1+200,y2)),fill=(80,80,80,255))
            draw.rectangle(((x1,y1),(x2,y2)),fill=(0,169,224,255))
            draw.text((W-w/2,H-h/2), text, font=font)
            # lasthits denies
            font = ImageFont.truetype('./assets/fonts/AvenirNext-Regular-08.ttf',37)
            W = x_axis+50
            H = y_axis+270
            text = 'LH/D: ' + str(hero['lasthits'])+'/'+str(hero['denies'])
            w, h = draw.textsize(text,font=font)
            draw.text((W-w/2,H-h/2), text, font=font)
        # backpack
        for item in hero['backpack']:
            j = j + 1
            y_axis = back_y_axis_list[i]
            x_axis = back_x_axis_list[j]
            temp = Image.open(item)
            temp = temp.resize((44, 32))
            img.paste(temp, (x_axis,y_axis))
        # inventario
        j = 0
        col = 0
        for item in hero['inv']:
            y_axis = item_y_axis_list[2*i+int(col)]
            if i < 5:
                x_axis = item_x_axis_list1[j]
            else:
                x_axis = item_x_axis_list2[j]
            temp = Image.open(item)
            temp = temp.resize((65, 49))
            img.paste(temp, (x_axis,y_axis))
            j = j + 1
            if j == 3:
                j = 0
                col = not col

    # coso victoria
    temp = Image.open('./assets/pieces/victory-resized.png')
    if match['ganador']:
        img.paste(temp,(730,240),mask=temp) # radiant
    else:
        img.paste(temp,(1880,240),mask=temp) # radiant

    #logo lpg
    temp = Image.open('./assets/pieces/movistar_lpg.png')
    img.paste(temp,(930,70),mask=temp)

    # texto duracion

    font = ImageFont.truetype('./assets/fonts/AvenirNext-Regular-08.ttf',80)
    W = 1294
    H = 500
    if match['segundos'] > 9:
        text = str(match['minutos'])+':'+str(match['segundos'])
    else:
        text = str(match['minutos'])+':'+'0'+str(match['segundos'])
    w, h = draw.textsize(text,font=font)
    draw.text((W-w/2,H-h/2), text, font=font)

    # total gold
    totgold = 0
    for hero in match['heroes'][0:5]:
        totgold = totgold+hero['oro']
    font = ImageFont.truetype('./assets/fonts/AvenirNext-Regular-08.ttf',50)
    W = 3070
    H = 2088
    text = str(totgold)
    w, h = draw.textsize(text,font=font)
    draw.text((W-w/2,H-h/2), text, font=font,fill=(0,169,224,255))
    totgold = 0
    for hero in match['heroes'][5:10]:
        totgold = totgold+hero['oro']
    font = ImageFont.truetype('./assets/fonts/AvenirNext-Regular-08.ttf',50)
    W = 3465
    H = 2088
    text = str(totgold)
    w, h = draw.textsize(text,font=font)
    draw.text((W-w/2,H-h/2), text, font=font,fill=(0,169,224,255))

    ##########
    img.show()
    img.save(folder_path.get()+'/post-stats.png')
    showinfo('Éxito','Imagen grabada en la ruta\n'+folder_path.get())
    config['POSTGAME']['LastPath'] = folder_path.get()
    with open('pawbot.ini','w') as configfile:
        config.write(configfile)
    return

def activateCheck():
    if bool_lpg.get() == 0:
        matchid_entry.config(state=tkinter.NORMAL)
        print('vacia')
    elif bool_lpg.get() == 1:
        matchid_entry.config(state=tkinter.DISABLED)
        print('llena')

def get_item(name):
    if 'recipe' in name:
        name = 'recipe'
    return './assets/items/' + name + '_png.png'

def get_hero(name):
    return './assets/heroes/' + name + '.png'

def get_logo(name):
    return './assets/logo/squared/' + name + '.png'
    
def main():

    master = tkinter.Tk()
    global folder_path
    folder_path = tkinter.StringVar()
    
    global config
    config = configparser.ConfigParser()
    config.read('pawbot.ini')
    if config['POSTGAME']['LastInsteadOfDefault']:
        folder_path.set(config['POSTGAME']['LastPath'])
    else:
        folder_path.set(config['POSTGAME']['DefaultPath'])
    
    response = requests.get("https://api.stratz.com/api/v1/Item")
    print(response.text)
    myjson = response.json()

    global itemlist
    itemlist = dict()
    for key,item in myjson.items():
        itemlist[item['id']] = item['shortName']
    itemlist[0] = 'emptyitembg'
    response = requests.get("https://api.stratz.com/api/v1/Hero")
    myjson = response.json()
    
    global herolist
    herolist = dict()
    for key,item in myjson.items():
        herolist[item['id']] = item['shortName']

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

    global players
    
    with open('players.json', 'r') as fp:
        players = json.load(fp)
    
    master.bind('<Return>',generarImagen)
    master.title("Generar Stats Postpartida")
    global bool_lpg
    bool_lpg = tkinter.BooleanVar()
    global matchid
    matchid = tkinter.StringVar()
    tkinter.Checkbutton(master, text="Buscar Ultima Partida LPG", variable=bool_lpg,command=activateCheck).grid(row=0, column=1)
    tkinter.Label(master,text='Match ID').grid(row=1,column=0)
    global matchid_entry
    matchid_entry = ttk.Entry(master,textvariable=matchid,width=30)
    matchid_entry.grid(row=1,column=1)
    tkinter.Label(master,text='Ubicación').grid(row=2,column=0)
    ttk.Entry(master,textvariable=folder_path,width=30).grid(row=2,column=1)
    tkinter.Button(text='Explorar',command=explorarRuta).grid(row=2,column=2)
    tkinter.Button(text='Generar',command=generarImagen).grid(row=3,column=1)
    tkinter.mainloop()

if __name__ == '__main__':
    main()
