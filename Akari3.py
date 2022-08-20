from math import *
from random import *
from functools import *
from AkariDB import stacks, mceil, perc
import discord
from discord.ext import commands, tasks
import sqlite3
import os
import re
import AkariDB as adb
import io
import ast
import asyncio
import time
import math
import random
import requests
from collections import Counter, defaultdict
import shutil
import datetime
import vk_api
from gtts import gTTS
from PIL import Image, ImageSequence
from PIL import ImageFont
from PIL import ImageDraw
from bs4 import BeautifulSoup
from pyppeteer import launch
import logging
from wordcloud import WordCloud, ImageColorGenerator
import numpy as np
from nltk.corpus import stopwords

if adb.tensor_on:
    from rnnmorph.predictor import RNNMorphPredictor

# TODO: обновить иконки ачивок, сделать их одинакового размера, ачивки в профиле, обновить профиль
#        добавить сообщения ВК в стату и общую стату
# TODO: словари для описания команд и микрохелпа (списки на случай если нужно много страниц), ревизия команд

# Contents:
# Vehicle class
# Nexus class
# Vehicle loading and saving
# Loops
# Nexus game functions
# Pictures and music
# Events
# Common functions
# Blackout
# Experience and statistics
# Achievements
# Server/Channel statistics and saving history into file
# Vehicle functions
# TGD functions
# Emoji functions
# VK commands
# Cogs

# Main Init
DIR = os.path.dirname(__file__)
db = sqlite3.connect(os.path.join(DIR, "Akari.db"))
SQL = db.cursor()

vk_session = vk_api.VkApi(token=open('vktoken.txt').readlines()[0])
vka = vk_session.get_api()

client = discord.Client()
bot = commands.Bot(command_prefix=adb.prefix, intents=discord.Intents.all())
bot.remove_command("help")
start_time = time.time()

if adb.tensor_on:
    predictor = RNNMorphPredictor(language="ru")

# Logging
logger = logging.getLogger('AkariWood')
logger.setLevel(logging.INFO)
if not os.path.exists('logs'):
    os.mkdir('logs')
fh = logging.FileHandler(f'logs/Akari-{time.strftime("%d.%m.%Y-%H.%M", time.localtime())}.txt')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)
def logg(x):
    return logger.info(re.sub(r'[^\w\s:()\-<>.,/]|\n', '', x))


# Some Vars
activetimers = []
achs = []
expd = defaultdict(dict)
emosdict = defaultdict(dict)
meslogs = defaultdict(list)
mlFlags = defaultdict(bool)
quis = {}
ACPvars = {}

# Future Vars
bbag = None
programistishe = None
monopolishe = None
mainchannel = None
logchannel = None

# Nexus Vars
nexus1 = None
nexus2 = None
nex1roles = []
nex2roles = []
kingrole = None
mainchannel2 = None
mainchannel2id = 823312775468023858
# TODO: json but not db
"""
nexus: class Nexus and db
nexus_damage: only db
nexus_items: only db
nexus_player_items: class Vehicle and db
nexus_players: class Vehicle, id in class Nexus and db
nexus_players_total: only db
nexus_sets: only db
"""


class Vehicle:
    """
    experience, statistics, custom user-linked emojis, nexus items and stuff
    """
    def __init__(self, sd, new=False):
        self.id = int(sd[0])
        self.server = int(sd[1])
        self.emos = []
        self.bottle = False
        if new:
            self.exp = defaultdict(int)
            self.bbagid = 0
            self.role = defaultdict(int)
            self.name = None
            self.vkid = 0
            self.vkemo = ''
            return
        self.bbagid = int(sd[2])
        self.name = sd[3]
        self.exp = {'exp': int(sd[4]), 'allmessages': int(sd[5]), 'messages': int(sd[6]),
                    'pictures': int(sd[7]), 'mentions': int(sd[8]), 'smiles': int(sd[9]),
                    'mat': sd[14], 'online': sd[15], 'symbols': sd[16], 'selfsmiles': sd[17],
                    'bottles': sd[18], 'dayphrases': sd[19], 'stickers': sd[20], 'vkmes': sd[21],
                    'lastbottle': sd[22]}
        if sd[23]:
            print(f'На бутылке: {sd[3]} ({int(sd[0])})')
            self.bottle = True
        if sd[10]:
            self.role = {'id': int(sd[10]), 'color': int(sd[11], 16)}
        else:
            self.role = defaultdict(int)
        self.vkid = sd[12]
        self.vkemo = sd[13]
        
    def __str__(self):
        c = [self.exp['allmessages'], self.exp['messages'], self.exp['pictures'], self.exp['mentions'], self.exp['smiles']]
        return f'{self.name} {self.id} from {self.server}, exp: {self.exp["exp"]}, counters={c}'

    def __eq__(self, other):
        if self.id == other.id and self.server == other.server:
            return True
        return False

    async def addexp(self, eadd, channel=None, reason='', mem=None):
        if eadd == 0:
            return
        if self.server == adb.bbag:
            if not mem:
                mem = bot.get_guild(self.server).get_member(self.id)
            roles = [i.id for i in mem.roles]
            if adb.congrats in roles:
                eadd = int(eadd * adb.ek_congrats)
        if self.bottle:
            eadd = int(eadd * adb.ek_bottle)
        lvl = adb.levelget(self.exp['exp'])
        self.exp['exp'] += eadd
        if reason:
            if reason != 'online':
                print(f'{self.name} получил {eadd} exp ({reason})')
            logg(f'exp: {self.name} ({self.server}/{self.id}) <- {eadd} exp ({reason})')
        else:
            print(f'{self.name} получил {eadd} exp')
            logg(f'exp: {self.name} ({self.server}/{self.id}) <- {eadd} exp')
        lvl_new = adb.levelget(self.exp['exp'])
        if lvl_new > lvl and self.bbagid <= 10:
            if self.server == adb.bbag:
                if not channel:
                    channel = mainchannel
                if os.path.exists('music') and os.listdir('music') and mem:
                    sound = random.choice(os.listdir('music'))
                    if mem.voice and mem.voice.channel:
                        await forceplay(sound, mem.voice.channel)
                    else:
                        vv = None
                        vvn = -1
                        for vc in mem.guild.voice_channels:
                            if len(vc.members) > vvn:
                                vvn = len(vc.members)
                                vv = vc
                        if vvn > 0:
                            await forceplay(sound, vv)
            else:
                return
            await channel.send(f'{rolemention(self)} апнул новый **{lvl_new}** уровень!', file=number_gif(lvl_new))
            print(f'{self.name} апнул {lvl_new} уровень!')
            logg(f'lvlup: {self.name} ({self.server}/{self.id}) <- {lvl_new} уровень!')


class Nexus:
    """Nexus game"""
    def __init__(self):
        data = None
        last_time = 0
        for i in os.listdir('nexus/data'): # find newest nexus
            le = ast.literal_eval(open(f'nexus/data/{i}').read())
            if le['last_played'] > last_time:
                last_time = le['last_played']
                data = le
        if not data: # if not found, create one
            data = {'season': 1, 'year': int(time.strftime("%y")), 'month': int(time.strftime("%m")), 'players': {},
                    'health0': 1000, 'health1': 1000, 'style': 'hotwater', 'img': 'nexus/data/1.png', 'days': 0}
            with open('nexus/data/1.png', 'w', encoding='uif-8') as f:
                f.write(data)
        self.data = data

    def add_player(self, mid, side):  # side 0 or 1
        self.data['players'][mid] = side

    def remove_player(self, mid):
        if mid in self.data['players']:
            del self.data['players'][mid]

    async def get_damage(self, id, player_id, dmg, reason):
        raw_damage = int(dmg)
        pure = True if 17 in expd[adb.bbag][id].nitems.keys() else False
        items = []
        for p in self.players:
            items += list(expd[adb.bbag][p].nitems.keys())
        if not pure:
            if 2 in items:
                pp = [[p, self.players[p]] for p in self.players if 2 in expd[adb.bbag][p].nitems.keys()][0]
                df = 10 if dmg > 10 else int(dmg)
                SQL.execute(f'UPDATE nexus_players SET damage_block = damage_block + {df} WHERE player_id = {pp[1]}')
                SQL.execute(f'UPDATE nexus_players_total SET damage_block = damage_block + {df} WHERE id = {pp[0]}')
                expd[adb.bbag][pp[0]].nplayer["damage_block"] += df
                dmg -= 10
            if reason != 'daily' and 12 in items:
                pp = [[p, self.players[p]] for p in self.players if 12 in expd[adb.bbag][p].nitems.keys()][0]
                df = 30 if dmg > 30 else int(dmg)
                SQL.execute(f'UPDATE nexus_players SET damage_block = damage_block + {df} WHERE player_id = {pp[1]}')
                SQL.execute(f'UPDATE nexus_players_total SET damage_block = damage_block + {df} WHERE id = {pp[0]}')
                expd[adb.bbag][pp[0]].nplayer["damage_block"] += df
                dmg -= 30
            if (1 in items and adb.chance(25)) or dmg < 0:
                pp = [[p, self.players[p]] for p in self.players if 1 in expd[adb.bbag][p].nitems.keys()][0]
                df = int(dmg)
                SQL.execute(f'UPDATE nexus_players SET damage_block = damage_block + {df} WHERE player_id = {pp[1]}')
                SQL.execute(f'UPDATE nexus_players_total SET damage_block = damage_block + {df} WHERE id = {pp[0]}')
                expd[adb.bbag][pp[0]].nplayer["damage_block"] += df
                dmg = 0
            if self.side == 2:
                dmg *= 0.9
        dmg = int(dmg)
        self.health -= dmg
        SQL.execute(f'UPDATE nexus SET health = {self.health} WHERE id = {self.id}')
        SQL.execute(f'UPDATE nexus_players SET damage = damage + {dmg} WHERE player_id = {player_id}')
        SQL.execute(f'UPDATE nexus_players_total SET damage = damage + {dmg} WHERE id = {id}')
        expd[adb.bbag][id].nplayer["damage"] += dmg
        if reason == 'daily':
            SQL.execute(f'UPDATE nexus_players SET day_damage = day_damage + {dmg} WHERE player_id = {player_id}')
            SQL.execute(f'UPDATE nexus_players_total SET day_damage = day_damage + {dmg} WHERE id = {id}')
            expd[adb.bbag][id].nplayer["day_damage"] += dmg
        sql_insert = f'INSERT INTO nexus_damage(nexus_id, player_id, damage, raw_damage, reason, time, day) VALUES (?,?,?,?,?,?,?)'
        data = (self.id, player_id, dmg, raw_damage, reason, int(time.time()), self.days)
        SQL.execute(sql_insert, data)
        db.commit()
        res = [[id, dmg, reason, self.side]]
        if self.health <= 0:
            res[0].append('death')
        if 15 in items and adb.chance(10):
            pp = [[p, self.players[p]] for p in self.players if 10 in expd[adb.bbag][p].nitems.keys()][0]
            if self.side == 1:
                data2 = await nexus2.get_damage(pp[0], pp[1], dmg, 'Банка с хреном')
            else:
                data2 = await nexus1.get_damage(pp[0], pp[1], dmg, 'Банка с хреном')
            res += data2
        return res

    async def get_heal(self, id, player_id, heal, reason):
        raw_heal = int(heal)
        heal = int(heal)
        self.health += heal
        SQL.execute(f'UPDATE nexus SET health = {self.health} WHERE id = {self.id}')
        SQL.execute(f'UPDATE nexus_players SET heal = heal + {heal} WHERE player_id = {player_id}')
        SQL.execute(f'UPDATE nexus_players_total SET heal = heal + {heal} WHERE id = {id}')
        expd[adb.bbag][id].nplayer["heal"] += heal
        sql_insert = f'INSERT INTO nexus_damage(nexus_id, player_id, damage, raw_damage, reason, time, day) VALUES (?,?,?,?,?,?,?)'
        data = (self.id, player_id, heal*-1, raw_heal*-1, reason, int(time.time()), self.days)
        SQL.execute(sql_insert, data)
        db.commit()
        res = [[id, heal*-1, reason, self.side]]
        return res


# ----------------------------------------------------------------------------------------------------------------------
# Vehicle loading and saving
def AELoad():
    global expd
    global emosdict
    for c in SQL.execute('SELECT * FROM exp').fetchall():
        expd[c[1]][c[0]] = Vehicle(c)
    for g in bot.guilds:
        for m in g.members:
            try:
                if not expd[g.id][m.id]:
                    print(g.id, m.id)
            except:
                expd[g.id][m.id] = Vehicle([g.id, m.id], True)
    for e in SQL.execute('SELECT * FROM emos').fetchall():
        if e[5]:
            code = f'<a:{e[0]}:{e[1]}>'
        else:
            code = f'<:{e[0]}:{e[1]}>'
        if not emosdict[e[2]]:
            emosdict[e[2]] = defaultdict(str)
        emosdict[e[2]][e[0]] = code
        if 0 < e[2] < 11:
            for g in expd:
                for m in expd[g]:
                    if e[2] == expd[g][m].bbagid:
                        expd[g][m].emos.append(code)
    for a in SQL.execute('SELECT * FROM achs').fetchall():
        ach = {'owner': a[0], 'name': a[2], 'level': a[3], 'value': a[4], 'date': a[5]}
        achs.append(ach)


def AESavedef(reason=None):
    for g in expd:
        for m in expd[g]:
            i = expd[g][m].exp
            SQL.execute(f'SELECT * FROM exp WHERE id = {m} AND server = {g}')
            u = SQL.fetchall()
            if not u:
                sql_insert = 'INSERT INTO exp(id, server, exp, allmessages, messages, pictures, mentions, smiles, mat, online, symbols, selfsmiles, bottles, dayphrases, stickers, vkmes, lastbottle) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)'
                SQL.execute(sql_insert, (
                    m, g, i['exp'], i['allmessages'], i['messages'], i['pictures'], i['mentions'], i['smiles'], i['mat'], i['online'], i['symbols'], i['selfsmiles'], i['bottles'], i['dayphrases'], i['stickers'], i['vkmes'], i['lastbottle']))
                db.commit()
            else:
                SQL.execute(
                    f"UPDATE exp SET exp = {i['exp']}, allmessages = {i['allmessages']}, messages = {i['messages']}, pictures = {i['pictures']}, mentions = {i['mentions']}, smiles = {i['smiles']} WHERE id = {m} AND server = {g}")
                SQL.execute(
                    f"UPDATE exp SET mat = {i['mat']}, online = {i['online']}, symbols = {i['symbols']}, selfsmiles = {i['selfsmiles']}, bottles = {i['bottles']} WHERE id = {m} AND server = {g}")
                SQL.execute(
                    f"UPDATE exp SET vkmes = {i['vkmes']}, lastbottle = '{i['lastbottle']}' WHERE id = {m} AND server = {g}")
                SQL.execute(
                    f"UPDATE exp SET dayphrases = {i['dayphrases']}, stickers = {i['stickers']} WHERE id = {m} AND server = {g}")
    db.commit()
    if reason:
        logg(f'aesave: DB saved after '+reason)
    else:
        logg(f'aesave: DB saved after a while...')


@tasks.loop(minutes=adb.e_savetime)
async def AESavetask():
    AESavedef()


# ----------------------------------------------------------------------------------------------------------------------
# Loops
@tasks.loop(minutes=adb.e_onlinetime)
async def online_counter():
    mems = []
    trans_time = datetime.datetime.utcnow() - datetime.timedelta(minutes=adb.e_onlinetime)
    async for mes in mainchannel.history(after=trans_time):
        mems.append(mes.author.id)
    async for mes in programistishe.history(after=trans_time):
        mems.append(mes.author.id)
    async for mes in monopolishe.history(after=trans_time):
        mems.append(mes.author.id)
    for v in bbag.voice_channels:
        if len(v.members) > 1:
            for m in v.members:
                if m.voice and not m.voice.self_deaf:
                    mems.append(m.id)
    mems = list(set(mems))
    for m in mems:
        if 0 < expd[adb.bbag][m].bbagid < 11:
            await expd[adb.bbag][m].addexp(adb.e_online, reason='online')
            expd[adb.bbag][m].exp['online'] += adb.e_onlinetime
            await sum_achieve(m, {"online": True})
            await asyncio.sleep(1)


@tasks.loop(hours=1)
async def daycheck():
    if time.strftime("%H") == "17":
        if not os.path.exists('AEBackups'):
            os.mkdir('AEBackups')
        shutil.copyfile("Akari.db", f"AEBackups/Akari{random.randint(10000, 99999)}.db")


@tasks.loop(hours=1)
async def daymeme():
    if time.strftime("%H") == "18":
        mems = []
        async for m in bot.get_channel(adb.mymemes).history(limit=10000):
            mems += [a.url for a in m.attachments]
        if mems:
            emb = discord.Embed(title='Мем дня')
            emb.set_image(url=random.choice(mems))
            mes = await mainchannel.send(embed=emb)
            await mes.add_reaction(get_emoji('TemaOr'))
            await mes.add_reaction(get_emoji('Tthinking'))
            await mes.add_reaction(get_emoji('FaceTem'))
            await mes.add_reaction(get_emoji('hateful'))


@tasks.loop(hours=1)
async def daybottle():
    if time.strftime("%H") == "20":
        mem = random.choice([i for i in expd[adb.bbag] if 0 < expd[adb.bbag][i].bbagid < 11])
        await bottledef(mem)


@tasks.loop(hours=1)
async def dayphrase():
    if time.strftime("%H") == "22":
        file = open('pips/phrases.txt', encoding='utf-8').readlines()
        phrase = random.choice(file)
        author = ''
        if '©' in phrase:
            phrase, author = phrase.split('©')
        phrase.rstrip()
        emb = discord.Embed(title='Фраза дня', description=phrase)
        if author:
            url = ''
            member = author.split('+')[0].split(' ')[0].replace('\n', '')
            for m in expd[adb.bbag]:
                if expd[adb.bbag][m].name == member:
                    try:
                        mem = bot.get_guild(adb.bbag).get_member(m)
                        url = mem.avatar_url
                    except:
                        continue
            if url:
                emb.set_footer(icon_url=url, text=f'©{author}')
                expd[adb.bbag][mem.id].exp['dayphrases'] += 1
                await expd[adb.bbag][mem.id].addexp(adb.e_dayphrase, reason='фраза дня', mem=mem)
        mes = await mainchannel.send(embed=emb)
        await mes.add_reaction(get_emoji('TemaOr'))
        await mes.add_reaction(get_emoji('Tthinking'))
        AESavedef('a dayphrase')


@tasks.loop(minutes=3)
async def achieve_giver():
    for m in expd[adb.bbag]:
        if not 0 < expd[adb.bbag][m].bbagid < 11:
            continue
        for i in adb.achieves:
            c, ac, s, n, t, d, icon = i['counts'], i['addcount'], i['stat'], i['name'], i['title'], i['desc'], i['icon']
            cur_levels = [a['level'] for a in achs if a['owner'] == m and a['name'] == n]
            nextlevel = max(cur_levels) + 1 if cur_levels else 1
            nextvalue = c[nextlevel - 1] if nextlevel <= len(c) else c[-1] + ac * (nextlevel - len(c))
            value = adb.levelget(expd[adb.bbag][m].exp[s]) if s == 'exp' else expd[adb.bbag][m].exp[s]
            if value >= nextvalue:
                ach = {'name': n, 'level': nextlevel, 'value': nextvalue,
                       'date': time.strftime("%d.%m.%Y, %H:%M", time.localtime()), 'owner': m}
                achs.append(ach)
                save_achieve(ach)
                title = f'{t} {adb.to_roman(nextlevel)}'
                desc = d.format(nextvalue)
                purl = await picfinder(icon)
                emb = discord.Embed(title='Achievement get!',
                                    description=f'**{title}**\n{desc}\nНаграду получил: {rolemention(expd[adb.bbag][m])}')
                emb.set_image(url=purl)
                await mainchannel.send(embed=emb)
                await expd[adb.bbag][m].addexp(adb.e_ach + nextlevel * adb.e_ach_lvladd,
                                               reason=f'{n} {adb.to_roman(nextlevel)}')
                AESavedef('giving an achieve')


@tasks.loop(hours=1)
async def bbag_reminder():
    hour = int(time.strftime("%H"))
    picname = ''
    if picname and 7 < hour < 22 and hour % 3 == 2:
        purl = await picfinder(picname)
        mes = await mainchannel.send(purl)
        await mes.add_reaction('<:agroMornyX:833000410976354334>')


@tasks.loop(hours=1)
async def all_guilds_save():
    if time.strftime("%d") == "24" and time.strftime("%H") == "22":
        if adb.if_host:
            for g in bot.guilds:
                savepics = 'False' if g.id in adb.guildsave_pic_blacklist else ''
                await guildsavedef(g, None, savepics, f'D:/Brutal Bro Abnormal Gang/Archives/{g.name}')
        else:
            tai = bot.get_guild(adb.dmh).get_channel(adb.taisetsu)
            await tai.send('Время делать бекап!')


@tasks.loop(seconds=10)
async def voice_disconnect():
    voice = discord.utils.get(bot.voice_clients, guild=bbag)
    if voice and voice.is_connected() and not voice.is_playing():
        await voice.disconnect()


@tasks.loop(hours=1)
async def weeklyword():
    if time.strftime("%w") == "0" and time.strftime("%H") == "21":
        trans_time = datetime.datetime.utcnow() - datetime.timedelta(days=7)
        words = []
        russian_stopwords = stopwords.words("russian")
        async for mes in mainchannel.history(after=trans_time):
            sp = re.sub(r'<[\S]+>|https*|://[\S]+', '', mes.content).lstrip()
            sp = re.sub(r'[^\s\w-]', '', re.sub(r'[\n_ ]+', ' ', sp)).split(' ')
            words += [i for i in sp if i and i not in russian_stopwords]
        mask = np.array(Image.open("pips/caban.png"))
        wordcloud = WordCloud(background_color="white", mask=mask, max_font_size=40).generate(' '.join(words))

        wordcloud.recolor(color_func=ImageColorGenerator(mask))
        wordcloud.to_file("pips/wordcloud.png")
        await mainchannel.send(file=discord.File(fp="pips/wordcloud.png"))


# ----------------------------------------------------------------------------------------------------------------------
# Nexus game functions
def nsort(l):
    pass


def nexus_draw():
    phone = Image.open(f'nexus/{nexus1.season}_raw.png').convert('RGBA')
    SQL.execute(f'SELECT * FROM nexus_style_poses WHERE style = "{nexus1.style}"')
    pos1 = SQL.fetchone()
    SQL.execute(f'SELECT * FROM nexus_style_poses WHERE style = "{nexus2.style}"')
    pos2 = SQL.fetchone()
    imgs1 = random.shuffle([i for i in nexus1.players])
    imgs2 = random.shuffle([i for i in nexus2.players])

    for i, id in enumerate(imgs1):
        idx = len(imgs1)-i-1
        items = []
        if pos1[idx][5]:
            pad = Image.open(f'nexus/pad_{nexus1.style}.png').convert('RGBA')
            if pos1[idx][8] != 100:
                h, w = pad.size
                pad = pad.resize((h*pos1[idx][8]/100, w*pos1[idx][8]/100))
            phone.paste(pad, (pos1[idx][6], pos1[idx][7]), pad)

        img = Image.open(f'nexus/{expd[adb.bbag][id].nplayer["icon"]}').convert('RGBA')
        if pos1[idx][4] != 100:
            h, w = img.size
            img = img.resize((h * pos1[idx][4] / 100, w * pos1[idx][4] / 100))
        phone.paste(img, (pos1[idx][2], pos1[idx][3]), img)

        av = Image.open(f'nexus/a{expd[adb.bbag][id].bbagid}.png').convert('RGBA')
        if pos1[idx][4] != 100:
            h, w = av.size
            av = av.resize((h * pos1[idx][4] / 100, w * pos1[idx][4] / 100))
        phone.paste(av, (pos1[idx][2]+22, pos1[idx][3]-17), av)

        nitems = nsort(list(expd[adb.bbag][id].nitems.keys()))
        for item in nitems:
            itg = Image.open(f'nexus/i{item}.png').convert('RGBA')
            if pos1[idx][4] != 100:
                h, w = itg.size
                av = itg.resize((h * pos1[idx][4] / 100, w * pos1[idx][4] / 100))

            idata = SQL.execute(f'SELECT * FROM nexus_poses WHERE pose_id = 1 AND item_id = {item}').fetchone()
            if idata[2] != 100:
                h, w = itg.size
                av = itg.resize((h * pos1[idx][2] / 100, w * pos1[idx][2] / 100))
            if item in [13]:
                eyepose = SQL.execute(f'SELECT nexus_eyes FROM exp WHERE id = {id}').fetchone()[0] # FIXME: этого нет в exp
                phone.paste(av, (pos1[idx][2]+int(eyepose.split('.'[0]))-13, pos1[idx][3]), av)
            else:
                phone.paste(av, (pos1[idx][2] + idata[3], pos1[idx][3] + idata[4]), av)
            items.append(item)

    for i, id in enumerate(imgs2):
        idx = len(imgs2)-i-1
        items = []

        if pos2[idx][5]:
            pad = Image.open(f'nexus/pad_{nexus2.style}.png').convert('RGBA')
            if pos2[idx][8] != 100:
                h, w = pad.size
                pad = pad.resize((h*pos2[idx][8]/100, w*pos2[idx][8]/100))
            phone.paste(pad, (pos2[idx][6], pos2[idx][7]), pad)

        img = Image.open(f'nexus/{expd[adb.bbag][id].nplayer["icon"]}').convert('RGBA')
        if pos2[idx][4] != 100:
            h, w = img.size
            img = img.resize((h * pos2[idx][4] / 100, w * pos2[idx][4] / 100))
        phone.paste(img, (pos2[idx][2], pos2[idx][3]), img)

        av = Image.open(f'nexus/a{expd[adb.bbag][id].bbagid}.png').convert('RGBA')
        if pos2[idx][4] != 100:
            h, w = av.size
            av = av.resize((h * pos2[idx][4] / 100, w * pos2[idx][4] / 100))
        phone.paste(av, (pos2[idx][2]+22, pos2[idx][3]-17), av)

        nitems = nsort(list(expd[adb.bbag][id].nitems.keys()))
        for item in nitems:
            itg = Image.open(f'nexus/i{item}.png').convert('RGBA')
            if pos2[idx][4] != 100:
                h, w = itg.size
                av = itg.resize((h * pos2[idx][4] / 100, w * pos2[idx][4] / 100))

            idata = SQL.execute(f'SELECT * FROM nexus_poses WHERE pose_id = 1 AND item_id = {item}').fetchone()
            if idata[2] != 100:
                h, w = itg.size
                av = itg.resize((h * pos2[idx][2] / 100, w * pos2[idx][2] / 100))
            if item in [13]:
                eyepose = SQL.execute(f'SELECT eyepose FROM exp WHERE id = {id}').fetchone()[0] # FIXME: этого нет в exp
                phone.paste(av, (pos2[idx][2]+int(eyepose.split('.'[0]))-13, pos2[idx][3]), av)
            else:
                phone.paste(av, (pos2[idx][2] + idata[3], pos2[idx][3] + idata[4]), av)
            items.append(item)

    phone.save(f'nexus/{nexus1.season}.png')
    file = discord.File(fp=f'nexus/{nexus1.season}.png')
    return file


def nexus_starter():
    if adb.nexus_on:
        global nex1roles
        global nex2roles
        for i in adb.nexusroles[1]:
            role = bbag.get_role(i)
            nex1roles.append(role)
        for i in adb.nexusroles[2]:
            role = bbag.get_role(i)
            nex2roles.append(role)
        SQL.execute('SELECT * FROM nexus WHERE side = 1 ORDER BY season DESC')
        n1 = SQL.fetchone()
        if not n1:
            print('\033[31m\033[1mОшибка: нет нексуса в базе данных')
            return
        SQL.execute(f'SELECT * FROM nexus WHERE side = 2 AND season = {n1[1]}')
        n2 = SQL.fetchone()
        if not n2:
            print('\033[31m\033[1mОшибка: нет второго нексуса в базе данных')
            return
        if n1[5] <= 0 or n2[5] <= 0:
            print('\033[31m\033[1mОшибка: у нексуса нет здоровья')
            return

        global nexus1
        global nexus2
        nexus1 = Nexus(n1)
        nexus2 = Nexus(n2)
        p1 = SQL.execute(f"SELECT * FROM nexus_players WHERE nexus_id = {nexus1.id}").fetchall()
        p2 = SQL.execute(f"SELECT * FROM nexus_players WHERE nexus_id = {nexus2.id}").fetchall()
        nexus1.add_players(p1)
        nexus2.add_players(p2)
        for p in p1+p2:
            expd[adb.bbag][p[2]].nplayer = {'player_id': p[0], 'nexus_id': p[1], 'level': p[3], 'icon': p[4], 'damage': p[6], 'heal': p[7], 'damage_block': p[8], 'day_damage': p[9]}
            items = SQL.execute(f"SELECT * FROM nexus_items WHERE item_id in "
                                f"(SELECT item_id FROM nexus_player_items WHERE player_id = {p[0]})").fetchall()
            expd[adb.bbag][p[2]].nitems = {i[0]: {'id': i[0], 'name': i[1], 'description': i[2], 'level': i[3], 'season': i[4], 'icon': i[5]} for i in items}


@tasks.loop(hours=1)
async def nexus_daily():
    if adb.nexus_on:
        if time.strftime("%H") == "06":
            global nexus1
            global nexus2
            endFlag = 0
            if time.strftime("%d") != "01":
                items1 = []
                items2 = []
                dmgl = []
                for p in nexus1.players:
                    items1 += list(expd[adb.bbag][p].nitems.keys())
                for p in nexus2.players:
                    items2 += list(expd[adb.bbag][p].nitems.keys())
                for p in nexus1.players:
                    pitems = expd[adb.bbag][p].nitems.keys()
                    dmg = 10
                    if 4 in items1:
                        dmg *= 2
                    if 13 in pitems:
                        dmg *= 1.5
                    if 6 in pitems and adb.chance(25):
                        dmg *= 2
                    if 16 in pitems and adb.chance(20):
                        dmg *= 1.5
                    if 3 in items2:
                        dmg = 0
                    dmgi = await nexus2.get_damage(p, nexus1.players[p], dmg, 'daily')
                    dmgl += dmgi
                    if 9 in items1:
                        heal = dmgi[0][3] / 2
                        pp = [[p, nexus1.players[p]] for p in nexus1.players if 10 in expd[adb.bbag][p].nitems.keys()][0]
                        dmgi = await nexus1.get_heal(pp[0], pp[1], heal, 'Ангельское крыло')
                        dmgl += dmgi
                    if 10 in items2:
                        pp = [[p, nexus2.players[p]] for p in nexus2.players if 10 in expd[adb.bbag][p].nitems.keys()][0]
                        dmgi = await nexus1.get_damage(pp[0], pp[1], dmg / 2, 'Зеркало души')
                        dmgl += dmgi
                for p in nexus2.players:
                    pitems = expd[adb.bbag][p].nitems.keys()
                    dmg = 10
                    if 4 in items2:
                        dmg *= 2
                    if 13 in pitems:
                        dmg *= 1.5
                    if 6 in pitems and adb.chance(25):
                        dmg *= 2
                    if 16 in pitems and adb.chance(20):
                        dmg *= 1.5
                    if 3 in items1:
                        dmg = 0
                    dmgi = await nexus1.get_damage(p, nexus2.players[p], dmg, 'daily')
                    dmgl += dmgi
                    if 9 in items2:
                        heal = dmgi[0][3] / 2
                        pp = [[p, nexus2.players[p]] for p in nexus2.players if 10 in expd[adb.bbag][p].nitems.keys()][0]
                        dmgi = await nexus2.get_heal(pp[0], pp[1], heal, 'Ангельское крыло')
                        dmgl += dmgi
                    if 10 in items1:
                        pp = [[p, nexus1.players[p]] for p in nexus1.players if 10 in expd[adb.bbag][p].nitems.keys()][0]
                        dmgi = await nexus2.get_damage(pp[0], pp[1], dmg / 2, 'Зеркало души')
                        dmgl += dmgi
                if nexus1.health > 0:
                    SQL.execute(f'UPDATE nexus SET days = days+1 WHERE id = {nexus1.id}')
                    nexus1.days += 1
                if nexus2.health > 0:
                    SQL.execute(f'UPDATE nexus SET days = days+1 WHERE id = {nexus2.id}')
                    nexus2.days += 1
                db.commit()
                emb = discord.Embed(title=f'Дневной урон, день {max([nexus1.days, nexus2.days])}')
                d1 = ''
                d2 = ''
                for i in dmgl:
                    if i[3] == 2:
                        d1 += f'{bbag.get_role(expd[adb.bbag][i[0]].role["id"]).mention}{random.choice(expd[adb.bbag][i[0]].emos)} наносит **{i[1]}**'
                        if i[2] != 'daily':
                            d1 += f' by {i[2]}'
                        d1 += '\n'
                    if i[3] == 1:
                        d2 += f'{bbag.get_role(expd[adb.bbag][i[0]].role["id"]).mention}{random.choice(expd[adb.bbag][i[0]].emos)} наносит **{i[1]}**'
                        if i[2] != 'daily':
                            d2 += f' by **{i[2]}**'
                        d2 += '\n'
                for i in dmgl[::-1]:
                    if i[-1] == 'death':
                        endFlag = i[3]
                if not d1:
                    d1 = 'Нет'
                if not d2:
                    d2 = 'Нет'
                emb.add_field(name='☀️Свет', value=d1)
                emb.add_field(name='🌙️ Тьма', value=d2)
                await mainchannel2.send(embed=emb)
            mesdays = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
            mesidx = int(time.strftime("%m")) - 1
            if endFlag or time.strftime("%d") == str(mesdays[mesidx]):
                if endFlag == 1:
                    halfor = 1
                    winners = nexus1.players.keys()
                    emb = discord.Embed(title=f'Nexus Battle Season {nexus1.season} End',
                                        description=f'Игра закончилась! Победила команда ☀️Света!')
                elif endFlag == 2:
                    halfor = 1
                    winners = nexus2.players.keys()
                    emb = discord.Embed(title=f'Nexus Battle Season {nexus1.season} End',
                                        description=f'Игра закончилась! Победила команда 🌙️ Тьмы!')
                else:
                    if nexus1.health == nexus2.health:
                        halfor = 0.5
                        winners = list(nexus1.players.keys()) + list(nexus2.players.keys())
                        emb = discord.Embed(title=f'Nexus Battle Season {nexus1.season} End',
                                            description=f'Игра закончилась! Между командами ничья! У обоих нексусов осталось {nexus1.health} здоровья')
                    elif nexus1.health > nexus2.health:
                        halfor = 1
                        winners = nexus1.players.keys()
                        emb = discord.Embed(title=f'Nexus Battle Season {nexus1.season} End',
                                            description=f'Игра закончилась! Победила команда ☀️Света!')
                    else:
                        halfor = 1
                        winners = nexus2.players.keys()
                        emb = discord.Embed(title=f'Nexus Battle Season {nexus1.season} End',
                                            description=f'Игра закончилась! Победила команда 🌙️ Тьмы!')
                desc = ''
                maxdmg = 0
                maxdmgp = None
                for p in winners:
                    desc += f'{bbag.get_role(expd[adb.bbag][p].role["id"]).mention}{random.choice(expd[adb.bbag][p].emos)}:\n  Урон: **{expd[adb.bbag][p].nplayer["damage"]}**, **{expd[adb.bbag][p].nplayer["level"]}** уровень,\n' \
                            f'  блок урона: **{expd[adb.bbag][p].nplayer["damage_block"]}**, хил: **{expd[adb.bbag][p].nplayer["heal"]}** уровень\n'
                    dmg = expd[adb.bbag][p].nplayer["damage"] + expd[adb.bbag][p].nplayer["damage_block"] + expd[adb.bbag][p].nplayer["heal"]
                    if dmg > maxdmg:
                        maxdmg = dmg
                        maxdmgp = p
                    await expd[adb.bbag][p].addexp(int(adb.e_nexwinner * halfor), reason='Nexus winner!')
                for p in list(nexus1.players.keys()) + list(nexus2.players.keys()):
                    expd[adb.bbag][p].nitems = defaultdict(int)
                    expd[adb.bbag][p].nplayer = defaultdict(int)
                emb.add_field(name='Игроки-победители', value=desc)
                img = nexus_draw()
                mes = await logchannel.send(file=img)
                nexus1.img = mes.attachments[0].url
                emb.set_image(url=nexus1.img)
                SQL.execute('SELECT * FROM nexus WHERE side = 1 ORDER BY season DESC')
                n1 = SQL.fetchone()
                SQL.execute(f'SELECT * FROM nexus WHERE side = 2 AND season = {n1[1]}')
                n2 = SQL.fetchone()
                icon1 = f'{n1[1] + 1}.png' if f'{n1[1] + 1}.png' in os.listdir('nexus') else ''
                icon2 = f'{n2[1] + 1}.png' if f'{n2[1] + 1}.png' in os.listdir('nexus') else ''
                data1 = (n1[0] + 2, n1[1] + 1, 0, 0, 1, 1000, n1[6], icon1, 0)
                data2 = (n2[0] + 2, n2[1] + 1, 0, 0, 2, 1000, n2[6], icon2, 0)
                nexus1 = Nexus(data1)
                nexus2 = Nexus(data2)
                sql_insert = f"INSERT INTO nexus(id, season, year, month, side, health, style, img, days) VALUES (?,?,?,?,?,?,?,?,?)"
                SQL.execute(sql_insert, data1)
                SQL.execute(sql_insert, data2)
                SQL.execute(f"UPDATE sets SET value = 0 WHERE name = 'cd1_cz'")
                SQL.execute(f"UPDATE sets SET value = 0 WHERE name = 'cd1_8ball'")
                SQL.execute(f"UPDATE sets SET value = 0 WHERE name = 'cd1_spor'")
                SQL.execute(f"UPDATE sets SET value = 0 WHERE name = 'cd1_flip'")
                SQL.execute(f"UPDATE sets SET value = 0 WHERE name = 'cd2_cz'")
                SQL.execute(f"UPDATE sets SET value = 0 WHERE name = 'cd2_8ball'")
                SQL.execute(f"UPDATE sets SET value = 0 WHERE name = 'cd2_spor'")
                SQL.execute(f"UPDATE sets SET value = 0 WHERE name = 'cd2_flip'")
                db.commit()
                for m in bbag.members:
                    for r in nex1roles + nex2roles + [kingrole]:
                        await m.remove_roles(r)
                    if m.id == maxdmgp:
                        await m.add_roles(kingrole)
                await mainchannel2.send(embed=emb)
            else:
                emb = discord.Embed(title=f'Nexus Battle Season {nexus1.season}',
                                    description='Добро пожаловать на битву Нексусов! Присоединяйтесь к силам света и тьмы, играйте в мини-игры, находите предметы и уничтожьте Нексус врага!')
                emb.add_field(name="Свет ☀️",
                              value='Силы света наносят на 20% больше урона, участвуя в играх. Приходи к нам за лучиком добра')
                emb.add_field(name="Игры",
                              value=f'Игры приносят много очков, но имеют большой кулдаун:\n**;flip 0|1** {adb.reload} 3d'
                                    f'\n**;spor** {adb.reload} 2d\n**;cz** {adb.reload} 3d'
                                    f'**;8ball** {adb.reload} 2d')
                emb.add_field(name="Тьма 🌙",
                              value='Силы тьмы получают на 10% меньше урона от любых источников. Переходи к нам, у нас есть печеньки')
                emb.add_field(name="Уровни",
                              value='Повышайте мастерство владения светом или тьмой, нанося урон Нексусу врага. Уровень сбросится, если сменить сторону!')
                emb.add_field(name="Предметы", value='Вы можете находить предметы, дающие прирост к характеристикам')
                emb.add_field(name="Бонусы",
                              value='Помочь уничтожению вражеского Нексуса можно прослушивая музыку или, например, сев на бутылку')
                emb.add_field(name="Дневной урон",
                              value='Каждый день ваша команда наносит урон вражескому Нексусу')
                emb.add_field(name="Испытания",
                              value='Выполняйте специальные задания и получайте за них очки!')
                img = nexus_draw()
                mes = await logchannel.send(file=img)
                nexus1.img = mes.attachments[0].url
                emb.set_image(url=nexus1.img)
                mes = await mainchannel2.send(embed=emb)
                await mes.add_reaction('☀️')
                await mes.add_reaction('🌙')


# ----------------------------------------------------------------------------------------------------------------------
# Pictures and music
async def picfinder(text, ch=None):
    if not ch:
        ch = adb.enpics
    async for m in bot.get_channel(ch).history(limit=10000):
        if m.content == text:
            if m.attachments:
                return m.attachments[0].url
    raise ValueError(f"Encoded pic {text} not found")


async def forceplay(name, channel):
    try:
        guild = channel.guild
        try:
            await channel.connect()
        except:
            pass
        voice = discord.utils.get(bot.voice_clients, guild=guild)
        voice.play(discord.FFmpegOpusAudio(source=f'music/{name}'))
        voice.source = discord.PCMVolumeTransformer(voice.source)
        voice.source.volume = 100
    except:
        return


def number_gif(num):
    if int(num) < 10:
        return discord.File(fp=f'pips/{num}.gif')
    num = str(num)
    main_ims = []
    frames = {'0':9, '1':6, '2':7, '3':11, '4':9, '5':7, '6':6, '7':6, '8':5, '9':7}
    for f in range(1, 8):
        main_im = Image.new('RGBA', (45 * len(num), 100), (54, 57, 63, 255))
        for i, im in enumerate(num):
            frame_num = f if f < frames[im] else frames[im]
            im = Image.open(f'pips/numgifs/{im}_{frame_num}.png').convert('RGBA')
            main_im.paste(im, (45 * i, 0, 45 * (i + 1), 100), im)
        main_ims.append(main_im)

    if not os.path.exists('pips/numgifs_'):
        os.mkdir('pips/numgifs_')
    path = f'pips/numgifs_/{num}.gif'
    main_ims[0].save(
        path,
        optimize=False,
        save_all=True,
        append_images=main_ims[1:],
        duration=200,
        loop=0,
        transparency=0
    )
    return discord.File(fp=path)


@bot.command()
async def numgif(ctx, num):
    await ctx.send(file=number_gif(num))


# ----------------------------------------------------------------------------------------------------------------------
# Events
@bot.event
async def on_message(message):
    if message.content.startswith(adb.prefix):
        for i in adb.allcoms:
            if i == 'r':
                if message.content.split(' ')[0] != adb.prefix+i:
                    continue
            if message.content.startswith(adb.prefix+i):
                if i != 'clear' and i != 'newemoji':
                    try:
                        await message.delete()
                    except:
                        pass
                name = expd[message.guild.id][message.author.id].name
                print(f'{name} применил {i}')
                logg(f'command: {name} ({message.guild.id}/{message.author.id}) -> {i}')
                sql_insert = 'INSERT INTO commlog(id, server, name, command, date) VALUES (?,?,?,?,?)'
                SQL.execute(sql_insert, (message.author.id, message.guild.id, name, i, time.strftime("%d.%m.%Y, %X", time.localtime())))
                db.commit()
    await bot.process_commands(message)
    if message.channel.id in adb.oldchannels:
        await message.channel.send(f'Дебил! Это не тот канал! Пиши в {mainchannel.mention}', file=adb.mischat, delete_after=30)
        if len(message.content) > 0 and len(message.content) <= 1900:
            await mainchannel.send(f'`{message.author.name}`{smile(message)} из {message.channel.mention}:\n{message.content}')
        return
    if message.author.id != bot.user.id:
        await AkariCatch(message)
        await AkariCoderEvent(message)
        await AkariCalculatingProcessor(message)
        await AkariMetrics(message)
    await memlog(message)
    if message.channel.id == adb.vkchannel:
        await vkExp(message)
    await AkariExp(message)
    if '&$' in message.content:
        await rolelore(message)
    if message.author.id != bot.user.id:
        await AkariSwitcher(message)
        # await AkariCorrector(message)


@bot.event
async def on_message_edit(_, new):
    if new.content.startswith(adb.prefix):
        for i in adb.allcoms:
            if i == 'r':
                if not new.content.split(' ')[0] != adb.prefix + i:
                    continue
            if new.content.startswith(adb.prefix + i):
                if i != 'clear' and i != 'newemoji':
                    await new.delete()
                name = expd[new.guild.id][new.author.id].name
                print(f'{name} применил {i}')
                logg(f'command_edit: {name} ({new.guild.id}/{new.author.id}) -> {i}')
                sql_insert = 'INSERT INTO commlog(id, server, name, command, date) VALUES (?,?,?,?,?)'
                SQL.execute(sql_insert, (
                new.author.id, new.guild.id, name, i, time.strftime("%d.%m.%Y, %X", time.localtime())))
                db.commit()
    await bot.process_commands(new)

    
@bot.event
async def on_ready():
    global bbag
    global programistishe
    global monopolishe
    global mainchannel
    global logchannel
    bbag = bot.get_guild(adb.bbag)
    programistishe = bot.get_channel(adb.programistishe)
    monopolishe = bot.get_channel(adb.monopolishe)
    mainchannel = bot.get_channel(adb.bbagmain)
    mainchannel2 = bot.get_channel(mainchannel2id) # для отладки нексуса
    logchannel = bot.get_channel(adb.botcage)
    AELoad()
    nexus_starter()
    AESavetask.start()
    daycheck.start()
    dayphrase.start()
    daymeme.start()
    daybottle.start()
    online_counter.start()
    achieve_giver.start()
    bbag_reminder.start()
    voice_disconnect.start()
    nexus_daily.start()
    weeklyword.start()
    gr = random.choice(adb.greets)
    await logchannel.send(gr, delete_after=30)
    print(gr)
    all_guilds_save.start()
    logg("start: Bot started, all tasks work and tables loaded!")
    activity = discord.Activity(name=f"Плюётся в людей | {adb.prefix}help", type=0)
    await bot.change_presence(status=discord.Status.online, activity=activity)


@bot.event
async def on_raw_reaction_add(payload):
    if str(payload.emoji) == '<:agroMornyX:833000410976354334>' and payload.user_id != bot.user.id:
        mes = await bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
        await mes.delete()
    elif payload.message_id in quis and payload.user_id != bot.user.id:
        mes = await bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
        qdict = quis[payload.message_id]
        emb = discord.Embed(title='Опрос', description=qdict['desc'])
        for i in qdict['ans']:
            if not i['emo'] == str(payload.emoji):
                try:
                    await mes.remove_reaction(i['emo'], payload.member)
                except:
                    pass
        mes = await bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
        all = 0
        for ii,i in enumerate(qdict['ans']):
            for r in mes.reactions:
                if str(r.emoji) == i['emo']:
                    qdict['ans'][ii]['count'] = r.count - 1
                    all += r.count - 1
        for i in qdict['ans']:
            if all == 0:
                prog = '░' * 20
                perc = f'0.00%'
                add = ''
            else:
                prog = int(round((i['count'] / all) * 20))
                prog = f"{'▓' * prog}{'░' * (20 - prog)}"
                perc = f"{round((i['count'] / all) * 100, 2)}%"
                add = f"({i['count']})" if i['count'] > 0 else ''
            emb.add_field(name=i['name'] + ' ' + add, value=f"{i['emo']} {prog} {perc}", inline=False)
            emb.set_footer(icon_url=qdict['author'].avatar_url, text=f"©{qdict['author'].display_name}")
        await mes.edit(embed=emb)
    if adb.nexus_on:
        if payload.user_id == bot.user.id:
            return
        m = payload.member
        if not m.id in expd[adb.bbag]:
            return
        elif not 0 < expd[adb.bbag][m.id].bbagid < 11:
            return
        react = str(payload.emoji)
        message = await payload.member.guild.get_channel(payload.channel_id).fetch_message(payload.message_id)
        if react == '☀️':
            try:
                await message.remove_reaction('🌙', m)
            except:
                pass
            SQL.execute(f"SELECT * FROM nexus_players WHERE id = {m.id}")
            dbp = SQL.fetchone()
            if dbp and (dbp[1] == nexus1.id or time.time() - dbp[5] > 60):
                return
            for r in nex2roles:
                await m.remove_roles(r)
            for r in nex1roles[:2]:
                await m.add_roles(r)
            if dbp:
                SQL.execute(f"UPDATE nexus_players SET nexus_id = {nexus1.id} WHERE id = {m.id}")
                pid = dbp[0]
                expd[adb.bbag][m.id].nplayer['nexus_id'] = nexus1.id
            else:
                icon = random.choice([i for i in os.listdir('nexus') if i.startswith('p1')])
                sql_insert = f"INSERT INTO nexus_players(nexus_id, id, name, level, icon) VALUES (?,?,?,?,?)"
                SQL.execute(sql_insert, (nexus1.id, m.id, expd[adb.bbag][m.id].name, 1, icon))

                SQL.execute(f"SELECT * FROM nexus_players_total WHERE id = {m.id}")
                dbpt = SQL.fetchone()
                if not dbpt:
                    sql_insert = f"INSERT INTO nexus_players_total(id, name) VALUES (?,?)"
                    SQL.execute(sql_insert, (m.id, expd[adb.bbag][m.id].name))

                SQL.execute(f"SELECT * FROM nexus_players WHERE id = {m.id} AND nexus_id = {nexus1.id}")
                dbp = SQL.fetchone()
                pid = dbp[0]
                expd[adb.bbag][m.id].nplayer = {'player_id': pid, 'nexus_id': nexus1.id, 'level': 1, 'damage': 0,
                                                'day_damage': 0, 'damage_block': 0, 'heal': 0, 'icon': icon}
            nexus2.remove_player(m.id, pid)
            nexus1.add_player(m.id, pid)
            db.commit()

        elif react == '🌙':
            try:
                await message.remove_reaction('☀️', m)
            except:
                pass
            SQL.execute(f"SELECT * FROM nexus_players WHERE id = {m.id}")
            dbp = SQL.fetchone()
            if dbp and (dbp[1] == nexus2.id or time.time() - dbp[5] > 60):
                return
            for r in nex1roles:
                await m.remove_roles(r)
            for r in nex2roles[:2]:
                await m.add_roles(r)
            if dbp:
                SQL.execute(f"UPDATE nexus_players SET nexus_id = {nexus2.id} WHERE id = {m.id}")
                pid = dbp[0]
                expd[adb.bbag][m.id].nplayer['nexus_id'] = nexus2.id
            else:
                icon = random.choice([i for i in os.listdir('nexus') if i.startswith('p1')])
                sql_insert = f"INSERT INTO nexus_players(nexus_id, id, name, level, icon) VALUES (?,?,?,?,?)"
                SQL.execute(sql_insert, (nexus2.id, m.id, expd[adb.bbag][m.id].name, 1, icon))

                SQL.execute(f"SELECT * FROM nexus_players_total WHERE id = {m.id}")
                dbpt = SQL.fetchone()
                if not dbpt:
                    sql_insert = f"INSERT INTO nexus_players_total(id, name) VALUES (?,?)"
                    SQL.execute(sql_insert, (m.id, expd[adb.bbag][m.id].name))

                SQL.execute(f"SELECT * FROM nexus_players WHERE id = {m.id} AND nexus_id = {nexus2.id}")
                dbp = SQL.fetchone()
                pid = dbp[0]
                expd[adb.bbag][m.id].nplayer = {'player_id': pid, 'nexus_id': nexus2.id, 'level': 1, 'damage': 0,
                                                'day_damage': 0, 'damage_block': 0, 'heal': 0, 'icon': icon}
            nexus1.remove_player(m.id, pid)
            nexus2.add_player(m.id, pid)
            db.commit()


@bot.event
async def on_member_join(m):
    try:
        if not expd[m.guild.id][m.id]:
            print(m.guild.id, m.id)
    except:
        expd[m.guild.id][m.id] = Vehicle([m.guild.id, m.id], True)
    if m.guild.id == adb.bbag:
        await mainchannel.send(f'{rolemention(expd[m.guild.id][m.id])}', file=adb.streetracing)


@bot.event
async def on_typing(channel, user, ttime):
    if adb.chance(1, 1000):
        await channel.send(f'{rolemention(expd[channel.guild.id][user.id])}{random.choice(adb.typing)}')
    if channel.guild.id == adb.dmh and not channel.id == adb.memlog and not mlFlags[channel.id]:
        meslogs[channel.id].append(int(time.time()))
        mlFlags[channel.id] = True
        await asyncio.sleep(120)
        mlFlags[channel.id] = False


@bot.event
async def on_member_remove(member):
    if member.guild.id == adb.bbag:
        # await mainchannel.send(embed=discord.Embed(title='НУ ПОКА', description=f'Харон провожает **{member.nick}** в Тартар))'), file=adb.cannon)
        SQL.execute(f'SELECT value FROM config WHERE name = "daykick"')
        d = SQL.fetchone()[0].split('.')
        days = int(time.time() - time.mktime((int(d[2]), int(d[1]), int(d[0]), 0, 0, 0, 0, 0, 0))) // 86400
        await mainchannel.send(f'**{member.display_name}** был УНИЧТОЖЕН жестокой системой. Дней без проишествий:', file=number_gif(days))
        t = time.localtime(time.time())
        SQL.execute(f'UPDATE config SET value = "{t[2]}.{t[1]}.{t[0]}" WHERE name = "daykick"')
        db.commit()


@bot.event
async def on_member_update(before, after):
    if before.display_name != after.display_name:
        print(f'{before.display_name} ({before.guild.id}/{before.id}) сменил имя на {after.display_name}')
        logg(f'changename: {expd[after.guild.id][after.id].name} ({after.id}/{after.guild.id}) {before.display_name} -> {after.display_name}')
        sql_insert = 'INSERT INTO changenicks(id, server, before, after, time) VALUES (?,?,?,?,?)'
        SQL.execute(sql_insert, (after.id, after.guild.id, before.display_name, after.display_name, time.strftime("%d.%m.%Y, %X", time.localtime())))
        db.commit()


# ----------------------------------------------------------------------------------------------------------------------
# Common functions
async def vekdef(ctx):
    god = int(time.strftime('%Y'))
    vekr = adb.to_roman(god)

    daysec = (int(time.strftime('%j')) - 1) * 24 * 3600
    hoursec = int(time.strftime('%H')) * 3600
    minsec = int(time.strftime('%M')) * 60
    secsec = int(time.strftime('%S'))
    sec = daysec + hoursec + minsec + secsec
    await ctx.send(f"С начала {god} года прошло {adb.postfix(sec, ['секунда', 'секунды', 'секунд'])}")
    vek = int(sec * 99.795081967213114754098360655738) if adb.vis(god) is True else int(
        sec * 100.06575342465753424657534246575)

    year = vek // 31536000 if adb.vis(god) is True else vek // 31622400
    year = year + 100 * god - 99
    vek = vek % 31536000 + len([None for a in range(1, year % 100) if adb.vis(a) is True]) * 86400
    if vek >= 31536000 and adb.vis(year) is False:
        vek -= 31536000
        year += 1
    if vek >= 31622400:
        vek -= 31622400
        year += 1

    day = adb.day_to_day(vek // 86400 + 1, year)
    vek %= 86400
    hour = vek // 3600
    vek %= 3600
    minute = vek // 60
    vek = int(vek % 60)

    if vek < 10: vek = '0' + str(vek)
    if minute < 10: minute = '0' + str(minute)
    if hour < 10: hour = '0' + str(hour)

    await ctx.send(
        f"{random.choice(adb.veks)} **{vekr}** век, {year} год, {day}, {random.choice(adb.hours).lower()} {hour}:{minute}:{vek}")


@bot.command()
async def vek(ctx):
    await vekdef(ctx)


@bot.command()
async def help(ctx):
    helps = discord.Embed(title=random.choice(adb.helps), colour=random.choice(adb.raincolors))
    for i in range(len(adb.botcoms)):
        helps.add_field(name=f'{random.choice(adb.garbage)} #{i + 1}',
                        value=f"**{adb.botcoms[i]}**: {adb.comdescs[i]}", inline=False)
    await ctx.send(embed=helps)


@bot.command()
async def dmhelp(ctx):
    helps = discord.Embed(title=random.choice(adb.dmhelps), colour=random.choice(adb.raincolors))
    for i in range(len(adb.dmcoms)):
        helps.add_field(name=f'{random.choice(adb.garbage)} #{i + 1}',
                        value=f"**{adb.dmcoms[i]}**: {adb.dmdescs[i]}", inline=False)
    await ctx.send(embed=helps)


@bot.command()
async def uptime(ctx):
    t = int((time.time() - start_time))
    d, t = t // 86400, t % 86400
    h, t = t // 3600, t % 3600
    m, t = t // 60, t % 60
    send = random.choice(adb.uptimes) + ' '
    if d != 0: send += adb.postfix(d, ['день', 'дня', 'дней']) + ' '
    if h != 0: send += adb.postfix(h, ['час', 'часа', 'часов']) + ' '
    if m != 0: send += adb.postfix(m, ['минуту', 'минуты', 'минут']) + ' '
    send += adb.postfix(t, ['секунду', 'секунды', 'секунд'])
    await ctx.send(send)


@bot.command()
async def stol(ctx):
    await ctx.send(random.choice(adb.stoliki))


@bot.command()
async def chiefr(ctx, *words):
    words = ' '.join(words).lower()
    alphabet = {'а':'100000', 'б':'101000', 'в':'011101', 'г':'111100', 'д':'110100', 'е':'100100', 'ё':'100001', 'ж':'011100', 'з':'100111', 'и':'011000', 'й':'111011', 'к':'100010', 'л':'101010', 'м':'110010', 'н':'110110', 'о':'100110', 'п':'111010', 'р':'101110', 'с':'011010', 'т':'011010', 'у':'100011', 'ф':'111000', 'х':'101100', 'ц':'110000', 'ч':'111110', 'ш':'100101', 'щ':'110011', 'ъ':'101111', 'ы':'011011', 'ь':'011111', 'э':'011001', 'ю':'101101', 'я':'111001'}
    strings = ['','','']
    for i in words:
        if i in alphabet:
            strings[0] += alphabet[i][:2]+'  '
            strings[1] += alphabet[i][2:4]+'  '
            strings[2] += alphabet[i][4:6]+'  '
        elif i == ' ':
            strings[0] += '    '
            strings[1] += '    '
            strings[2] += '    '
    string = '\n'.join(strings)
    fin_string = ''
    for i in string:
        if i == '0':
            fin_string += '👽'
        elif i == '1':
            fin_string += '😂'
        else:
            fin_string += i
    await ctx.send(fin_string)


async def AkariCatch(mes):
    if mes.guild.id != adb.bbag:
        return
    mcl = mes.content.lower()
    for k in adb.catch:
        if ':' in k[1]:
            chance = adb.chance(int(k[1].split(':')[0]), int(k[1].split(':')[1]))
        else:
            chance = adb.chance(int(k[1]))
        if not chance:
            continue
        for i in range(2, len(k)):
            if k[i] in mcl:
                if k[0] == 'vek': await vekdef(mes.channel)
                if k[0] == 'sleep': await mes.channel.send(
                    f'{random.choice(adb.sleep)}, {rolemention(expd[mes.guild.id][mes.author.id])}')
                if k[0] == 'sleepp': await mes.channel.send(file=adb.sleeppic)
                if k[0] == 'stol': await mes.channel.send(random.choice(adb.stoliki))
                if k[0] == 'beda': await mes.channel.send(f'Беды с башкой, {rolemention(expd[mes.guild.id][mes.author.id])}')
                if k[0] == 'iq': await mes.channel.send(file=adb.iqpic)
                if k[0] == 'p': await mes.channel.send(random.choice(adb.prcatch), file=AkariCoder())
                if k[0] == 'pp': await mes.channel.send(random.choice(adb.prcatch), file=AkariCoder())
                if k[0] == 'lenyka': await mes.channel.send('Мотиватор: https://torshina.me/pizdaboliya/dodelyivat-delo-do-kontsa/')
                if k[0] == 'hello': await mes.channel.send('Я те щас помашу, пидрила 👋')
                break


@bot.command()
async def coder(ctx):
    await ctx.send(random.choice(adb.prcatch), file=AkariCoder())


async def AkariCoderEvent(mes):
    if mes.channel.id != adb.programistishe:
        return
    if not adb.chance(5):
        return
    await mes.channel.send(random.choice(adb.prcatch), file=AkariCoder())


def AkariCoder():
    file = open('pips/AkariRunaCode.txt', encoding='utf-8').read()
    file2 = open('pips/AkariRunaOnlyfuncs.txt', encoding='utf-8').read()
    file3 = open('pips/bbagdict.txt', encoding='utf-8').read()
    main = list(set(re.findall(r'[\w\.\[\]_]+', file)))
    code = list(set(file2.split(' ')))
    words = file3.split('\n')
    sym = 0
    comms = []
    res = ''

    imports = [f'import {adb.ranget(main)}' for _ in range(random.randint(2, 4))]
    if adb.chance(50):
        imports[-1] = f'from {adb.ranget(main)} import {adb.ranget(words)}'
    imports = '\n'.join(imports)
    sym += len(imports)
    comms.append(imports)

    config = '\n'.join([f'{f"{adb.ranget(main)} = "}{adb.ranget(code)}' for _ in range(random.randint(2, 5))])
    sym += len(config)
    comms.append(config)

    for _ in range(random.randint(2, 6)):
        comm = ''
        if adb.chance(67):
            if adb.chance(67):
                if adb.chance(50):
                    comm += f"@bot.event\n"
                else:
                    comm += f"@bot.command()\n"
                comm += f'async def {adb.ranget(words)}(ctx, {adb.ranget(main, random.randint(1, 3))}):\n  '
            else:
                comm += f'async def {adb.ranget(words)}({adb.ranget(main, random.randint(2, 3))}):\n  '
        else:
            comm += f'def {adb.ranget(words)}({adb.ranget(main, random.randint(2, 5))}):\n  '
        comm += '\n'.join([f'    {random.choice(["await ", f"{adb.ranget(main)} = ", f"{adb.ranget(main)} += ", "return ", f"{adb.ranget(code)} "])}{adb.ranget(code)}' for _ in range(random.randint(1, 9))])
        sym += len(comm)
        comms.append(comm)
    while sym > 1800:
        sym -= len(comms[-1])
        del comms[-1]
    text = res + '\n\n'.join(comms)
    if os.path.exists('pips/ac.py'):
        os.remove('pips/ac.py')
    file4 = open('pips/ac.py', 'a', encoding='utf-8')
    file4.write(text)
    file4.close()
    file5 = discord.File(fp='pips/ac.py')
    return file5


async def bottledef(m, g=None, channel=None):
    if not channel:
        channel = mainchannel
    if g:
        guild = bot.get_guild(g)
    else:
        guild = bbag
        g = adb.bbag
    mem = guild.get_member(m)

    bidx = random.randrange(0, len(adb.bottles))
    bottle = adb.bottles[bidx]
    fil = adb.fillers[bidx]

    if g == adb.bbag and not adb.if_host:
        role = bbag.get_role(adb.bottle_role)
        bottlecolor = random.choice(list(adb.colnames.values()))
        bottlecolor = discord.Colour.from_rgb(*bottlecolor)
        await role.edit(name=adb.randomnick_nlp(), color=bottlecolor)

    if g == adb.bbag and not adb.if_host:
        emb = discord.Embed(title='Бутылка дня', description=f'На бутылку c {bottle} сегодня садится {rolemention(expd[g][m])}\n:champagne: {fil} {fil} {fil} :champagne:\nЕму присуждается звание {role.mention}')
    else:
        emb = discord.Embed(title='Бутылка дня', description=f'На бутылку c {bottle} сегодня садится {rolemention(expd[g][m])}\n:champagne: {fil} {fil} {fil} :champagne:')

    await expd[g][m].addexp(adb.e_bottle, reason='бутылка', mem=mem)

    expd[g][m].exp['bottles'] += 1
    expd[g][m].exp['lastbottle'] = time.strftime("%d.%m.%Y, %H:%M", time.localtime())

    # purl = await picfinder('$$$')
    mems = []
    async for message in bot.get_channel(adb.impconv).history(limit=10000):
        mems += [a.url for a in message.attachments]
    if mems:
        emb.set_image(url=random.choice(mems))
    emb.set_footer(icon_url=mem.avatar_url, text=f'Опыт увеличен в {adb.ek_bottle} раза на сутки')

    for mm in expd[g]:
        expd[g][mm].bottle = False
        SQL.execute(f"UPDATE exp SET bottlednow = 0 WHERE id = {mm} AND server = {g}")
        if g == adb.bbag and not adb.if_host:
            try:
                mmem = guild.get_member(mm)
                if role in mmem.roles:
                    await mmem.remove_roles(role)
            except:
                pass
    expd[g][m].bottle = True
    SQL.execute(f"UPDATE exp SET bottlednow = 1 WHERE id = {m} AND server = {g}")
    if g == adb.bbag and not adb.if_host:
        await mem.add_roles(role)
    db.commit()
    await channel.send(embed=emb)
    AESavedef('giving a bottle')


@bot.command()
async def bottle(ctx, mem=None):
    if ctx.author.id != 262288342035595268:
        return
    if mem:
        mem = finduserindex(mem, ctx.guild.id)
        await bottledef(mem.id, ctx.guild.id, ctx.channel)
        return
    if ctx.guild.id == adb.bbag:
        mem = random.choice([i for i in expd[adb.bbag] if 0 < expd[adb.bbag][i].bbagid < 11])
    else:
        mem = random.choice(list(expd[ctx.guild.id]))
    await bottledef(mem, ctx.guild.id, ctx.channel)


@bot.command()
async def bottleregen(ctx):
    if ctx.guild.id == adb.bbag:
        role = bbag.get_role(adb.bottle_role)
        bottlecolor = random.choice(list(adb.colnames.values()))
        bottlecolor = discord.Colour.from_rgb(*bottlecolor)
        await role.edit(name=adb.randomnick_nlp(), color=bottlecolor)


@bot.command()
async def randomplay(ctx):
    mem = ctx.author
    if os.path.exists('music') and os.listdir('music') and mem:
        sound = random.choice(os.listdir('music'))
        if mem.voice.channel:
            await forceplay(sound, mem.voice.channel)
        else:
            vv = None
            vvn = -1
            for vc in mem.guild.voice_channels:
                if len(vc.members) > vvn:
                    vvn = len(vc.members)
                    vv = vc
            if vvn > 0:
                await forceplay(sound, vv)


@bot.command()
async def musplay(ctx, sound):
    mem = ctx.author
    if os.path.exists('music') and os.listdir('music') and mem:
        if not '.mp3' in sound:
            sound += '.mp3'
        if sound not in os.listdir('music'):
            await ctx.send('Такого трека нет:(', delete_after=10)
            return
        if mem.voice.channel:
            await forceplay(sound, mem.voice.channel)
        else:
            vv = None
            vvn = -1
            for vc in mem.guild.voice_channels:
                if len(vc.members) > vvn:
                    vvn = len(vc.members)
                    vv = vc
            if vvn > 0:
                await forceplay(sound, vv)


async def new_role(mes, name, color=None):
    if color in adb.colnames:
        c = adb.colnames[color]
        color = discord.Colour.from_rgb(c[0], c[1], c[2])
    else:
        color = discord.Colour.from_rgb(255, 255, 255)
    newrole = await mes.guild.create_role(name=name, color=color, reason=f'Так захотел {mes.author.nick}', mentionable=True)
    return newrole


async def rolelore(mes):
    roles = []
    text = mes.content.split('&$')
    for i, a in enumerate(text[1:]):
        color = None
        men = None
        b = a.split(' ', maxsplit=1)
        if '$' in b[0]:
            d = b[0].split('$')
            name = d[0]
            color = d[1].lower()
            try:
                men = d[2:]
            except:
                pass
        else:
            name = b[0]
        role = await new_role(mes, name, color)
        roles.append(role)
        b[0] = role.mention
        if men:
            for m in men:
                me = finduserindex(m, mes.guild.id)
                me = mes.guild.get_member(me.id)
                await me.add_roles(role, reason=f'Так захотел {mes.author.nick}')
        text[i + 1] = ' '.join(b)
    text = ''.join(text)
    await mes.channel.send(text)
    await mes.delete()
    for r in roles:
        await r.delete(reason=f'Так захотел {mes.author.nick}')


@bot.command()
async def ping(ctx):
    em = discord.Embed(title='**Текущая задержка:**', description=f'{bot.ws.latency * 1000:.0f} ms', color=random.choice(adb.raincolors))
    await ctx.send(embed=em)


@bot.command()
async def felete(ctx, file):
    if not '.' in file:
        file +='.txt'
    os.remove(file)
    await ctx.send(f'Файл {file} удалён!', delete_after=5)


@bot.command()
async def transfer(ctx, ch, count):
    ch = ctx.guild.get_channel(int(ch))
    days = False
    if 'd' in count:
        days = True
        count = count.split('d')[0]
    count = int(count)
    mess = []
    mems = []
    if days:
        if count < 1:
            await ctx.send(f'Введите количество дней')
        trans_time = datetime.datetime.now() - datetime.timedelta(days=count-1)
        async for mes in ch.history(after=trans_time):
            mess.append(mes)
        days_count = count
        count = len(mess)
    else:
        async for mes in ch.history(limit=count):
            mess.append(mes)
        days_count = 1
    mess = mess[::-1]
    for m in mess:
        cont = m.content
        # mentions = re.findall(r'<@.?>', cont)
        # print(mentions)
        # for me in mentions:
        #     me_id = re.sub(r'\D', '', me)
        #     mem = m.guild.get.member(me_id)
        #     re.sub(me, f'{mem.name}{smile(mem=mem)}', cont)
        file = None
        if m.attachments:
            a = m.attachments[0]
            if a.filename.endswith((".png", ".jpg", ".gif")):
                pic = requests.get(a.url)
                pf = open(f'{a.filename}', 'wb')
                pf.write(pic.content)
                pf.close()
                file = discord.File(fp=a.filename)
        if len(cont) > 1900:
            await ctx.send(f'`{m.author.name}`{smile(m)}, `{m.created_at.strftime("%d.%m.%Y, %X")}`')
            await ctx.send(cont, file=file)
        else:
            await ctx.send(f'`{m.author.name}`{smile(m)}, `{m.created_at.strftime("%d.%m.%Y, %X")}`\n{cont}', file=file)
        mems.append(m.author)
        await asyncio.sleep(0.5)
        if file:
            os.remove(file.fp.name)
    if count <= 5:
        return
    mems = set(mems)
    mems = [rolemention(expd[me.guild.id][me.id]) for me in mems]
    mems = '\n'.join(mems)
    desc = f'Перекинул {count} сообщений '
    if days:
        desc += f'(за {adb.postfix(days_count, ["день", "дня", "дней"])}) '
    desc += f'из {ch.mention} ({ch.guild.name})\nАвторы сообщений:\n{mems}'
    embed = discord.Embed(tile='Перенос', description=desc)
    embed.set_footer(icon_url=ctx.author.avatar_url, text=f'Вызвал: {ctx.author.name}')
    await ctx.send(embed=embed)


@bot.command()
async def tts(ctx, *text: str):
    text = ' '.join(text)
    tts = gTTS(text=text, lang="ru", lang_check=True)
    name = ctx.author.name + '.mp3'
    tts.save(name)
    file = discord.File(fp=name)
    await ctx.send(random.choice(adb.ttss), file=file)
    os.remove(name)


def casino_def():
    l = list(adb.cas_reward.keys())
    return random.choice(l), random.choice(l), random.choice(l)


@bot.command()
async def casino(ctx):
    g = ctx.guild.id
    m = ctx.author.id
    emb = discord.Embed(title='Казино 🪓🪓🪓', description='Вращайте барабан!')
    embed = await ctx.send(embed=emb)
    a, b, c = casino_def()
    mes = await ctx.send(f'{a}{b}{c}')
    for i in range(4):
        await asyncio.sleep(1)
        a, b, c = casino_def()
        await mes.edit(content=f'{a}{b}{c}')
    await mes.delete()
    if a == b and a == c:
        emb.add_field(name=f'Джекпот!', value=f'{a}{b}{c}! Ваш выигрыш: **{adb.cas_reward[a]}**')
        await expd[g][m].addexp(adb.cas_reward[a], ctx.channel, 'казино', mem=ctx.author)
        await embed.edit(embed=emb)
    else:
        emb.add_field(name=f'Неудача((', value=f'Повезёт в другой раз!\n{a}{b}{c}')
        await embed.edit(embed=emb)


@bot.command()
async def qui(ctx, *args):
    try:
        args = ' '.join(args).split('|')
        desc = args[0]
        emb = discord.Embed(title='Опрос', description=desc)
        qdict = {'desc': desc, 'author': ctx.author, 'ans': []}
        n = 0
        for i in args[1:]:
            n += 1
            ans, emo = i.split('<', maxsplit=1)
            emo = '<' + emo.split('>')[0] + '>'
            prog = '░' * 20
            perc = f'0.00%'
            emb.add_field(name=f'{n}. {ans}', value=f'{emo} {prog} {perc}', inline=False)
            emb.set_footer(icon_url=ctx.author.avatar_url, text=f'©{ctx.author.display_name}')
            qdict['ans'].append({'name': f'{n}. {ans}', 'emo': emo, 'count': 0})
        mes = await ctx.send(embed=emb)
        for i in qdict['ans']:
            await mes.add_reaction(i['emo'])
        quis[mes.id] = qdict
    except Exception as e:
        print(e)


async def AkariSwitcher(mes):
    sw = adb.switch(mes.content)
    z = zip(mes.content.lower().split(), sw.split())
    bolds = []
    for orig, trlt in z:
        pure_orig = re.sub(r'[\W\d_]', '', orig)
        pure_trlt = re.sub(r'[\W\d_]', '', trlt.lower())
        if len(pure_orig) > 3 and trlt not in bolds and not adb.find_word(pure_orig) and adb.find_word(pure_trlt):
            bolds.append(trlt)
            sw = re.sub(trlt, '**'+trlt+'**', sw)
    if bolds:
        await mes.channel.send('Akari переведёт:\n'+sw[:1900])


async def AkariCorrector(mes):
    ct = mes.content
    bolds = []
    for word in ct.split():
        pure = re.sub(r'[\W\d_]', '', word.lower())
        if len(pure) > 3 and word not in bolds and not adb.find_word(pure):
            kword = adb.correct_word(pure)
            if kword:
                bolds.append(word)
                ct = re.sub(word, '**'+adb.replace_reg(word, kword)+'**', ct)
    if bolds:
        await mes.channel.send('Очепятка, правильно:\n' + ct[:1900])


@bot.command()
async def nicks(ctx, mem=None):
    if not mem:
        mem = ctx.author
    else:
        mem = finduserindex(mem, ctx.guild.id)
        mem = ctx.guild.get_member(mem.id)
    SQL.execute(f'SELECT after, time FROM changenicks WHERE id = {mem.id} AND server = {mem.guild.id}')
    lastnicks = SQL.fetchall()[-10:]
    if not lastnicks:
        await ctx.send('Этот пользователь ещё не менял ники:(', delete_after=10)
        return
    embed = discord.Embed(title=random.choice(adb.changenicks), colour=random.choice(adb.raincolors))
    for i,t in lastnicks:
        embed.add_field(name=t, value=f'{i}{smile(mem=mem)}', inline=False)
    await ctx.send(embed=embed)


@bot.command(aliases=['cov'])
async def corona(ctx):
    browser = await launch()
    page = await browser.newPage()
    await page.goto('https://xn--80aesfpebagmfblc0a.xn--p1ai/information/')
    soup = BeautifulSoup(await page.content(), 'html.parser')
    await browser.close()

    date = str(soup.find("small").string).split('По состоянию на')[1] # FIXME: дата должна быть не вакцинации, а статы
    values = soup.find_all("h3", {"class": "cv-stats-virus__item-value"})
    values = [i.string.replace('\n', '').replace('\xa0', '') for i in values]
    values = [re.sub('\D', '', i) for i in values]
    values = values[:1]+values[1:6:2]+values[2:7:2]
    for j,t in enumerate(values):
        text = str(int(t))[::-1]
        text = ' '.join([text[i:i+3] for i in range(0, len(text), 3)])[::-1]
        values[j] = text

    heads = ['В больничку', 'Обратно', 'Заболело', 'Сдохло', 'Здоровых', 'Заболело', 'Сдохло']
    heads_icons = ['hospital', 'medcar', 'biohazard', 'skull', 'plus', 'biohazard', 'skull']

    icons = {i.split('.png')[0]: Image.open('pips/plgs/' + i).convert('RGBA') for i in os.listdir('pips/plgs')}
    font = ImageFont.truetype('pips/arial.ttf', size=55)
    fontmd = ImageFont.truetype('pips/blood.ttf', size=44)
    fontsm = ImageFont.truetype('pips/arial.ttf', size=36)

    im = Image.open(f'pips/plg.png').convert('RGBA')
    photo = random.choice(os.listdir("pips/plgphones"))
    photo = Image.open(f'pips/plgphones/{photo}').convert('RGBA')
    photo = photo.resize((445, 445))
    im.paste(photo, (137, 14), photo)
    im.paste(icons['corner1'], (137, 401), icons['corner1'])
    im.paste(icons['corner2'], (519, 14), icons['corner2'])
    im.paste(icons['corner2'], (137, 401), icons['corner2'])
    im.paste(icons['corner1'], (519, 14), icons['corner1'])

    barvalues = [int(re.sub('\D', '', i)) for i in values[3:0:-1]]
    barsum = sum(barvalues)
    covvals_pxs = [int(1700 * i / barsum) for i in barvalues]
    obj = im.load()
    px_start = 611, 368
    barsize = 1700, 86
    if sum(covvals_pxs) != barsize[0]:
        covvals_pxs[0] += barsize[0] - sum(covvals_pxs)
    xoffset = 0
    for k in range(3):
        color = [adb.colnames['серый'], adb.colnames['тёмно-красный'], adb.colnames['голубой']][k]
        color = tuple(list(color) + [255])
        for i in range(covvals_pxs[k]):
            for j in range(barsize[1]):
                ii = px_start[0] + xoffset + i
                jj = px_start[1] + j
                obj[ii, jj] = color
        xoffset += covvals_pxs[k]

    im.paste(icons['barmask'], px_start, icons['barmask'])
    draw = ImageDraw.Draw(im)
    draw.text((621, 25), 'Россия', font=font, fill=('#FFFFFE'))
    draw.text((978, 37), 'За сутки  |  Всего', font=fontmd, fill=('#FFFFFE'))
    # draw.text((1840, 37), date, font=fontmd, fill=('#FFFFFE')) # FIXME: см. выше
    draw.text((670, 130), heads[0], font=fontsm, fill=('#FFFFFE'))
    draw.text((970, 130), heads[1], font=fontsm, fill=('#FFFFFE'))
    draw.text((670, 230), heads[2], font=fontsm, fill=('#FFFFFE'))
    draw.text((970, 230), heads[3], font=fontsm, fill=('#FFFFFE'))
    draw.text((1280, 130), heads[4], font=fontsm, fill=('#FFFFFE'))
    draw.text((1280, 230), heads[5], font=fontsm, fill=('#FFFFFE'))
    draw.text((1580, 230), heads[6], font=fontsm, fill=('#FFFFFE'))

    draw.text((670, 180), values[0], font=fontsm, fill=('#FFFFFE'))
    draw.text((970, 180), values[1], font=fontsm, fill=('#FFFFFE'))
    draw.text((670, 280), values[2], font=fontsm, fill=('#FFFFFE'))
    draw.text((970, 280), values[3], font=fontsm, fill=('#FFFFFE'))
    draw.text((1280, 180), values[4], font=fontsm, fill=('#FFFFFE'))
    draw.text((1280, 280), values[5], font=fontsm, fill=('#FFFFFE'))
    draw.text((1580, 280), values[6], font=fontsm, fill=('#FFFFFE'))

    im.paste(icons[heads_icons[0]], (885, 130), icons[heads_icons[0]])
    im.paste(icons[heads_icons[1]], (1118, 130), icons[heads_icons[1]])
    im.paste(icons[heads_icons[2]], (838, 230), icons[heads_icons[2]])
    im.paste(icons[heads_icons[3]], (1100, 230), icons[heads_icons[3]])
    im.paste(icons[heads_icons[4]], (1450, 135), icons[heads_icons[4]])
    im.paste(icons[heads_icons[5]], (1448, 230), icons[heads_icons[5]])
    im.paste(icons[heads_icons[6]], (1710, 230), icons[heads_icons[6]])

    output = io.BytesIO()
    im.save(output, 'png')
    image_pix = io.BytesIO(output.getvalue())
    await ctx.send(file=discord.File(fp=image_pix, filename='corona.png'))


@bot.command()
async def whereami(ctx):
    if adb.if_host:
        await ctx.send('Я у Димы на компе!')
    else:
        await ctx.send('Я у Лёши на хосте))')


@bot.command(aliases=['rt'])
async def rantime(ctx, *args):
    args = ' '.join(args)
    t = random.choice([30, 7200, 21600, 86400, 172800])
    d, t = t // 86400, t % 86400
    h, t = t // 3600, t % 3600
    m, t = t // 60, t % 60
    send = args + ' через '
    if d != 0: send += adb.postfix(d, ['день', 'дня', 'дней']) + ' '
    if h != 0: send += adb.postfix(h, ['час', 'часа', 'часов']) + ' '
    if m != 0: send += adb.postfix(m, ['минуту', 'минуты', 'минут']) + ' '
    if t != 0: send += adb.postfix(t, ['секунду', 'секунды', 'секунд'])
    await ctx.send(send)


async def AkariCalculatingProcessor(message):
    t = message.content
    u = message.author
    errFlag = False
    if not t or t.isdigit() or t[0] == '`':  # or (not t[0].isdigit() and not t[0] == '(' and not t[0] == '#'):
        return
    if t.endswith("-err"):
        errFlag = True
        t = t.split("-err")[0]
    for i in re.findall(r'[A-Za-z]+\.[A-Za-z]+', t):
        if all(j not in i for j in ['math.', 'random.', 'adb.']):
            if 'os.' in i or 'system.' in i:
                await message.channel.send('ТЫ АХУЕЛ?', delete_after=10)
            return
    for i in ['exit', 'quit']:
        if i in t:
            await message.channel.send('ТЫ АХУЕЛ?', delete_after=10)
            return
    try:
        ACPvars['result'] = 0
        if "#" in t and not t.endswith("#"):
            t, tt = t.split("#")[:2]
            vars = {'result': 0}
            for i in tt.split(","):
                m, n = i.split("=")
                m = m.strip()
                n = n.strip()
                exec('result='+n, globals(), vars)
                ACPvars[m] = vars['result'] if not adb.is_float(vars['result']) or int(vars['result']) != float(vars['result']) else int(vars['result'])
        t = re.sub(r'==', '=', t)
        t = re.sub(r'=', '==', t)
        t = re.sub(r'\^', '**', t)
        exec('result='+t, globals(), ACPvars)
        res = ACPvars["result"] if not adb.is_float(ACPvars["result"]) or int(ACPvars["result"]) != float(ACPvars["result"]) else int(ACPvars["result"])
        await message.channel.send(f'{rolemention(expd[u.guild.id][u.id])} {res}')
    except Exception as e:
        # if errFlag or all(i not in str(e) for i in ['invalid syntax', 'is not defined', 'in identifier', 'unexpected EOF while parsing', 'invalid character', 'unmatched']):
        #     await message.channel.send(f'{get_emoji("AgroMornyX")} {e}', delete_after=10)
        pass


async def AkariMetrics(message):
    if not adb.tensor_on:
        return
    t = message.clean_content
    u = message.author
    if not t:
        return
    num = re.findall(r'[\d]+', t)
    if not num:
        return
    tl = t.split(" ")
    num = num[0]
    a = []
    for s in tl:
        reg = re.findall(r'[^\W\d_]+', s)
        if reg:
            a.append(reg[0])
    res = predictor.predict(tl)
    for i,s in enumerate(res):
        if s.pos == 'NOUN' and 'Case=Gen' in s.tag and 'Number=Plur' in s.tag:
            await message.channel.send(f'{num} {tl[i]} тебе в жопу, {rolemention(expd[u.guild.id][u.id])}')
            return


@bot.command()
async def nlp(ctx, *args):
    if not adb.tensor_on:
        return
    a = []
    for s in args:
        reg = re.findall(r'[^\W\d_]+', s)
        if reg:
            a.append(reg[0])
    res = predictor.predict(a)
    res = [adb.pretty_nlp_tag(a[i], s) for i, s in enumerate(res)]
    for i in adb.longsplit_lines(res):
        await ctx.channel.send('```py\n'+i+'```')


@bot.command()
async def make_nlp_dict(ctx, filename):
    if not adb.tensor_on:
        return
    file = open(f'pips/{filename}.txt', 'r', encoding='utf-8').readlines()
    data = adb.longsplit(file, 1000)
    nlpdict = defaultdict(list)
    counter = 0
    for i in data:
        a = [j.split('\n')[0] for j in i]
        res = predictor.predict(a)
        for j, word in enumerate(res):
            nlpdict[word.pos].append({'word': a[j], 'nform': word.normal_form})
            if word.tag != '_':
                for tag in word.tag.split('|'):
                    key, value = tag.split('=')
                    nlpdict[word.pos][-1][key] = value
        counter += 1000
        print(f"\033[33m\033[4mParsing {filename}.txt: {counter * 100 // len(file)}% done ({counter}/{len(file)})\033[0m")
    file2 = open(f'pips/{filename}nlp.txt', 'w', encoding='utf-8')
    file2.write(str(nlpdict))


@bot.command()
async def quit(ctx):
    if ctx.author.id != 262288342035595268:
        return
    os.abort()


@bot.command()
async def sayd(ctx, *args):
    m = ctx.message
    text = ' '.join(args)
    file = None
    if m.attachments:
        a = m.attachments[0]
        if a.filename.endswith((".png", ".jpg", ".gif")):
            pic = requests.get(a.url)
            pf = open(f'{a.filename}', 'wb')
            pf.write(pic.content)
            pf.close()
            file = discord.File(fp=a.filename)
    if text:
        await ctx.send(text)
    if file:
        await ctx.send(file=file)


# ----------------------------------------------------------------------------------------------------------------------
# Blackout
async def whiteoutdef(ctx):
    if not os.path.exists('whiteout.txt'):
        return
    g = ctx.guild.id
    whiteoutlist = ast.literal_eval(open('whiteout.txt', 'r', encoding='utf-8').read())
    embed = discord.Embed(title=random.choice(adb.paintlist), colour=0xfffffe)
    rest = discord.Embed(title=random.choice(adb.restlist), colour=0xfffffe)
    embedi = 1
    resti = 1
    await ctx.send(random.choice(adb.whiteouts), delete_after=10)
    for u, nick in whiteoutlist.items():
        if u in expd[g]:
            mem = ctx.guild.get_member(u)
            try:
                oldnick = rolementionfixed(expd[g][u])
                await mem.edit(nick=nick)
                await asyncio.sleep(0.5)
                embed.add_field(name=f'{random.choice(adb.people)} #{embedi}',
                                value=f"{oldnick} {random.choice(adb.calling)} **{nick}**",
                                inline=False)
                embedi += 1
            except:
                rest.add_field(name=f'{random.choice(adb.garpeople)} #{resti}',
                               value=f"{rolementionfixed(expd[g][u])} {random.choice(adb.calling)} **{nick}**",
                               inline=False)
                resti += 1
    await ctx.send(embed=embed)
    await ctx.send(embed=rest)
    os.remove('whiteout.txt')


@bot.command()
async def whiteout(ctx):
    await whiteoutdef(ctx)


@bot.command()
async def blackout(ctx, timedef=None):
    if os.path.exists('whiteout.txt'):
        await ctx.send('Дождитесь вайтаута.', delete_after=10)
        return
    g = ctx.guild.id
    whiteoutlist = {}
    embed = discord.Embed(title=random.choice(adb.paintlist), colour=0x000000)
    rest = discord.Embed(title=random.choice(adb.restlist), colour=0x000000)
    embedi = 1
    resti = 1
    await ctx.send(random.choice(adb.blackouts), delete_after=10)
    for mem in ctx.guild.members:
        u = mem.id
        if expd[g][u].name:
            whiteoutlist[u] = mem.display_name
            try:
                oldnick = rolementionfixed(expd[g][u])
                await mem.edit(nick=expd[g][u].name)
                await asyncio.sleep(0.5)
                embed.add_field(name=f'{random.choice(adb.people)} #{embedi}',
                                value=f"{oldnick} {random.choice(adb.calling)} **{expd[g][u].name}**",
                                inline=False)
                embedi += 1
            except:
                rest.add_field(name=f'{random.choice(adb.garpeople)} #{resti}',
                               value=f"{rolementionfixed(expd[g][u])} {random.choice(adb.calling)} **{expd[g][u].name}**",
                               inline=False)
                resti += 1
    await ctx.send(embed=embed)
    await ctx.send(embed=rest)
    file = open('whiteout.txt', 'w', encoding='utf-8')
    file.write(str(whiteoutlist))
    file.close()
    if timedef:
        timedef = str(timedef)
        if 'h' in timedef:
            timedef = int(timedef.split('h')[0]) * 3600
        elif 'm' in timedef:
            timedef = int(timedef.split('m')[0]) * 60
        timedef = int(timedef)
        await asyncio.sleep(timedef)
        await whiteoutdef(ctx)


@bot.command()
async def colorout(ctx, timedef=None):
    if os.path.exists('whiteout.txt'):
        await ctx.send('Дождитесь вайтаута.', delete_after=10)
        return
    g = ctx.guild.id
    whiteoutlist = {}
    embed = discord.Embed(title=random.choice(adb.paintlist), colour=0x000000)
    rest = discord.Embed(title=random.choice(adb.restlist), colour=0x000000)
    embedi = 1
    resti = 1
    await ctx.send(random.choice(adb.blackouts), delete_after=10)
    rans = [adb.randomnick_nlp() for _ in range(len(ctx.guild.members))]
    for mem in ctx.guild.members:
        u = mem.id
        whiteoutlist[u] = mem.display_name
        ran = random.choice(rans)
        rans.remove(ran)
        try:
            oldnick = rolementionfixed(expd[g][u])
            await mem.edit(nick=ran)
            await asyncio.sleep(0.5)
            embed.add_field(name=f'{random.choice(adb.people)} #{embedi}',
                            value=f"{oldnick} {random.choice(adb.calling)} **{ran}**",
                            inline=False)
            embedi += 1
        except:
            rest.add_field(name=f'{random.choice(adb.garpeople)} #{resti}',
                           value=f"{rolementionfixed(expd[g][u])} {random.choice(adb.calling)} **{ran}**",
                           inline=False)
            resti += 1
    await ctx.send(embed=embed)
    await ctx.send(embed=rest)
    file = open('whiteout.txt', 'w', encoding='utf-8')
    file.write(str(whiteoutlist))
    file.close()
    if timedef:
        timedef = str(timedef)
        if 'h' in timedef:
            timedef = int(timedef.split('h')[0]) * 3600
        elif 'm' in timedef:
            timedef = int(timedef.split('m')[0]) * 60
        timedef = int(timedef)
        await asyncio.sleep(timedef)
        await whiteoutdef(ctx)


# ----------------------------------------------------------------------------------------------------------------------
# Experience and statistics
async def AkariExp(mes):
    atts = len(mes.attachments)
    eadd = 0
    g = mes.guild.id
    m = mes.author.id
    flags = {'exp': True, 'allmessages': True}
    expd[g][m].exp['allmessages'] += 1
    expd[g][m].exp['pictures'] += atts
    if len(mes.content) > 0:
        expd[g][m].exp['messages'] += 1
        if len(mes.content) > adb.e_message * 3:
            eadd += len(mes.content)
        else:
            eadd += adb.e_message
    eadd += atts * adb.e_picture

    if atts:
        flags['pictures'] = True
    if len(mes.content) > 0:
        mat = len(adb.matcounter(mes.content))
        expd[g][m].exp['symbols'] += len(mes.content)
        flags['symbols'] = True
        if mat:
            expd[g][m].exp['mat'] += mat
            flags['mat'] = True
    await expd[g][m].addexp(eadd, mes.channel, mem=mes.author)

    if m != bot.user.id and len(mes.content) > 0:
        if mes.raw_mentions or mes.raw_role_mentions:
            roles = {expd[g][mmm].role["id"]: expd[g][mmm].id for mmm in expd[g] if 0 < expd[g][mmm].bbagid < 11}
            ids = [expd[g][mmm].id for mmm in expd[g]]
        for u in mes.raw_mentions:
            if u == m or u not in ids:
                continue
            await expd[g][u].addexp(adb.e_men, mes.channel, 'mention')
            expd[g][u].exp['mentions'] += 1
            flags['mentions'] = True
        for r in mes.raw_role_mentions:
            if not r in roles:
                continue
            u = roles[r]
            if u == m or u not in ids:
                continue
            await expd[g][u].addexp(adb.e_men, mes.channel, 'role_mention')
            expd[g][u].exp['mentions'] += 1
            flags['mentions'] = True
        smiles = Counter(re.findall(r'<:\S{,15}:\S{,20}>', mes.content))
        if smiles:
            for u in expd[g]:
                if u == m:
                    if g == adb.bbag:
                        for s in expd[g][u].emos:
                            if s in smiles:
                                ecount = smiles[s]
                                if ecount > 0:
                                    expd[g][u].exp['selfsmiles'] += ecount
                                    flags['selfsmiles'] = True
                    continue
                for s in expd[g][u].emos:
                    if s in smiles:
                        ecount = smiles[s]
                        if ecount > 0:
                            await expd[g][u].addexp(adb.e_emo * ecount, mes.channel, 'smile')
                            expd[g][u].exp['smiles'] += ecount
                            flags['smiles'] = True
    if g == adb.bbag:
        await sum_achieve(m, flags)


async def process_chaos(message):
    ctx = await bot.get_context(message)
    await bot.invoke(ctx)


async def vkExp(mes):
    text = mes.content
    if not 'α' in text:
        return
    cont = ''
    att = 0
    stick = 0
    eps = 0
    if 'ε' in text:
        eps = int(text.split('ε')[1])
        text = text.split('ε')[0]
    if 'δ' in text:
        stick = int(text.split('δ')[1])
        text = text.split('δ')[0]
    if 'γ' in text:
        att = int(text.split('γ')[1].rstrip().rstrip(','))
        text = text.split('γ')[0]
    if 'β' in text:
        cont = text.split('β')[1].rstrip().rstrip(',')
        text = text.split('β')[0]
    vkid = int(text.split('α')[1].rstrip().rstrip(','))
    eadd = 0
    g = adb.bbag
    m = 0
    if eps == 0:
        eps = len(cont)
    for mem in expd[g]:
        if expd[g][mem].vkid == vkid:
            m = mem
    if not m:
        print('Кто-то проник в беседу ВК...')
        return

    flags = {'exp': True, 'vkmes': True, 'allmessages': True}
    expd[g][m].exp['allmessages'] += 1
    expd[g][m].exp['vkmes'] += 1
    if att:
        expd[g][m].exp['pictures'] += 1
        flags['pictures'] = True
        eadd += adb.e_picture
    if stick:
        expd[g][m].exp['stickers'] += 1
        eadd += adb.e_vkstick
    if len(cont) > 0:
        expd[g][m].exp['messages'] += 1
        expd[g][m].exp['symbols'] += eps
        flags['symbols'] = True
        mat = len(adb.matcounter(cont))
        if mat:
            expd[g][m].exp['mat'] += mat
            flags['mat'] = True
        if eps > adb.e_message * 3:
            eadd += eps
        else:
            eadd += adb.e_message

    await expd[g][m].addexp(eadd, reason='вк')
    await sum_achieve(m, flags)
    if cont.startswith(adb.vk_prefix):
        if cont.startswith(adb.vk_prefix+'ds'):
            cont = cont.split(adb.vk_prefix+'ds', maxsplit=1)[1]
            if len(cont) <= 1900:
                if att:
                    file = discord.File(fp=f'vk/{att}.jpg')
                    await mainchannel.send(f'`{expd[g][m].name}`{random.choice(expd[g][m].emos)} из {emosdict[51]["vk"]}:\n{cont}', file=file)
                    os.remove(f'vk/{att}.jpg')
                else:
                    await mainchannel.send(f'`{expd[g][m].name}`{random.choice(expd[g][m].emos)} из {emosdict[51]["vk"]}:\n{cont}')
                save_vk_comm(expd[g][m], 'vk_ds')
            else:
                vka.messages.send(random_id=random.randint(0, 1000000), message='Сообщение не больше 1900 символов. Кар', chat_id=3)
        if cont.startswith(adb.vk_prefix + 'tts'):
            clean_cont = cont.split(adb.vk_prefix + 'tts', maxsplit=1)[1]
            name = expd[g][m].name + '.ogg'
            tts = gTTS(text=clean_cont, lang="ru", lang_check=True)
            tts.save(name)
            a = vka.method("docs.getMessagesUploadServer", {"type": "audio_message", "peer_id": 156809784})
            b = requests.post(a['upload_url'], files={'file': open("voice.mp3", 'rb')}).json()
            c = vka.method("docs.save", {"file": b["file"]})[0]
            d = f"doc{c['owner_id']}_{c['id']}"
            vka.messages.send(random_id=random.randint(0, 1000000), message='Ваше сообщение', chat_id=3, attachment=d)
            save_vk_comm(expd[g][m], 'vk_tts')
            os.remove(name)


def save_vk_comm(e, comm):
    print(f'{e.name} применил {comm}')
    logg(f'command_vk: {e.name} ({e.server}/{e.id}) -> {comm}')
    sql_insert = 'INSERT INTO commlog(id, server, name, command, date) VALUES (?,?,?,?,?)'
    SQL.execute(sql_insert, (e.id, e.server, e.name, comm, time.strftime("%d.%m.%Y, %X", time.localtime())))
    db.commit()


@bot.command(enabled=False)
async def aerecount(ctx, password=''):
    if password != 'ghbdtn':
        await ctx.send('Пароль неверный!', delete_after=5)
        return
    oldp = [250, 300, 120, 90, 120] #old_parameters: adb.e_message, adb.e_picture, adb.e_emo, adb.e_men, adb.e_vkstick
    for g in expd:
        for m in expd[g]:
            v = expd[g][m].exp
            oldeadd = v['messages'] * oldp[0] + v['pictures'] * oldp[1] + v['smiles'] * oldp[2] + v['mentions'] * oldp[3] + expd[g][m].exp['stickers'] * oldp[4]
            diff = expd[g][m].exp['exp'] - oldeadd
            eadd = v['messages'] * adb.e_message + v['pictures'] * adb.e_picture + v['smiles'] * adb.e_emo + v['mentions'] * adb.e_men + expd[g][m].exp['stickers'] * adb.e_vkstick
            expd[g][m].exp['exp'] = eadd + diff
    await ctx.send(f'Готово!', delete_after=5)


@bot.command()
async def aesave(ctx):
    AESavedef('user request')
    await ctx.send('Готово!', delete_after=5)


@bot.command()
async def removeexp(ctx, i, count):
    if ctx.author.id != 262288342035595268:
        return
    mem = finduserindex(i, ctx.guild.id)
    mem.exp["exp"] -= int(count)
    await ctx.send(f'{random.choice(adb.exp_removes)} Снято {count} опыта у {mem.name}{random.choice(mem.emos)}', delete_after=10)


# ----------------------------------------------------------------------------------------------------------------------
# Achievements
def sum_stats(g=adb.bbag):
    res = defaultdict(int)
    for m in expd[g]:
        for key in expd[g][m].exp:
            if type(expd[g][m].exp[key]) == int:
                res[key] += expd[g][m].exp[key]
    return res


async def sum_achieve(mem, flags):
    stats = sum_stats()
    for i in adb.sum_achieves:
        s, lv, n, t, d = i['stat'], i["levelvalue"], i["name"], i["title"], i["desc"]
        if s in flags:
            cur_levels = [a['level'] for a in achs if a['name'] == n]
            lvl = int(stats[s] // lv)
            if lvl == 0: continue
            if not cur_levels or lvl > max(cur_levels):
                nextvalue = lv * lvl
                ach = {'name': n, 'level': lvl, 'value': nextvalue, 'date': time.strftime("%d.%m.%Y, %H:%M", time.localtime()), 'owner': mem}
                achs.append(ach)
                save_achieve(ach)
                title = f"{t} {adb.to_roman(lvl)}"
                desc = d.format(nextvalue)
                purl = await picfinder(n)
                emb = discord.Embed(title='Achievement get!', description=f'**{title}**\n{desc}\nНаграду получил: {rolemention(expd[adb.bbag][mem])}')
                emb.set_image(url=purl)
                await mainchannel.send(embed=emb)
                await expd[adb.bbag][mem].addexp(adb.e_sumach+lvl*adb.e_sumach_lvladd, reason=f'{n} {adb.to_roman(lvl)}')
                AESavedef('giving sum_achieve')


def save_achieve(ach):
    sql_insert = 'INSERT INTO achs(id, server, name, level, value, date) VALUES (?,?,?,?,?,?)'
    SQL.execute(sql_insert, (ach['owner'], adb.bbag, ach['name'], ach['level'], ach['value'], ach['date']))
    db.commit()


# ----------------------------------------------------------------------------------------------------------------------
# Server/Channel statistics and saving history into file
async def channelexpdef(channel, cve, flist):
    mems = channel.guild.members
    g = channel.guild.id
    async for mes in channel.history(limit=10000000):
        atts = len(mes.attachments)
        eadd = 0
        v = mes.author.id
        if v not in cve:
            continue
        cve[v].exp['allmessages'] += 1
        cve[v].exp['pictures'] += atts
        if len(mes.content) > 0:
            cve[v].exp['messages'] += 1
            if len(mes.content) > adb.e_message * 3:
                eadd += len(mes.content)
            else:
                eadd += adb.e_message
        eadd += atts * adb.e_picture

        if g == adb.bbag:
            if len(mes.content) > 0:
                mat = len(adb.matcounter(mes.content))
                cve[v].exp['symbols'] += len(mes.content)
                if mat:
                    cve[v].exp['mat'] += mat
        cve[v].exp['exp'] += eadd

        if v != bot.user.id and len(mes.content) > 0:
            for u in mems:
                if u == mes.author:
                    if g == adb.bbag:
                        for s in flist[u.id][1]:
                            ecount = mes.content.count(s)
                            cve[u.id].exp['selfsmiles'] += ecount
                    continue
                if rolementionchat(cve[u.id]):
                    mencount = mes.content.count(flist[u.id][0])
                    cve[v].exp["exp"] += adb.e_men * mencount
                    cve[u.id].exp['mentions'] += mencount
                if f'{u.id}>' in mes.content:
                    mencount = mes.content.count(f'{u.id}>')
                    cve[v].exp["exp"] += adb.e_men * mencount
                    cve[u.id].exp['mentions'] += mencount
                for s in flist[u.id][1]:
                    ecount = mes.content.count(s)
                    cve[v].exp["exp"] += adb.e_emo * ecount
                    cve[u.id].exp['smiles'] += ecount
    return cve


@bot.command()
async def channelexp(ctx, all=''):
    stime = time.time()
    mems = ctx.guild.members
    cve = {mem.id: Vehicle([mem.id, mem.guild.id], True) for mem in mems}
    flist = {u.id: [rolementionchat(cve[u.id]), expd[u.guild.id][u.id].emos] for u in mems}
    if all == 'all':
        embed = discord.Embed(title=f'Опыт во всех каналах {ctx.guild.name}', colour=random.choice(adb.raincolors))
        for ch in ctx.guild.text_channels:
            cve = await channelexpdef(ch, cve, flist)
    else:
        cve = await channelexpdef(ctx.channel, cve, flist)
        embed = discord.Embed(title=f'Опыт в {ctx.channel.name}', colour=random.choice(adb.raincolors))
    newvehicles = aesort([cve[v] for v in cve if cve[v].exp['exp'] != 0])
    for i in newvehicles:
        text = f'{rolemention(expd[i.server][i.id])} {adb.levelget(i.exp["exp"])} уровня'
        if i.exp["allmessages"] > 0:
            text += f', сообщений: {i.exp["allmessages"]}'
        if i.exp["messages"] > 0:
            text += f', с текстом: {i.exp["messages"]}'
        if i.exp["pictures"] > 0:
            text += f', картиночек: {i.exp["pictures"]}'
        if i.exp["mentions"] > 0:
            text += f', упоминаний: {i.exp["mentions"]}'
        if i.exp["smiles"] > 0:
            text += f', смайликов с ним: {i.exp["smiles"]}'
        if i.exp["mat"] > 0:
            text += f', лексики: {i.exp["mat"]}'
        if i.exp["symbols"] > 0:
            text += f', символов: {i.exp["symbols"]}'
        if i.exp["selfsmiles"] > 0:
            text += f', смайликов с собой: {i.exp["selfsmiles"]}'
        embed.add_field(name=f'Опыт: {i.exp["exp"]}', value=text, inline=False)
    await ctx.send(embed=embed)
    await ctx.send(f'Выполнено за {time.time() - stime}', delete_after=300)
    stamp = time.time() - stime
    print(f'channelexp {all} completed by {stamp}')
    allmes = f'server {ctx.guild.id}' if all == 'all' else f'channel {ctx.channel.id}'
    logg(f'channelexp: {allmes} completed by {stamp}')


async def channelsavedef(channel, pics='', name=None):
    stime = time.time()
    cve = {}
    if not name:
        name = channel.name
    if not os.path.exists(name):
        os.mkdir(name)
    file = open(f'{name}/{name}.txt', 'w', encoding='utf-8')
    co, sum = 0, 0
    data = []
    dic = []
    dicdate = defaultdict(str)
    atts = []
    async for i in channel.history(limit=10000000):
        co += 1
        v = i.author.id
        if v not in cve:
            cve[v] = defaultdict(int)
            cve[v]['id'] = v
            cve[v]['name'] = i.author.name
            cve[v]['onserver'] = True if i.author in channel.guild.members else False
        cve[v]['allmessages'] += 1
        cve[v]['pictures'] += len(i.attachments)
        if len(i.content) > 0:
            cve[v]['messages'] += 1
            cve[v]['symbols'] += len(i.content)
            for a in i.attachments:
                atts.append(a)
                data.append(f"∭")
            data.append(f"∬{co}, {len(i.content)} sym, {len(i.content.split(' '))} words\n")
            data.append(f"∫{i.author.id}, {i.created_at.strftime('%d.%m.%Y, %X')}\n")
            data.append(f'{i.content}\n')
            sum += len(i.content)
            mes = re.sub(r'[^\s\w-]', '', re.sub('\n_', ' ', i.content))
            split = mes.split(' ')
            dic += split
            for s in split:
                dicdate[s] = i.created_at.strftime('%d.%m.%Y, %X')
            cve[v]['words'] += len(split)
        else:
            for a in i.attachments:
                atts.append(a)
                data.append("∭")
            if len(i.attachments) > 0:
                data.append(f"∬{co}\n")
                data.append(f"∫{i.author.id}, {i.created_at.strftime('%d.%m.%Y, %X')}\n")
    data = data[::-1]
    atts = atts[::-1]
    exfiles = os.listdir(name)
    if pics != 'False':
        for i, a in enumerate(atts):
            if f'{i+1}-{a.filename}' not in exfiles:
                await a.save(f'{name}/{i+1}-{a.filename}')
    att_index = 0
    for d in data:
        if d == '∭':
            wr = f"∭{name}/{att_index+1}-{atts[att_index].filename}\n"
            att_index += 1
            file.write(wr)
        else:
            file.write(d)
    words = len(dic)
    total = f"⨌{co} messages, {sum} symbols, {words} words, {round(words / (co - len(atts)), 2)} avg, {len(atts)} pics, {time.time() - stime} seconds to parse\n\n"
    file.write(total)
    cve_main = adb.esort_ext(cve, 'allmessages', 'onserver', True)
    cve_rest = adb.esort_ext(cve, 'allmessages', 'onserver', False)
    for m in cve_main:
        if m['messages'] == 0:
            file.write(
                f"∰ID {m['id']} {m['name']}: Всего сообщений: {m['allmessages']}, текстовых: {m['messages']}, картиночек: {m['pictures']}\n")
        else:
            file.write(
                f"∰ID {m['id']} {m['name']}: Всего сообщений: {m['allmessages']}, текстовых: {m['messages']}, картиночек: {m['pictures']}\n"
                f"  Символов: {m['symbols']}, слов: {m['words']}, в среднем {round(m['words'] / m['messages'], 2)} слов/сообщение\n")
    if cve_rest:
        file.write('\nНе на сервере:\n')
    for m in cve_rest:
        if m['messages'] == 0:
            file.write(
                f"⨏ID {m['id']} {m['name']}: Всего сообщений: {m['allmessages']}, текстовых: {m['messages']}, картиночек: {m['pictures']}\n")
        else:
            file.write(
                f"⨏ID {m['id']} {m['name']}: Всего сообщений: {m['allmessages']}, текстовых: {m['messages']}, картиночек: {m['pictures']}\n"
                f"  Символов: {m['symbols']}, слов: {m['words']}, в среднем {round(m['words'] / m['messages'], 2)} слов/сообщение\n")
    file = open(f'{name}/dict.txt', 'w', encoding='utf-8')
    dic = adb.ownname(Counter(dic)).most_common()
    for x in dic:
        file.write(f"{x[0]} — {adb.postfix(x[1], ('раз', 'раза', 'раз'))}, {str(round(x[1] / words * 100, 3)) + '%'} — {dicdate[x[0]]}\n")
    file.write(f"Всего: {adb.postfix(len(dic), ('слово', 'слова', 'слов'))}")
    stamp = time.time() - stime
    await channel.send(f"Готово! ❖❖❖ {co} messages, {sum} symbols, {words} words, {round(words / (co - len(atts)), 2)} avg, {len(atts)} pics ❖❖❖ Выполнено за {stamp}")
    print(f"{channel.name} channel saved! ❖❖❖ {co} messages, {sum} symbols, {words} words, {round(words / (co - len(atts)), 2)} avg, {len(atts)} pics ❖❖❖ Выполнено за {stamp}")
    logg(f"channelsave: {channel.name} ({channel.guild.id}/{channel.id}) saved with {co} mes, {sum} sym, {words} words, {round(words / (co - len(atts)), 2)} avg, {len(atts)} pics. Done for {stamp}")


@bot.command()
async def channelsave(ctx, pics='', name=None):
    await channelsavedef(ctx.channel, pics, name)


async def guildsavedef(guild, channel=None, pics='', dirr=None):
    print(f'\033[33m\033[4mStarting backup {guild.name}...\033[0m')
    logg(f'guildsave: Backup of {guild.name} ({guild.id}) started!')
    stime = time.time()
    cve = {}
    if not dirr:
        dirr = guild.name
    if not os.path.exists(dirr):
        os.mkdir(dirr)
    count, sum, all_atts = 0, 0, 0
    dic = []
    dicdate = defaultdict(str)
    for c in guild.text_channels:
        name = c.name
        print(f'\033[32m{name}... \033[0m')
        logg(f'guildsave: Backup of {name} ({guild.id}/{c.id}) started!')
        if not os.path.exists(f'{dirr}/{name}'):
            os.mkdir(f'{dirr}/{name}')
        file = open(f'{dirr}/{name}/{name}.txt', 'w', encoding='utf-8')
        data = []
        atts = []
        ch_dic = []
        ch_dicdate = defaultdict(str)
        co, sym = 0, 0
        ntime = time.time()
        async for i in c.history(limit=10000000):
            co += 1
            count += 1
            v = i.author.id
            if v not in cve:
                cve[v] = defaultdict(int)
                cve[v]['id'] = v
                cve[v]['name'] = i.author.name
                cve[v]['onserver'] = True if i.author in guild.members else False
            cve[v]['allmessages'] += 1
            cve[v]['pictures'] += len(i.attachments)
            if len(i.content) > 0:
                cve[v]['messages'] += 1
                cve[v]['symbols'] += len(i.content)
                for a in i.attachments:
                    atts.append(a)
                    data.append(f"∭")
                    all_atts += 1
                data.append(f"∬{co}, {len(i.content)} sym, {len(i.content.split(' '))} words\n")
                data.append(f"∫{i.author.id}, {i.created_at.strftime('%d.%m.%Y, %X')}\n")
                data.append(f'{i.content}\n')
                sum += len(i.content)
                sym += len(i.content)
                mes = re.sub(r'[^\s\w-]', '', re.sub('\n_', ' ', i.content))
                split = mes.split(' ')
                dic += split
                ch_dic += split
                for s in split:
                    dicdate[s] = i.created_at.strftime('%d.%m.%Y, %X')
                    ch_dicdate[s] = i.created_at.strftime('%d.%m.%Y, %X')
                cve[v]['words'] += len(split)
            else:
                for a in i.attachments:
                    atts.append(a)
                    data.append("∭")
                    all_atts += 1
                if len(i.attachments) > 0:
                    data.append(f"∬{co}\n")
                    data.append(f"∫{i.author.id}, {i.created_at.strftime('%d.%m.%Y, %X')}\n")
        data = data[::-1]
        atts = atts[::-1]
        exfiles = os.listdir(f'{dirr}/{name}')
        if pics != 'False':
            for i, a in enumerate(atts):
                if f'{i+1}-{a.filename}' not in exfiles:
                    await a.save(f'{dirr}/{name}/{i+1}-{a.filename}')
        att_index = 0
        for d in data:
            if d == '∭':
                wr = f"∭{dirr}/{name}/{att_index+1}-{atts[att_index].filename}\n"
                att_index += 1
                file.write(wr)
            else:
                file.write(d)
        ch_words = len(ch_dic)
        nstamp = time.time() - ntime
        avgsyms = str(round(ch_words / (co - len(atts)), 2)) if co - len(atts) == 0 else 'N/A'
        file.write(f"⨌{co} messages, {sym} symbols, {ch_words} words, {avgsyms} avg, {len(atts)} pics, {nstamp} seconds to parse\n")
        file = open(f'{dirr}/{name}/dict.txt', 'w', encoding='utf-8')
        ch_dic = adb.ownname(Counter(ch_dic)).most_common()
        for x in ch_dic:
            file.write(f"{x[0]} — {adb.postfix(x[1], ('раз', 'раза', 'раз'))}, {str(round(x[1] / ch_words * 100, 3)) + '%'} — {ch_dicdate[x[0]]}\n")
        file.write(f"Всего: {adb.postfix(len(ch_dic), ('слово', 'слова', 'слов'))}")
        print(f'\033[32m{name} done!\033[0m')
        logg(f'guildsave: Backup of {name} ({guild.id}/{c.id}) done with {co} mes, {sym} sym, {ch_words} words, {avgsyms} avg, {len(atts)} pics. Done for {nstamp}')
    words = len(dic)
    stamp = time.time() - stime
    total = f"⨌{count} messages, {sum} symbols, {words} words, {round(words / (count - all_atts), 2)} avg, {all_atts} pics, {stamp} seconds to parse\n\n"
    file = open(f'{dirr}/total.txt', 'w', encoding='utf-8')
    file.write(total)
    cve_main = adb.esort_ext(cve, 'allmessages', 'onserver', True)
    cve_rest = adb.esort_ext(cve, 'allmessages', 'onserver', False)
    for m in cve_main:
        if m['messages'] == 0:
            file.write(
                f"∰ID {m['id']} {m['name']}: Всего сообщений: {m['allmessages']}, текстовых: {m['messages']}, картиночек: {m['pictures']}\n")
        else:
            file.write(
                f"∰ID {m['id']} {m['name']}: Всего сообщений: {m['allmessages']}, текстовых: {m['messages']}, картиночек: {m['pictures']}\n"
                f"  Символов: {m['symbols']}, слов: {m['words']}, в среднем {round(m['words'] / m['messages'], 2)} слов/сообщение\n")
    if cve_rest:
        file.write('\nНе на сервере:\n')
    for m in cve_rest:
        if m['messages'] == 0:
            file.write(
                f"⨏ID {m['id']} {m['name']}: Всего сообщений: {m['allmessages']}, текстовых: {m['messages']}, картиночек: {m['pictures']}\n")
        else:
            file.write(
                f"⨏ID {m['id']} {m['name']}: Всего сообщений: {m['allmessages']}, текстовых: {m['messages']}, картиночек: {m['pictures']}\n"
                f"  Символов: {m['symbols']}, слов: {m['words']}, в среднем {round(m['words'] / m['messages'], 2)} слов/сообщение\n")
    file = open(f'{dirr}/dict.txt', 'w', encoding='utf-8')
    dic = adb.ownname(Counter(dic)).most_common()
    for x in dic:
        file.write(f"{x[0]} — {adb.postfix(x[1], ('раз', 'раза', 'раз'))}, {str(round(x[1] / words * 100, 3)) + '%'} — {dicdate[x[0]]}\n")
    file.write(f"Всего: {adb.postfix(len(dic), ('слово', 'слова', 'слов'))}")
    if channel:
        await channel.send(f"Готово! ❖❖❖ {count} messages, {sum} symbols, {words} words, {round(words / (count - all_atts), 2)} avg, {all_atts} pics ❖❖❖ Выполнено за {stamp}")
    print(f"{guild.name} saved! ❖❖❖ {count} messages, {sum} symbols, {words} words, {round(words / (count - all_atts), 2)} avg, {all_atts} pics ❖❖❖ Выполнено за {stamp}")
    logg(f'guildsave: Backup of {guild.name} ({guild.id}) done with {count} mes, {sum} sym, {words} words, {round(words / (count - all_atts), 2)} avg, {all_atts} pics. Done for {stamp}')


@bot.command()
async def guildsave(ctx, pics='', dirr=None):
    await guildsavedef(ctx.guild, ctx.channel, pics, dirr)


@bot.command()
async def chencounter(ctx):
    stime = time.time()
    co, sum, atts = 0, 0, 0
    dic = []
    async for i in ctx.channel.history(limit=10000000):
        if len(i.content) > 0:
            sum += len(i.content)
            co += 1
            mes = re.sub(r'[^\s\w-]', '', re.sub('\n_', ' ', i.content))
            dic += mes.split(' ')
        atts += len(i.attachments)
    words = len(dic)
    total = f"❖❖❖\nСообщений: {co}\nВсего символов: {sum}\nВсего слов: {words}\nСреднее: {round(words / co, 2)}\nВсего фоточек: {atts}"
    await ctx.send(f"{total}\n❖❖❖\nВыполнено за {time.time() - stime}")


# ----------------------------------------------------------------------------------------------------------------------
# Vehicle functions
def aesort(l):
    a = [v for v in l]
    for i in range(len(a) - 1):
        for j in range(len(a) - i - 1):
            if a[j].exp["exp"] < a[j + 1].exp["exp"]:
                a[j], a[j + 1] = a[j + 1], a[j]
    return a


def finduserindex(men, gid):
    for g in expd[gid]:
        s = expd[gid][g]
        if str(men).lower() in [f'<@!{s.id}>', f'<@{s.id}>', f'<@&{s.role["id"]}>', str(s.bbagid), s.name.lower(), str(s.id)]:
            return s
    try:
        for g in expd[gid]:
            s = expd[gid][g]
            if men.id == s.id:
                return s
        return None
    except:
        return None


def rolemention(e, opt=None):
    if e.server == adb.bbag:
        try:
            if 0 < e.bbagid < 11:
                return f'{bot.get_guild(e.server).get_role(e.role["id"]).mention}{random.choice(e.emos)}'
        except:
            return bot.get_guild(e.server).get_member(e.id).mention
    if opt:
        return f'**{opt}**'
    return bot.get_guild(e.server).get_member(e.id).mention


def rolementionfixed(e, opt=None):
    if e.server == adb.bbag:
        try:
            if 0 < e.bbagid < 11:
                return f'{bot.get_guild(e.server).get_role(e.role["id"]).mention}{random.choice(e.emos)}'
        except:
            return bot.get_guild(e.server).get_member(e.id).display_name
    if opt:
        return f'**{opt}**'
    return bot.get_guild(e.server).get_member(e.id).display_name


def rolementionchat(e):
    try:
        if e.bbagid <= 10:
            return f'<@&{e.role["id"]}>'
    except:
        return None


@bot.command()
async def exp(ctx, mem=None):
    if not mem:
        newvehicles = aesort([expd[ctx.guild.id][e] for e in expd[ctx.guild.id]])
        embed = discord.Embed(title=f'Опыт {ctx.guild.name}', colour=random.choice(adb.raincolors))
        memids = [x.id for x in ctx.guild.members]
        e = sum_stats(ctx.guild.id)
        text = f'ВСЕ<:Akari:824752874231431178>'
        text += f'   сообщений: {e["allmessages"]}'
        text += f', текстовых: {e["messages"]}'
        text += f', картиночек: {e["pictures"]}'
        text += f', упоминаний: {e["mentions"]}'
        text += f', смайликов с ним: {e["smiles"]}'
        text += f', лексики: {e["mat"]}'
        text += f', часов онлайн: {e["online"] // 60}'
        text += f', символов: {e["symbols"]}'
        text += f', смайликов с собой: {e["selfsmiles"]}'
        embed.add_field(name=f'Опыт: {e["exp"]}', value=text, inline=False)
        for i in newvehicles:
            if i.id in memids and (i.bbagid <= 10 or i.server != adb.bbag):
                e = i.exp
                lvl = adb.levelget(e["exp"], all=True)
                text = f'{rolemention(i)} {lvl[0]} уровня'
                if e['allmessages'] > 0:
                    text += f', сообщений: {e["allmessages"]}'
                if e['messages'] > 0:
                    text += f', текстовых: {e["messages"]}'
                if e["pictures"] > 0:
                    text += f', картиночек: {e["pictures"]}'
                if e["mentions"] > 0:
                    text += f', упоминаний: {e["mentions"]}'
                if e["smiles"] > 0:
                    text += f', смайликов с ним: {e["smiles"]}'
                if e["mat"] > 0:
                    text += f', лексики: {e["mat"]}'
                if e["online"] > 0:
                    online = f'{e["online"]//60}ч {e["online"]%60}мин'
                    text += f', онлайн: {online}'
                if e["symbols"] > 0:
                    text += f', символов: {e["symbols"]}'
                if e["selfsmiles"] > 0:
                    text += f', смайликов с собой: {e["selfsmiles"]}'
                prog = int(round((lvl[1] / lvl[2]) * 20))
                prog = f"{'▓' * prog}{'░' * (20 - prog)}"
                perc = f'{round((lvl[1] / lvl[2]) * 100, 2)}%'
                embed.add_field(name=f'Опыт: {e["exp"]}, {prog} {perc}', value=text, inline=False)
        await ctx.send(embed=embed)
    else:
        mem = finduserindex(mem, ctx.guild.id)
        e = mem.exp
        lvl = adb.levelget(e["exp"], all=True)
        embed = discord.Embed(title=f'{mem.name} {emosdict[mem.bbagid][random.choice(list(emosdict[mem.bbagid]))]} {lvl[0]} уровня',
                              colour=mem.role["color"])
        prog = int(round((lvl[1] / lvl[2]) * 20))
        prog = f"{'▓' * prog}{'░' * (20 - prog)}"
        perc = f'{round((lvl[1] / lvl[2]) * 100, 2)}%'
        embed.add_field(name='Прогресс', value=f'{prog} {perc}', inline=False)
        embed.add_field(name='Всего опыта', value=e["exp"], inline=True)
        if e["allmessages"] > 0:
            embed.add_field(name='Сообщений', value=e["allmessages"], inline=True)
        if e["messages"] > 0:
            embed.add_field(name='Текстовых', value=e["messages"], inline=True)
        if e["pictures"] > 0:
            embed.add_field(name='Картиночек', value=e["pictures"], inline=True)
        if e["mentions"] > 0:
            embed.add_field(name='Упоминаний', value=e["mentions"], inline=True)
        if e["smiles"] > 0:
            embed.add_field(name='Смайликов с ним', value=e["smiles"], inline=True)
        if e["mat"] > 0:
            embed.add_field(name='Лексики', value=e["mat"], inline=True)
        if e["online"] > 0:
            embed.add_field(name='Онлайн', value=f'{e["online"] // 60}ч {e["online"] % 60}мин', inline=True)
        if e["symbols"] > 0:
            embed.add_field(name='Символов', value=e["symbols"], inline=True)
        if e["selfsmiles"] > 0:
            embed.add_field(name='Смайликов с собой', value=e["selfsmiles"], inline=True)
        await ctx.send(embed=embed)
        return


# ----------------------------------------------------------------------------------------------------------------------
# TGD functions
@bot.command()
async def nikki(ctx):
    async for i in ctx.channel.history(limit=1000):
        if '▲' in i.content:
            yw = i.content.split('*Неделя* __***')[1].split('*')[0]
            ano = yw[:2]
            semana = yw[3:5]
            rd = i.content.split('РД')[0][-8:-5]
            ra = i.content.split('РА')[0][-9:-5]
            rm = i.content.split('РМ')[0][-9:-5]
            rest = i.content.split('***')[-1]
            break
    try:
        semana = int(semana) + 1
        if semana < 10:
            semana = "0" + str(semana)
        mes = '▲▼▲▼▲▼▲▼▲▼▲▼▲▼▲▼▲▼▲▼▲▼▲▼▲▼▲▼▲▼▲▼▲▼▲▼▲▼▲▼\n'
        mes += f'\*Неделя\* \_\_\*\*\*{ano}w{semana}: \*\*\*\_\_\n'
        mes += f'\*{int(rd) + 7}\* \*\*\*РД\*\*\* \*{int(ra) + 7}\* \*\*\*РА\*\*\* \*{int(rm) + 7}\* \*\*\*РМ\*\*\*'
        mes += rest
        await ctx.send(mes, delete_after=15)
    except:
        await ctx.send(file=adb.errorpic, delete_after=10)


@bot.command()
async def lognull(ctx):
    global meslogs
    global mlFlags
    lst = []
    for k, v in meslogs.items():
        if not v:
            continue
        k = bot.get_channel(k)
        fv = v[0]
        for i, e in enumerate(v):
            if i == len(v)-1 or v[i+1] - e > 300:
                lst.append((k.mention, fv, e))
                if i != len(v)-1:
                    fv = v[i+1]

    m = adb.listsplit(lst)
    for vs in m:
        emb = discord.Embed(title='Печатаем...', colour=random.choice(adb.raincolors))
        for men, fv, lv in vs:
            val = time.strftime("%d.%m.%Y, %H:%M:%S", time.localtime(fv)) if fv == lv else time.strftime("%d.%m.%Y, %H:%M:%S", time.localtime(fv))+' — '+time.strftime("%H:%M:%S", time.localtime(lv))
            emb.add_field(name=val, value=men, inline=False)
        await ctx.send(embed=emb)
    meslogs = defaultdict(list)
    mlFlags = defaultdict(bool)


async def memlog(mes):
    if (mes.channel.id in adb.mlinput) and len(mes.content) > 105:
        cout = bot.get_channel(adb.memlog)
        c = mes.content
        if '<' in c and '>' in c:
            title = f"<{c.split('<')[1].split('>')[0]}> "
        else: title = f"{c[:1]} "
        c = c.replace(title, '', 1).replace('\n', ' ')
        title += f'{random.choice(adb.letter)} {mes.channel.name}'
        emb = discord.Embed(title=title, colour=random.choice(adb.raincolors))
        d = c[:100][::-1].split(' ', maxsplit=1)[1][::-1]
        emb.add_field(name='Запись', value=d+'...', inline=False)
        emb.add_field(name='Символов', value=str(len(mes.content)), inline=True)
        emb.add_field(name='Время', value=time.strftime("%d.%m.%Y, %X", time.localtime()))
        await cout.send(embed=emb)


# ----------------------------------------------------------------------------------------------------------------------
# Emoji functions
def smile(mes=None, mem=None):
    if mem:
        obj = expd[mem.guild.id][mem.id]
    elif mes:
        obj = expd[mes.guild.id][mes.author.id]
    else:
        return
    if obj.bbagid <= 10:
        return emosdict[obj.bbagid][random.choice(list(emosdict[obj.bbagid]))]
    else:
        return ''


@bot.command()
async def newemoji(ctx, e, three=0, clas=''):
    sql_insert = 'INSERT INTO emos(emoji, eid, bbagid, server, class) VALUES (?,?,?,?,?)'
    one = e.split(':')[1]
    two = e.split(':')[2].split('>')[0]
    print(one, two)
    SQL.execute(sql_insert, (one, two, three, ctx.guild.id, clas))
    db.commit()


@bot.command()
async def emoji(ctx, e):
    u = finduserindex(e, ctx.guild.id)
    if u is not None:
        return await ctx.send(''.join(u.emos))
    return await ctx.send(get_emoji(e))


@bot.command()
async def all_emoji(ctx):
    await ctx.send('\n'.join([str(s) + '  \\' + str(s) for s in ctx.guild.emojis]))


# @bot.command()
# async def all_emojis_db(ctx):
#     sql_insert = 'INSERT INTO emos(emoji, eid, server) VALUES (?,?,?)'
#     for e in ctx.guild.emojis:
#         one = str(e).split(':')[1]
#         two = str(e).split(':')[2].split('>')[0]
#         print(one, two)
#         SQL.execute(sql_insert, (one, two, ctx.guild.id))
#         db.commit()


def get_emoji(e):
    for d in emosdict:
        for a in emosdict[d]:
            if a.lower() == e.lower():
                return emosdict[d][a]

# ----------------------------------------------------------------------------------------------------------------------
# VK commands
@bot.command()
async def vksend(ctx, *text: str, keyboard=''):
    g = ctx.guild.id
    m = ctx.author.id
    mes = expd[g][m].name
    if expd[g][m].vkemo:
        mes += expd[g][m].vkemo
    mes += ':\n'
    mes += ' '.join(text)
    att = ''
    if ctx.message.attachments:
        a = ctx.message.attachments[0]
        if a.filename.endswith((".png", ".jpg")):
            a.save(a.filename)
            b = vka.method('photos.getMessages.UploadServer', {'type': "doc", "peer_id": 156809784})
            c = requests.post(b['upload_url'], files={'photo': open(a.filename, 'rb')}).json()
            d = vka.method('photos.saveMessagesPhoto', {'photo': c['photo'], 'server': c['server'], 'hash': c['hash']})[0]
            att = f'photo{d["owner_id"]}_{d["id"]}'
            os.remove(a.filename)
        if a.filename.endswith((".docx", ".txt", ".gif")):
            a.save(a.filename)
            b = vka.method('docs.getMessagesUploadServer')
            c = requests.post(b['upload_url'], files={'file': open(a.filename, 'r')}).json()
            d = vka.method('docs.save', {'file': c['file'], 'title': a.filename})[0]
            att = f'doc{d["owner_id"]}_{d["id"]}'
            os.remove(a.filename)
        if a.filename.endswith((".mp3", ".wav", ".ogg")):
            a.save(a.filename)
            b = vka.method('audio.getUploadServer')
            c = requests.post(b['upload_url'], files={'file': open(a.filename, 'rb')}).json()
            d = vka.method('audio.save', {'audio': c['audio'], 'server': c['server'], 'hash': c['hash'], 'artist': 'BBAG', 'title': a.filename})
            att = f'photo{d["owner_id"]}_{d["id"]}'
            os.remove(a.filename)
    return vka.messages.send(user_id=156809784, message=mes, random_id=random.randint(0, 1000000), keyboard=keyboard, attachment=att)


@bot.command()
async def vk(ctx, *text: str, chat_id=3, keyboard=''):
    g = ctx.guild.id
    m = ctx.author.id
    mes = expd[g][m].name
    if expd[g][m].vkemo:
        mes += expd[g][m].vkemo
    att = ''
    if ctx.message.attachments:
        a = ctx.message.attachments[0]
        if a.filename.endswith((".png", ".jpg")):
            a.save(a.filename)
            b = vka.method('photos.getMessages.UploadServer', {'type': "doc", "peer_id": 156809784})
            c = requests.post(b['upload_url'], files={'photo': open(a.filename, 'rb')}).json()
            d = vka.method('photos.saveMessagesPhoto', {'photo': c['photo'], 'server': c['server'], 'hash': c['hash']})[0]
            att = f'photo{d["owner_id"]}_{d["id"]}'
            mes += ' прислал мемчик'
            os.remove(a.filename)
        if a.filename.endswith((".docx", ".txt", ".gif")):
            a.save(a.filename)
            b = vka.method('docs.getMessagesUploadServer')
            c = requests.post(b['upload_url'], files={'file': open(a.filename, 'r')}).json()
            d = vka.method('docs.save', {'file': c['file'], 'title': a.filename})[0]
            att = f'doc{d["owner_id"]}_{d["id"]}'
            os.remove(a.filename)
        if a.filename.endswith((".mp3", ".wav")):
            a.save(a.filename)
            b = vka.method('audio.getUploadServer')
            c = requests.post(b['upload_url'], files={'file': open(a.filename, 'rb')}).json()
            d = vka.method('audio.save',
                          {'audio': c['audio'], 'server': c['server'], 'hash': c['hash'], 'artist': 'BBAG',
                           'title': a.filename})
            att = f'photo{d["owner_id"]}_{d["id"]}'
            os.remove(a.filename)
    mes += ':\n'
    mes += ' '.join(text)
    if '@everyone' in mes:
        mes = mes.replace('@everyone', '@all')
    return vka.messages.send(random_id=random.randint(0, 1000000), message=mes, chat_id=chat_id, keyboard=keyboard, attachment=att)

# ----------------------------------------------------------------------------------------------------------------------
# Cogs

@bot.command()
async def load(ctx, extensions):
    bot.load_extension(f'cogs.{extensions}')
    await ctx.send("loaded")


@bot.command()
async def unload(ctx, extensions):
    bot.unload_extension(f'cogs.{extensions}')
    await ctx.send("unloaded")


@bot.command()
async def reload(ctx, extensions):
    bot.unload_extension(f'cogs.{extensions}')
    bot.load_extension(f'cogs.{extensions}')
    await ctx.send("reloaded")


for i in adb.cogs:
    bot.load_extension(i)
bot.load_extension('jishaku')

token = open('token.txt').readlines()[0]
bot.run(token)


