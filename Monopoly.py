import discord
from discord.ext import commands
import os
import sqlite3
import time
import shutil
import asyncio
import random
import AkariDB as adb
from _collections import defaultdict
import re
import logging

DIR = os.path.dirname(__file__)
db = sqlite3.connect(os.path.join(DIR, "Monopoly.db"))
SQL = db.cursor()
log = logging.getLogger('Monopoly')
log.setLevel(logging.INFO)
if not os.path.exists('logs'):
    os.mkdir('logs')
fh = logging.FileHandler(f'logs/Monopoly-{time.strftime("%d.%m.%Y %H.%M", time.localtime())}.txt')
fh.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
log.addHandler(fh)
moves = ['Следующим ходит: {0}', '{0}, ваш ход!']
emos = ['🤪', '🥐', '🌭', '🦄', '🤬', '🛶', '📡']
ai_names = ['Bot Dima', 'Bot Max', 'Bot Danil', 'Bot Ilyuha']
ai_emos = ['🤖', '🖲️', '🗜️', '🚽']
slap = '<:msh:830690670955331585>'
phrases = adb.phrasestxt
cube_values = ['🦯',  '🥢', '🚦', '🎛️', '🌿', '🍇']
cube_values2 = [':one:', ':two:', ':three:', ':four:', ':five:', ':six:']
cube_numbers = [':zero:', ':one:', ':two:', ':three:', ':four:', ':five:', ':six:', ':seven:', ':eight:', ':nine:']
player_colors = ['<:yellow:830416641309278238>', '<:lime:830416640939917362>', '<:red:830416640918159370>', '<:green:830416640884867072>', '<:blue:830416640805044254>', '<:orange:830416640956170240>', '<:purple:830416640428605440>']
player_color_icons = [['<:yellow1:830487866789724190>', '<:yellow2:830487866873610271>', '<:yellow3:830487867436433428>', '<:yellow4:830487867418869800>', '<:yellow5:830487867745894472>'],
                      ['<:lime1:830487866806239262>', '<:lime2:830487866890518618>', '<:lime3:830487866815414273>', '<:lime4:830487866999832596>', '<:lime5:830487868362326076>'],
                      ['<:red1:830487867008614449>', '<:red2:830487867532640340>', '<:red3:830487867016478721>', '<:red4:830487867524382800>', '<:red5:830487867813134366>'],
                      ['<:green1:830487866819608636>', '<:green2:830487866672414770>', '<:green3:830487867196178492>', '<:green4:830487866857488385>', '<:green5:830487867666071582>'],
                      ['<:blue1:830487866747387985>', '<:blue2:830487866341195777>', '<:blue3:830487867389509662>', '<:blue4:830487866698235945>', '<:blue5:830487867473395713>'],
                      ['<:orange1:830487867041644554>', '<:orange2:830487866856570891>', '<:orange3:830487867075723275>', '<:orange4:830487867205091378>', '<:orange5:830487867839086632>'],
                      ['<:purple1:830487867015823421>', '<:purple2:830487867201290320>', '<:purple3:830487867997552640>', '<:purple4:830487866827604009>', '<:purple5:830487867670265907>']]
locked_icons = ['<:yellowl:830487866849230910>', '<:limel:830487866370031627>', '<:redl:830487866944651304>', '<:greenl:830487866353516636>', '<:bluel:830487866773209106>', '<:orangel:830487866655637535>', '<:purplel:830487867012677682>']
shop_levels = ['', '¹', '²', '³', '⁴', '⁵']
all_shops = [{'name': 'Sweetees', 'length': 3, 'special': '', 'shops': [
          {'name': 'Nestle', 'mon_name': 'Sweetees', 'buyfor': 2200, 'mortgage': [0, 0, 0, 0, 0, 0], 'up': 0, 'brief': 'nes', 'special': {}},
          {'name': 'Danone', 'mon_name': 'Sweetees', 'buyfor': 1500, 'mortgage': [0, 0, 0, 0, 0, 0], 'up': 0, 'brief': 'dan', 'special': {}},
          {'name': 'Mondelez Int.', 'mon_name': 'Sweetees', 'buyfor': 1600, 'mortgage': [0, 0, 0, 0, 0, 0], 'up': 0, 'brief': 'mon', 'special': {}}]},
        {'name': 'Messengers', 'length': 4, 'special': '', 'shops': [
          {'name': 'Telegram', 'mon_name': 'Messengers', 'buyfor': 2000, 'mortgage': [0, 0, 0, 0, 0, 0], 'up': 0, 'brief': 'tel', 'special': {}},
          {'name': 'WhatsApp', 'mon_name': 'Messengers', 'buyfor': 1500, 'mortgage': [0, 0, 0, 0, 0, 0], 'up': 0, 'brief': 'wha', 'special': {}},
          {'name': 'Clubhouse', 'mon_name': 'Messengers', 'buyfor': 1400, 'mortgage': [0, 0, 0, 0, 0, 0], 'up': 0, 'brief': 'clu', 'special': {}},
          {'name': 'WeChat', 'mon_name': 'Messengers', 'buyfor': 1700, 'mortgage': [0, 0, 0, 0, 0, 0], 'up': 0, 'brief': 'wec', 'special': {}}]},
        {'name': 'CPUs', 'length': 2, 'special': '', 'shops': [
          {'name': 'Intel', 'mon_name': 'CPUs', 'buyfor': 2800, 'mortgage': [0, 0, 0, 0, 0, 0], 'up': 0, 'brief': 'int', 'special': {}},
          {'name': 'AMD', 'mon_name': 'CPUs', 'buyfor': 3600, 'mortgage': [0, 0, 0, 0, 0, 0], 'up': 0, 'brief': 'amd', 'special': {}}]},
        {'name': 'Technics', 'length': 3, 'special': '', 'shops': [
          {'name': 'Техносила', 'mon_name': 'Technics', 'buyfor': 1500, 'mortgage': [0, 0, 0, 0, 0, 0], 'up': 0, 'brief': 'tec', 'special': {'vin': 'Техносилу', 'rod': 'Техносилы'}},
          {'name': 'Эльдорадо', 'mon_name': 'Technics', 'buyfor': 2000, 'mortgage': [0, 0, 0, 0, 0, 0], 'up': 0, 'brief': 'eld', 'special': {}},
          {'name': 'М.Видео', 'mon_name': 'Technics', 'buyfor': 3200, 'mortgage': [0, 0, 0, 0, 0, 0], 'up': 0, 'brief': 'mvi', 'special': {}}]},
        {'name': 'Space', 'length': 3, 'special': '', 'shops': [
          {'name': 'SpaceX', 'mon_name': 'Space', 'buyfor': 3500, 'mortgage': [0, 0, 0, 0, 0, 0], 'up': 0, 'brief': 'spa', 'special': {}},
          {'name': 'NASA', 'mon_name': 'Space', 'buyfor': 2900, 'mortgage': [0, 0, 0, 0, 0, 0], 'up': 0, 'brief': 'nas', 'special': {}},
          {'name': 'Роскосмос', 'mon_name': 'Space', 'buyfor': 2000, 'mortgage': [0, 0, 0, 0, 0, 0], 'up': 0, 'brief': 'ros', 'special': {'rod':'Роскосмоса'}}]},
        {'name': 'Social Networks', 'length': 5, 'special': '', 'shops': [
          {'name': 'Вконтакте', 'mon_name': 'Social Networks', 'buyfor': 3000, 'mortgage': [0, 0, 0, 0, 0, 0], 'up': 0, 'brief': 'vko', 'special': {}},
          {'name': 'Facebook', 'mon_name': 'Social Networks', 'buyfor': 4000, 'mortgage': [0, 0, 0, 0, 0, 0], 'up': 0, 'brief': 'fac', 'special': {}},
          {'name': 'Reddit', 'mon_name': 'Social Networks', 'buyfor': 1800, 'mortgage': [0, 0, 0, 0, 0, 0], 'up': 0, 'brief': 'red', 'special': {}},
          {'name': 'Twitter', 'mon_name': 'Social Networks', 'buyfor': 2200, 'mortgage': [0, 0, 0, 0, 0, 0], 'up': 0, 'brief': 'twi', 'special': {}},
          {'name': 'Instagram', 'mon_name': 'Social Networks', 'buyfor': 3000, 'mortgage': [0, 0, 0, 0, 0, 0], 'up': 0, 'brief': 'ins', 'special': {}}]},
        {'name': 'Smartphones', 'length': 4, 'special': 'shuffled', 'shops': [
          {'name': 'Xiaomi', 'mon_name': 'Smartphones', 'buyfor': 4000, 'mortgage': [0, 0, 0, 0, 0, 0], 'up': 0, 'brief': 'xia', 'special': {}},
          {'name': 'Nokia', 'mon_name': 'Smartphones', 'buyfor': 2500, 'mortgage': [0, 0, 0, 0, 0, 0], 'up': 0, 'brief': 'nok', 'special': {}},
          {'name': 'Apple', 'mon_name': 'Smartphones', 'buyfor': 6000, 'mortgage': [0, 0, 0, 0, 0, 0], 'up': 0, 'brief': 'app', 'special': {}},
          {'name': 'Samsung', 'mon_name': 'Smartphones', 'buyfor': 3000, 'mortgage': [0, 0, 0, 0, 0, 0], 'up': 0, 'brief': 'sam', 'special': {}}]},
        {'name': 'Railways', 'length': 4, 'special': '', 'shops': [
          {'name': 'РЖД', 'mon_name': 'Railways', 'buyfor': 4000, 'mortgage': [0, 0, 0, 0, 0, 500], 'up': 0, 'brief': 'pzd', 'special': {}},
          {'name': 'Eurostar', 'mon_name': 'Railways', 'buyfor': 2500, 'mortgage': [0, 0, 0, 0, 0, 325], 'up': 0, 'brief': 'eur', 'special': {}},
          {'name': 'Bane NOR', 'mon_name': 'Railways', 'buyfor': 2000, 'mortgage': [0, 0, 0, 0, 0, 250], 'up': 0, 'brief': 'ban', 'special': {}},
          {'name': 'JR', 'mon_name': 'Railways', 'buyfor': 5000, 'mortgage': [0, 0, 0, 0, 0, 625], 'up': 0, 'brief': 'jr', 'special': {}}]},
        {'name': 'Cars', 'length': 2, 'special': '', 'shops': [
          {'name': 'Bentley', 'mon_name': '', 'buyfor': 4000, 'mortgage': [0, 0, 0, 0, 0, 0], 'up': 0, 'brief': 'ben', 'special': {}},
          {'name': 'Aston Martin', 'mon_name': '', 'buyfor': 4500, 'mortgage': [0, 0, 0, 0, 0, 0], 'up': 0, 'brief': 'ast', 'special': {}}]},
        {'name': 'Fastfood', 'length': 3, 'special': '', 'shops': [
          {'name': 'KFC', 'mon_name': 'Fastfood', 'buyfor': 3000, 'mortgage': [0, 0, 0, 0, 0, 0], 'up': 0, 'brief': 'kfc', 'special': {}},
          {'name': 'Burger King', 'mon_name': 'Fastfood', 'buyfor': 2000, 'mortgage': [0, 0, 0, 0, 0, 0], 'up': 0, 'brief': 'bur', 'special': {}},
          {'name': "McDonald's", 'mon_name': 'Fastfood', 'buyfor': 2600, 'mortgage': [0, 0, 0, 0, 0, 0], 'up': 0, 'brief': 'mac', 'special': {}}]},
        {'name': 'TV', 'length': 2, 'special': 'add', 'shops': [
          {'name': 'NETFLIX', 'mon_name': 'TV', 'buyfor': 2600, 'mortgage': [0, 0, 0, 0, 0, 0], 'up': 0, 'brief': 'net', 'special': {}},
          {'name': 'Walt Disney', 'mon_name': 'TV', 'buyfor': 3000, 'mortgage': [0, 0, 0, 0, 0, 0], 'up': 0, 'brief': 'dis', 'special': {}}]},
        {'name': 'Supermarkets', 'length': 4, 'special': 'add', 'shops': [
          {'name': 'Пятёрочка', 'mon_name': 'Supermarkets', 'buyfor': 3200, 'mortgage': [0, 0, 0, 0, 0, 0], 'up': 0, 'brief': 'pya', 'special': {'vin': 'Пятёрочку', 'rod':'Пятёрочки'}},
          {'name': 'Перекрёсток', 'mon_name': 'Supermarkets', 'buyfor': 2200, 'mortgage': [0, 0, 0, 0, 0, 0], 'up': 0, 'brief': 'per', 'special': {'rod':'Перекрёстка'}},
          {'name': 'Дикси', 'mon_name': 'Supermarkets', 'buyfor': 2500, 'mortgage': [0, 0, 0, 0, 0, 0], 'up': 0, 'brief': 'dik', 'special': {}},
          {'name': 'Лента', 'mon_name': 'Supermarkets', 'buyfor': 2700, 'mortgage': [0, 0, 0, 0, 0, 0], 'up': 0, 'brief': 'len', 'special': {'vin': 'Ленту', 'rod':'Ленты'}}]},
        {'name': 'Consoles', 'length': 3, 'special': 'add', 'shops': [
          {'name': 'Sony', 'mon_name': 'Consoles', 'buyfor': 4200, 'mortgage': [0, 0, 0, 0, 0, 0], 'up': 0, 'brief': 'son', 'special': {}},
          {'name': 'Microsoft', 'mon_name': 'Consoles', 'buyfor': 5000, 'mortgage': [0, 0, 0, 0, 0, 0], 'up': 0, 'brief': 'mic', 'special': {}},
          {'name': 'Nintendo', 'mon_name': 'Consoles', 'buyfor': 3000, 'mortgage': [0, 0, 0, 0, 0, 0], 'up': 0, 'brief': 'nin', 'special': {}}]},
        {'name': 'Disabled', 'length': 2, 'special': 'add', 'shops': [
          {'name': '', 'mon_name': '', 'buyfor': 0, 'mortgage': [0, 0, 0, 0, 0, 0], 'up': 0, 'brief': '', 'special': {}},
          {'name': '', 'mon_name': '', 'buyfor': 0, 'mortgage': [0, 0, 0, 0, 0, 0], 'up': 0, 'brief': '', 'special': {}}]},
        {'name': 'Disabled', 'length': 4, 'special': 'add', 'shops': [
          {'name': '', 'mon_name': '', 'buyfor': 0, 'mortgage': [0, 0, 0, 0, 0, 0], 'up': 0, 'brief': '', 'special': {}},
          {'name': '', 'mon_name': '', 'buyfor': 0, 'mortgage': [0, 0, 0, 0, 0, 0], 'up': 0, 'brief': '', 'special': {}},
          {'name': '', 'mon_name': '', 'buyfor': 0, 'mortgage': [0, 0, 0, 0, 0, 0], 'up': 0, 'brief': '', 'special': {}},
          {'name': '', 'mon_name': '', 'buyfor': 0, 'mortgage': [0, 0, 0, 0, 0, 0], 'up': 0, 'brief': '', 'special': {}}]},
        {'name': 'Coffee', 'length': 3, 'special': 'add', 'shops': [
          {'name': 'Cofix', 'mon_name': 'Coffee', 'buyfor': 1500, 'mortgage': [0, 0, 0, 0, 0, 0], 'up': 0, 'brief': 'cof', 'special': {}},
          {'name': 'Starbucks', 'mon_name': 'Coffee', 'buyfor': 2300, 'mortgage': [0, 0, 0, 0, 0, 0], 'up': 0, 'brief': 'sta', 'special': {}},
          {'name': 'Coffee Brain', 'mon_name': 'Coffee', 'buyfor': 1900, 'mortgage': [0, 0, 0, 0, 0, 0], 'up': 0, 'brief': 'cob', 'special': {}}]}]


def iconfinder(emoji):
    icons = []
    for i in range(6):
        try:
            if i == 0:
                icon = SQL.execute(f"SELECT eid FROM monop_emos WHERE emoji = '{emoji}'").fetchone()[0]
                icons.append(f'<:{emoji}:{icon}>')
            else:
                icon = SQL.execute(f"SELECT eid FROM monop_emos WHERE emoji = '{emoji}{i}'").fetchone()[0]
                icons.append(f'<:{emoji}{i}:{icon}>')
        except Exception as e:
            print(e)
    return icons


class Monopoly(commands.Cog):
    """docstring for Monopoly"""

    def __init__(self, bot):
        self.bot = bot
        self.monop_channelid = adb.monopolishe
        self.monop_channel = None
        self.maptype = 0
        self.map = None
        self.mapmes = None
        self.playmes = None
        self.infomes = None
        self.sellmes = None
        self.stockmes = None
        self.trademes = None
        self.curblock = ''
        self.players = []
        self.player_colors = []
        self.w8react = []
        self.on = False
        self.ongame = {}
        self.credits = defaultdict(dict)
        self.pledges = defaultdict(dict)
        self.stocks = []
        self.upgradeFlag = False
        self.userlist = defaultdict(dict)
        self.emosdict = defaultdict(list)
        self.emos = []
        self.ai_emos = []
        self.ai_names = []
        self.timers = []
        dbAkari = sqlite3.connect(os.path.join(DIR, "Akari.db"))
        SQLA = dbAkari.cursor()
        SQLA.execute('SELECT * FROM emos')
        emos = SQLA.fetchall()
        for e in emos:
            if e[5]:
                code = f'<a:{e[0]}:{e[1]}>'
            else:
                code = f'<:{e[0]}:{e[1]}>'
            self.emosdict[e[2]].append(code)

    async def showmap(self):
        emb = discord.Embed(title='Игроки', color=random.choice(adb.raincolors))
        for p in self.players:
            if not p.ikiru:
                text = f'Мёртв)) Очки: {p.worth}'
                emb.add_field(name=f'{p.nick}', value=text, inline=False)
                continue
            text = f'${p.money}, положение: {p.cords}\n∑{p.get_netmort()}'
            if p.credit:
                text += f', кредит: ${p.credit["money"]} ({p.credit["expires"]})'
            if p.stocks:
                text += f', акций: {len(p.stocks)})'
            text += f'\nОчки: {p.worth}'
            if p.slaps:
                text += f', {slap}{p.slaps}'
            if p.shops:
                text += f'\nСобственность: {p.show_shops()}'
            if p == self.ongame['cur_player']:
                if self.curblock:
                    emb.add_field(name=f'{p.nick}', value=text, inline=True)
                    if self.ongame['status'] == 'cubes':
                        emb.add_field(name=f'Текущий ход', value=f'Бросайте кубик!', inline=True)
                    else:
                        emb.add_field(name=f'Текущий ход', value=f'{self.curblock}', inline=True)
                    continue
            emb.add_field(name=f'{p.nick}', value=text, inline=False) # список магазов, баланс, корды и звёзды
        editFlag = False
        if self.mapmes:
            async for i in self.monop_channel.history(limit=7):
                if i.id == self.mapmes.id:
                    editFlag = True
        if editFlag:
            if self.playmes:
                try:
                    await self.playmes.edit(embed=emb)
                    if self.mapmes:
                        try:
                            await self.mapmes.edit(content=str(self.map))
                        except:
                            pass
                    else:
                        self.mapmes = await self.monop_channel.send(str(self.map))
                    return
                except:
                    pass
        if self.playmes:
            try:
                await self.playmes.delete()
            except:
                pass
        self.playmes = await self.monop_channel.send(embed=emb)
        if self.mapmes:
            try:
                await self.mapmes.delete()
            except:
                pass
        self.mapmes = await self.monop_channel.send(str(self.map))

    def update_player(self, player):
        for i, p in enumerate(self.players):
            if p.id == player.id:
                self.players[i] = player

    def finduser(self, pid):
        pid = str(pid).lower()
        for i in self.players:
            if pid in [i.name.lower(), i.men.lower(), str(i.id), i.icon.lower(), i.color.lower(), i.nick.lower()]:
                return i
            for j in [i.name.lower(), i.men.lower(), str(i.id), i.icon.lower(), i.color.lower(), i.nick.lower()]:
                if j in pid:
                    return i
        for i in self.userlist:
            if pid == str(self.userlist[i]['bbagid']) or pid in self.userlist[i]['name'].lower() or str(self.userlist[i]['roleid']) in pid:
                for p in self.players:
                    if self.userlist[i]['id'] == p.id:
                        return p

    async def action(self, mes, player, next_player):
        block = self.map.blocks[player.si]
        if block.cat == 'shop':
            if block.owner:
                if not block.buyback:
                    if block.owner.id != player.id:
                        mort = block.get_mort()
                        if player.money < mort:
                            nmort = player.get_sellmort()
                            if nmort < mort:
                                if self.ongame['crm_player']:
                                    if player != self.ongame['crm_player'] or self.ongame['criminal'] != 'polarize':
                                        mes2 = await self.monop_channel.send(f'{player.nick} не может оплатить аренду {block.rodshop} {block.owner.nick}. Скоро за ним придёт Харон')
                                        await mes2.add_reaction('💀')
                                        self.w8react.append(('death', mes2, player))
                        player.money -= mort
                        if self.ongame['crm_player']:
                            if player != self.ongame['crm_player'] and self.ongame['criminal'] == 'rob':
                                self.ongame['crm_player'].money += mort
                                self.ongame['crm_player'].worth += mort // 10
                                await self.monop_channel.send(f'{self.ongame["crm_player"].nick} украл у {player.nick} и его акционеров ${mort}')
                                self.ongame['criminal'] = ''
                                self.update_player(self.ongame['crm_player'])
                                self.ongame['crm_player'] = None
                        else:
                            for p in self.players:
                                if p.id == self.map.blocks[player.si].owner.id:
                                    p.money += mort * (100 - sum([block.stocks[a] for a in block.stocks])) // 100
                                    p.worth += mort * (100 - sum([block.stocks[a] for a in block.stocks])) // 1000
                                    p.worth += mort * 3 * sum([block.stocks[a] for a in block.stocks]) // 1000
                                    self.update_player(p)
                                if p.id in block.stocks:
                                    p.money += mort * block.stocks[p.id] // 100
                                    self.update_player(p)
                            self.map.blocks[player.si].income += mort
                            await self.monop_channel.send(f'{player.nick} платит ${mort} {block.owner.nick} в {block.vinshop}')
                    elif mes.content.lower().startswith('stocks'):
                        perc = int(mes.content.split('stocks')[1].split('%')[0])
                        if perc <= 100 - sum([block.stocks[a] for a in block.stocks]):
                            player.worth += 1000
                            self.stocks.append({'player': player.id, 'shop': block.shop, 'perc': perc, 'cost': int(block.worth * perc // 100)})
                            await self.monop_channel.send(f'{player.nick} выставил на биржу {perc}% {block.rodshop}')
            elif mes.content.lower().startswith('buy') or mes.content.lower().startswith('игн'):
                self.map.blocks[player.si].owner = player
                player.money -= block.cost
                player.shops.append(self.map.blocks[player.si])
                cur_monopoly = []
                for i in self.map.blocks:
                    if i.cat == 'shop':
                        if i.monopoly == block.monopoly:
                            cur_monopoly.append(i)
                create_monFlag = True
                for i in cur_monopoly:
                    if i.owner != player:
                        create_monFlag = False
                if create_monFlag:
                    for i in self.map.blocks:
                        if i in cur_monopoly:
                            i.in_monopoly = True
                            player.update_shop(i)
                    player.monopolies.append(block.monopoly)
                    player.worth += 1000
                player.worth += 500
                await self.monop_channel.send(f'{player.nick} покупает {block.vinshop} за ${block.cost}')
        if block.cat == 'special':
            if block.type == 1:
                jailed = [p for p in self.players if p.jailed]
                j = self.finduser(mes.content)
                if j in jailed:
                    j.slaps += 1
                    player.worth += 200
                    await self.monop_channel.send(f'{player.nick} даёт пощёчину {j.nick}')
                    self.update_player(j)
                if block.type == 2:
                    if mes.content.startswith('0'):
                        await self.monop_channel.send(f'{player.nick} не стал заряжать револьвер. Хочет сдохнуть самостоятельно')
                        block.icon = block.icons[0]
                    if mes.content.startswith('1'):
                        cont = mes.content.split('1', maxsplit=1)[1].lstrip()
                        block.icon = block.icons[1]
                        if 1 >= random.randint(1, 6):
                            mes2 = await self.monop_channel.send(f'{player.nick}, вам сопутствует удача! Вы убились с одного патрона! И, вообще-то, это был Дигл')
                            if cont:
                                await asyncio.sleep(2)
                                mes2 = await self.monop_channel.send(f'{player.nick} держал в руках прощальную записку. На ней было написано: {cont}')
                            await mes2.add_reaction('💀')
                            self.w8react.append(('suicide', mes2, player))
                        else:
                            player.worth += 100
                            player.money += 1000
                            self.update_player(j)
                            await self.monop_channel.send(f'{player.nick} зарядил револьвер с 1 патроном и, к сожалению, не убился (+${1000})')
                    if mes.content.startswith('2'):
                        cont = mes.content.split('2', maxsplit=1)[1].lstrip()
                        block.icon = block.icons[2]
                        if 2 >= random.randint(1, 6):
                            mes2 = await self.monop_channel.send(f'{player.nick} очень хотел ребёнка и сделал себе целую очередь из Узи')
                            if cont:
                                await asyncio.sleep(2)
                                mes2 = await self.monop_channel.send(f'{player.nick} оставил на столе прощальную записку. На ней было написано: {cont}')
                            await mes2.add_reaction('💀')
                            self.w8react.append(('suicide', mes2, player))
                        else:
                            player.worth += 300
                            player.money += 2000
                            self.update_player(j)
                            await self.monop_channel.send(f'{player.nick} увернулся от двух пуль из револьвера (+${2000})')
                    if mes.content.startswith('3'):
                        cont = mes.content.split('3', maxsplit=1)[1].lstrip()
                        block.icon = block.icons[3]
                        if 3 >= random.randint(1, 6):
                            mes2 = await self.monop_channel.send(f'{player.nick} купил калаш на Алиэкспрессе. Он оказался заряжен. Предохраняться {player.nick} забывает')
                            if cont:
                                await asyncio.sleep(2)
                                mes2 = await self.monop_channel.send(f'Мы нашли за шкафом прощальную записку {player.nick}. На ней было написано: {cont}')
                            await mes2.add_reaction('💀')
                            self.w8react.append(('suicide', mes2, player))
                        else:
                            player.worth += 900
                            player.money += 4000
                            self.update_player(j)
                            await self.monop_channel.send(f'{player.nick} проглотил 3 пули с железным сердечником и теперь умеет намагничивать ложки печенью (+${4000})')
                    if mes.content.startswith('4'):
                        cont = mes.content.split('4', maxsplit=1)[1].lstrip()
                        block.icon = block.icons[4]
                        if 4 >= random.randint(1, 6):
                            mes2 = await self.monop_channel.send(f'{player.nick} зарядил оружие с 4... там же дробинки... А, уже не важно ')
                            if cont:
                                await asyncio.sleep(2)
                                mes2 = await self.monop_channel.send(f'{player.nick} закопал в саду прощальную записку. На ней было написано: {cont}')
                            await mes2.add_reaction('💀')
                            self.w8react.append(('suicide', mes2, player))
                        else:
                            player.worth += 2700
                            player.money += 8000
                            self.update_player(j)
                            await self.monop_channel.send(f'{player.nick} хотел жахнуть себе в голову из дробовика, но дробовик отказался (+${8000})')
                    if mes.content.startswith('5'):
                        cont = mes.content.split('5', maxsplit=1)[1].lstrip()
                        block.icon = block.icons[5]
                        if 5 >= random.randint(1, 6):
                            mes2 = await self.monop_channel.send(f'{player.nick} достал тяжёлую артиллерию. Он не придумал, как застрелиться с минигана, уронил его на ногу, упал и ударился головой')
                            if cont:
                                await asyncio.sleep(2)
                                mes2 = await self.monop_channel.send(f'{player.nick} зашифровал прощальную записку и хранил в облаке. Наши специалисты смогли её расшифровать: {cont}')
                            await mes2.add_reaction('💀')
                            self.w8react.append(('suicide', mes2, player))
                        else:
                            player.worth += 8100
                            player.money += 16000
                            self.update_player(j)
                            await self.monop_channel.send(f'{player.nick} зарядил револьвер с 5 патронами и промахнулся, когда приставлял дуло к голове. Потом Штирлиц закрыл окно. Дуло исчезло. Хаха (+${16000})')
                    if mes.content.startswith('6'):
                        cont = mes.content.split('6', maxsplit=1)[1].lstrip()
                        block.icon = block.icons[6]
                        if adb.chance(5, 1000):
                            mes2 = await self.monop_channel.send(f'{player.nick}, жить надоело? Нельзя заряжать 6!!! А хотя почему нельзя? Вот, только сразу не ст...')
                            if cont:
                                await asyncio.sleep(2)
                                mes2 = await self.monop_channel.send(f'Среди обломков дома {player.nick} найдена прощальная записка. На ней написано: {cont}')
                            await mes2.add_reaction('💀')
                            self.w8react.append(('suicide', mes2, player))
                        else:
                            player.worth += 24300
                            player.money += 32000
                            self.update_player(j)
                            await self.monop_channel.send(f'У {player.nick} разорвалась ракета в стволе гранатомёта. К счастью, последний находился далеко в Китае. Не покупайте, всё-таки, оружие на Aliexpress (+${32000})')
                    self.map.blocks[player.si] = block
                if block.type == 4:
                    if self.ongame['criminal'] == 'bomb':
                        self.ongame['criminal'] = ''
                        self.ongame['crm_player'] = None
                        if 'bomb' in mes.content:
                            blow_to = self.finduser(mes.content.split('bomb')[1].lstrip())
                        else:
                            blow_to = self.finduser(mes.content)
                        if not blow_to.shops:
                            await self.monop_channel.send(f'Взрывать нечего((((( У {blow_to.nick} просто нет магазинов. Вместо этого террористы заплатят вам $4000')
                            player.worth += 2000
                            player.money += 4000
                            self.update_player(player)
                        else:
                            blow_what = random.choice(blow_to.shops)
                            blow_who = []
                            for p in self.players:
                                if p.cords == blow_what.cords:
                                    blow_who.append(p)
                            ruin = Special(blow_what.cords, 5)
                            ruin.desc = f'Здание фирмы {blow_what.shop} (разрушено)'
                            res = f'Здание {blow_what.rodshop} игрока {blow_to.nick} взорвано!'
                            if len(blow_who) == 1:
                                res += f' В здании находился {blow_who[0].nick}, которому {player.nick} выплатил $2000'
                            elif len(blow_who) > 1:
                                res += f' В здании находились {", ".join([p.nick for p in blow_who])}, которым {player.nick} выплатил по $2000'
                            for p in blow_who:
                                player.money -= 2000
                                p.money += 2000
                                self.update_player(p)
                            for j in range(len(self.map.blocks)):
                                if self.map.blocks[j].cords == blow_what.cords:
                                    p = self.map.blocks[j].owner
                                    wth = 2000 + int(self.map.blocks[j].worth * 1.5)
                                    p.money += self.map.blocks[j].worth // 4
                                    res += f'\n{p.nick} получил {self.map.blocks[j].worth // 4} от государства.'
                                    del p.shops[p.shops.index(self.map.blocks[j])]
                                    self.update_player(p)
                                    self.map.blocks[j] = ruin
                            res += f' {player.nick} и террористы вынесли {wth - len(blow_who) * 2000}'
                            player.worth += wth
                            player.money += wth
                            await self.monop_channel.send(res)
                    if self.ongame['criminal'] == 'stock':
                        self.ongame['criminal'] = ''
                        self.ongame['crm_player'] = None
                        if 'steal' in mes.content:
                            steal_to = self.finduser(mes.content.split('steal')[1].lstrip())
                        else:
                            steal_to = self.finduser(mes.content.split)
                        if not steal_to.shops:
                            await self.monop_channel.send(f'Красть нечего((((( У {steal_to.nick} просто нет магазинов. Вместо этого хакеры заплатят вам $1500')
                            player.worth += 750
                            player.money += 1500
                        else:
                            steal_what = random.choice(steal_to.shops)
                            for j in range(len(self.map.blocks)):
                                if self.map.blocks[j].cords == steal_what.cords:
                                    s = self.map.blocks[j]
                                    p = s.owner
                                    self.map.blocks[j].stocks[player.id] += 20
                                    p.update_shop(self.map.blocks[j])
                                    player.stocks[self.map.blocks[j].shop] += 20
                                    cur_perc = 100 - sum([s.stocks[a] for a in s.stocks])
                                    if s.stocks[player.id] > 50:
                                        if s.in_monopoly:
                                            for ss in self.map.blocks:
                                                if ss.cat == 'shop':
                                                    if ss.monopoly == s.monopoly:
                                                        ss.in_monopoly = False
                                                        p.update_shop(ss)
                                            del p.monopolies[p.monopolies.index(s.monopoly)]
                                        s.owner = player
                                        s.income = 0
                                        s.stocks[p.id] = cur_perc - 20
                                        p.stocks[self.map.blocks[j].shop] = cur_perc - 20
                                        del player.stocks[self.map.blocks[j].shop]
                                        del s.stocks[player.id]
                                        del p.shops[p.shops.index(s)]
                                        player.shops.append(s)
                                        cur_monopoly = []
                                        for ss in self.map.blocks:
                                            if ss.cat == 'shop':
                                                if s.monopoly == ss.monopoly:
                                                    cur_monopoly.append(ss)
                                        create_monFlag = True
                                        for ss in cur_monopoly:
                                            if ss.owner != player:
                                                create_monFlag = False
                                        if create_monFlag:
                                            for ss in self.map.blocks:
                                                if ss in cur_monopoly:
                                                    ss.in_monopoly = True
                                                    player.update_shop(ss)
                                            player.monopolies.append(s.monopoly)
                                            player.worth += 1000
                                        player.update_shop(s)
                                    self.update_player(p)
                                    await self.monop_channel.send(f'{player.nick} украл 20% акций компании {self.map.blocks[j].shop}')
                                    player.worth += 500
                                    break
        self.curblock = self.map.blockinfo(player, self.players)
        self.map.show_colors(next_player)
        player.update_shop(self.map.blocks[player.si])
        self.update_player(player)

    async def cubes(self, mes, player):
        count = player.cubes
        random.seed(mes.content)
        vs = [random.randint(1, 6) for _ in range(count)]
        cubes = [Cube(vs[i]) for i in range(count)]
        self.map.inject_cubes(cubes, sum(vs))
        self.map.move_player(player, sum(vs))
        self.curblock = self.map.blockinfo(player, self.players)
        self.map.show_shops(self.players, player)
        player.update_shop(self.map.blocks[player.si])
        self.update_player(player)
        await self.showmap()

    def eclevel(self, ai):
        for i in ai.shops:
            if i.buyback:
                return 0
        if self.ongame['round'] < 20:
            return 3
        if ai.monopolies:
            return 3
        return 2

    async def ai_processing(self, ai, mode, mes):
        await asyncio.sleep(1)
        log.info(re.sub(r'\W', '', f"{ai.nick} {mode} AIp"))
        if mode == 'idle':
            await self.monop_channel.send(f'ЪУЪ ↯AI{ai.id}')
        if mode == 'cubes':
            phrase = random.choice(phrases)
            if ai.jailed:
                phrase = 'aaa ' + phrase
            phrase = phrase.replace('\n', '') + '↯AI'
            await self.monop_channel.send(phrase)
            log.info(re.sub(r'\W', '', phrase))
        if mode == 'buystock':
            if self.eclevel(ai) > 0:
                if ai.money < mes['cost']:
                    if self.ongame['round'] >= 10 and not self.credits[ai.id] and ai.money + 10000 >= mes['cost']:
                        await self.monop_channel.send(f'credit 10000 ↯AI{ai.id}')
                        log.info(re.sub(r'\W', '', f'credit 10000 ↯AI{ai.id}'))
                        await asyncio.sleep(1)
                        await self.monop_channel.send(f'buystock {mes["shop"]} ↯AI{ai.id}')
                        log.info(re.sub(r'\W', '', f'buystock {mes["shop"]} ↯AI{ai.id}'))
                else:
                    await self.monop_channel.send(f'buystock {mes["shop"]} ↯AI{ai.id}')
                    log.info(re.sub(r'\W', '', f'buystock {mes["shop"]} ↯AI{ai.id}'))
        if mode == 'stocks':
            if self.eclevel(ai) > 2:
                await self.monop_channel.send(f'↯AI{ai.id} stock 25%')
                log.info(re.sub(r'\W', '', f'↯AI{ai.id} stock 25%'))
            else:
                await self.monop_channel.send(f'↯AI{ai.id} pass')
                log.info(re.sub(r'\W', '', f'↯AI{ai.id} pass'))
        if mode == 'buy':
            if self.eclevel(ai) > 1:
                if ai.money < mes:
                    if self.ongame['round'] >= 10 and not self.credits[ai.id]:
                        await self.monop_channel.send(f'credit 10000 ↯AI{ai.id}')
                        log.info(re.sub(r'\W', '', f'credit 10000 ↯AI{ai.id}'))
                        await asyncio.sleep(1)
                        await self.monop_channel.send(f'buy ↯AI{ai.id}')
                        log.info(re.sub(r'\W', '', f'buy ↯AI{ai.id}'))
                    else:
                        await self.monop_channel.send(f'↯AI{ai.id} pass')
                        log.info(re.sub(r'\W', '', f'↯AI{ai.id} pass'))
                else:
                    await self.monop_channel.send(f'buy ↯AI{ai.id}')
                    log.info(re.sub(r'\W', '', f'buy ↯AI{ai.id}'))
            else:
                await self.monop_channel.send(f'↯AI{ai.id} pass')
                log.info(re.sub(r'\W', '', f'↯AI{ai.id} pass'))
        if mode == 'slap':
            await self.monop_channel.send(f'{random.choice([a for a in self.players if a.jailed]).name} НЫЫЫАААААААААА ↯AI')
            log.info(re.sub(r'\W', '', f'{random.choice([a for a in self.players if a.jailed]).name} НЫЫЫАААААААААА ↯AI'))
        if mode == 'roulette':
            ec = self.eclevel(ai)
            if ec == 0:
                await self.monop_channel.send(f'2 Несчастная Смерть, теперь тебе не по силам противостоять восставшим против тебя могучим технологиям видоизмененного углерода, позволившим оцифровывать человеческий рассудок и загружать его в новую оболочку. Когда-то мы жили, с ужасом ожидая твоего появления. Теперь мы отчаянно флиртуем с тобой, мрачной старухой, а сильные мира сего не подпускают тебя даже к чёрному входу» ©Видоизменённый углерод, Ричард Морган ↯AI')
                log.info(re.sub(r'\W', '', f'2 Длиный мессадж.txt ↯AI'))
            if ec == 1:
                await self.monop_channel.send(f'1 Да как так то... ↯AI')
                log.info(re.sub(r'\W', '', f'1 Да как так то... ↯AI'))
            else:
                await self.monop_channel.send(f'0 Я ещё поживу)) ↯AI')
                log.info(re.sub(r'\W', '', f'0 Я ещё поживу)) ↯AI'))
        if mode == 'bomb':
            await self.monop_channel.send(f'↯AI bomb {random.choice([a for a in self.players if a.id != ai.id and a.ikiru]).name}')
            log.info(re.sub(r'\W', '', f'↯AI bomb {random.choice([a for a in self.players if a.id != ai.id and a.ikiru]).name}'))
        if mode == 'steal':
            await self.monop_channel.send(f'↯AI steal {random.choice([a for a in self.players if a.id != ai.id and a.ikiru]).name}')
            log.info(re.sub(r'\W', '', f'↯AI steal {random.choice([a for a in self.players if a.id != ai.id and a.ikiru]).name}'))
        if mode == 'pay':
            if ai.money < mes:
                if self.ongame['round'] >= 10 and not self.credits[ai.id] and ai.money + 10000 >= mes:
                    await self.monop_channel.send(f'credit 10000 ↯AI{ai.id}')
                    log.info(re.sub(r'\W', '', f'credit 10000 ↯AI{ai.id}'))
                    await asyncio.sleep(1)
                    await self.monop_channel.send(f'Затянем ремешки... ↯AI{ai.id}')
                    log.info(re.sub(r'\W', '', f'Затянем ремешки... ↯AI{ai.id}'))
                else:
                    tosell, pleds = ai.to_sell(ai=ai)
                    diff = mes - ai.money
                    while diff > 0:
                        if self.ongame['round'] >= 10 and not self.credits[ai.id] and ai.money + 10000 >= mes:
                            await self.monop_channel.send(f'credit 10000 ↯AI{ai.id}')
                            log.info(re.sub(r'\W', '', f'credit 10000 ↯AI{ai.id}'))
                            await asyncio.sleep(1)
                        elif not tosell and not pleds:
                            await self.monop_channel.send(f'Похоже, это конец... ↯AI{ai.id}')
                            log.info(re.sub(r'\W', '', f'Похоже, это конец... ↯AI{ai.id}'))
                            return
                        if not tosell:
                            pleds_nomons = [s for s in pleds if not s.in_monopoly]
                            if pleds_nomons:
                                s = random.choice(pleds_nomons)
                            else:
                                s = random.choice(pleds)
                            ai.money += int(s.cost * 0.5)
                            s.buyback = True
                            for i in self.map.blocks:
                                if i.cat == 'shop':
                                    if i.monopoly == s.monopoly:
                                        i.in_monopoly = False
                                        ai.update_shop(i)
                            if s.monopoly in ai.monopolies:
                                del ai.monopolies[ai.monopolies.index(s.monopoly)]
                            self.pledges[ai.id][s.shop] = 20
                            await self.monop_channel.send(f'{ai.nick} закладывает {s.vinshop}')
                            for j in range(len(self.map.blocks)):
                                ss = self.map.blocks[j]
                                if ss.cat == 'shop':
                                    if ss.shop == s.shop:
                                        self.map.blocks[j] = s
                            ai.update_shop(s)
                            self.update_player(ai)
                            diff -= int(s.cost * 0.5)
                            del pleds[pleds.index(s)]
                        else:
                            s = random.choice(tosell)
                            ai.money += int(s.up * 0.5)
                            s.level -= 1
                            s.worth -= s.up
                            s.icon = s.icons[s.level]
                            await self.monop_channel.send(f'{ai.nick} продаёт {s.level + 1} филиал {s.rodshop}')
                            for j in range(len(self.map.blocks)):
                                ss = self.map.blocks[j]
                                if ss.cat == 'shop':
                                    if ss.shop == s.shop:
                                        self.map.blocks[j] = s
                            ai.update_shop(s)
                            self.update_player(ai)
                            diff -= int(s.up * 0.5)
                            del tosell[tosell.index(s)]
                    await self.monop_channel.send(f'Продаю самое дорогое ↯AI{ai.id}')
                    log.info(re.sub(r'\W', '', f'Продаю самое дорогое ↯AI{ai.id}'))
            else:
                if adb.chance(20):
                    await self.monop_channel.send(f'НЕ ХОЧУ Я ПЛАТИТЬ ↯AI{ai.id}')
                    log.info(re.sub(r'\W', '', f'НЕ ХОЧУ Я ПЛАТИТЬ ↯AI{ai.id}'))
                else:
                    await self.monop_channel.send(f'pay ↯AI{ai.id}')
                    log.info(re.sub(r'\W', '', f'pay ↯AI{ai.id}'))
        if mode == 'up':
            toup, backs = ai.to_upgrade(ai=ai)
            ec = self.eclevel(ai)
            if ec > 0:
                async def ai_toup(ai, toup):
                    s = ''
                    toup = adb.esortatte(toup, 'level', True)
                    toup_topmon = [s for s in toup if s.monopoly == toup[0].monopoly]
                    if toup_topmon:
                        for i in random.shuffle(toup_topmon):
                            if ai.money >= i.up:
                                s = i
                                break
                    if not s:
                        if toup_topmon:
                            for i in random.shuffle(toup_topmon):
                                if ai.money >= i.up:
                                    s = i
                                    break
                    if s:
                        ai.money -= s.up
                        s.level += 1
                        s.worth += s.up
                        s.icon = s.icons[s.level]
                        self.upgradeFlag = False
                        ai.worth += 250
                        await self.monop_channel.send(f'{ai.nick} строит {s.level} филиал {s.rodshop}')
                        for j in range(len(self.map.blocks)):
                            ss = self.map.blocks[j]
                            if ss.cat == 'shop':
                                if ss.shop == s.shop:
                                    self.map.blocks[j] = s
                        ai.update_shop(s)
                        self.update_player(ai)

                async def ai_backs(ai, backs):
                    if backs:
                        for i in adb.esortatte(backs, 'cost'):
                            if ai.money >= int(i.cost * 0.6):
                                ai.money -= int(s.cost * 0.6)
                                s.buyback = False
                                s.icon = s.icons[s.level]
                                cur_monopoly = []
                                for i in self.map.blocks:
                                    if i.cat == 'shop':
                                        if i.monopoly == s.monopoly:
                                            cur_monopoly.append(i)
                                create_monFlag = True
                                for i in cur_monopoly:
                                    if i.owner != ai:
                                        create_monFlag = False
                                if create_monFlag:
                                    for i in self.map.blocks:
                                        if i in cur_monopoly:
                                            i.in_monopoly = True
                                            ai.update_shop(i)
                                    ai.monopolies.append(s.monopoly)
                                    ai.worth += 1000
                                await self.monop_channel.send(f'{ai.nick} выкупил {s.vinshop}')
                                for j in range(len(self.map.blocks)):
                                    ss = self.map.blocks[j]
                                    if ss.cat == 'shop':
                                        if ss.shop == s.shop:
                                            self.map.blocks[j] = s
                                ai.update_shop(s)
                                self.update_player(ai)

                if ec > 1:
                    if self.ongame['round'] >= 10 and not self.credits[ai.id]:
                        await self.monop_channel.send(f'credit 10000 ↯AI{ai.id}')
                        log.info(re.sub(r'\W', '', f'credit 10000 ↯AI{ai.id}'))
                        await asyncio.sleep(1)
                    await ai_backs(ai, backs)
                    await ai_toup(ai, toup)
                if ec == 1:
                    await ai_toup(ai, toup)
                    await ai_backs(ai, backs)

    async def passion(self, mes):
        player = self.ongame['cur_player']
        next_player = self.players[self.ongame['cp_id']]
        block = self.map.blocks[player.si]
        pol = player.money
        polFlag = False
        if block.cat == 'special':
            if block.type == 0:
                player.money += 250*player.circle
                player.worth += 250
                await self.monop_channel.send(f'{player.nick}: +${250*player.circle} за стартовое поле {player.circle} круга')
            if block.type == 1:
                jailed = [p.name for p in self.players if p.jailed]
                if jailed:
                    await self.monop_channel.send(f'Напишите имя заключённого, чтобы дать ему пощёчину')
                    if player.AI:
                        await self.ai_processing(self.ongame['cur_player'], 'slap', '')
                    return
            if block.type == 2:
                await self.monop_channel.send(f'Вы нашли револьвер! Введите количество патронов. Ну, и сообщение на прощание')
                if player.AI:
                    await self.ai_processing(self.ongame['cur_player'], 'roulette', '')
                return
            if block.type == 3:
                await self.monop_channel.send(f'{player.nick} садится в тюряжку за репост шутки про {random.choice(["котиков", "Илона Макса", "Gachi", "BBAG"])}')
                player.jailed = True
                for j in self.map.blocks:
                    if j.cat =='special':
                        if j.type == 1:
                            player.cords = j.cords
                self.timers.append({'name': 'jail', 'expires': 3, 'player': player})
            if block.type == 4:
                self.ongame['crm_player'] = player
                self.ongame['crm_player'] = player
                if self.ongame['criminal']:
                    await self.monop_channel.send(f'В городе сменился криминальный авторитет. Бонусы предыдущего пропадают')
                if adb.chance(2):
                    await self.monop_channel.send(f'{player.nick},\nВы видите это письмо, потому что мы решили обратиться к вам. Видите всех этих людей, стремящихся установить монополию на рынках? Мы считаем, что подобной политики на наших улицах быть не должно. Кто, на ваш взгляд, наиболее опасен для экономики? Мы — независимая организация, действующая анонимно. Мы предлагаем вам выбрать цель для закладки бомбы.\n'
                                                  f'Условия следующие:\n Выберите игрока. Через 2 хода бомба взорвётся в одном из его магазинов.\nГосударство возместит ему небольшую сумму, но наша с вами выгода будет гораздо больше.\n'
                                                  f'Вы получите большое количество активов игрока, которые наши специалисты добудут во время выполнения операции\nЕсли в компании в момент взрыва будут находиться другие игроки, вы также будете должны выплатить им компенсацию. Но риски невелики, выбирайте с умом.\nВо вложении мы отправили форму, в которой вы должны прислать ответ — цель теракта.\nНе отвечайте на это сообщение. Не пытайтесь найти нас. Рады сотрудничеству.\n\n`bomb <имя или id игрока>`')
                    self.ongame['criminal'] = 'bomb'
                    if player.AI:
                        await self.ai_processing(self.ongame['cur_player'], 'bomb', '')
                    return
                elif adb.chance(10):
                    await self.monop_channel.send(f'{player.nick}, российские хакеры предлагают вам украсть акции компании одного из игроков. Выберите игрока: `steal <имя или id игрока>`')
                    self.ongame['criminal'] = 'stocks'
                    if player.AI:
                        await self.ai_processing(self.ongame['cur_player'], 'steal', '')
                    return
                elif adb.chance(55):
                    await self.monop_channel.send(f'{player.nick}, если на следующий ход вы потеряете или потратите деньги, вместо этого вам прибавится такое же их количество (действует 1 раз)')
                    self.ongame['criminal'] = 'polarize'
                    polFlag = True
                else:
                    await self.monop_channel.send(f'{player.nick}, вы заберёте себе следующую полученную магазином другого игрока прибыль')
                    self.ongame['criminal'] = 'rob'
        if block.cat == 'bonus':
            if adb.chance(14):
                for p in self.players:
                    if player.id != p.id:
                        p.money -= 500
                        self.update_player(p)
                player.money += 500 * (len(self.players) - 1)
                await self.monop_channel.send(f'{player.nick} отмечает день рождения. Все остальные игроки скидываются ему по $500 на Папу Джонса')
            elif adb.chance(16):
                self.map.move_player(player, random.randint(10, 18))
                await self.monop_channel.send(f'{player.nick} тестирует новые способы телепортации')
            elif adb.chance(20):
                player.money += 1000
                await self.monop_channel.send(f'{player.nick} идёт рыться в помойке за ресторанчиком и находит $1000... И {random.choice(["рыбный торт", "жареные бананы", "мозги в томатном соусе", "чай с кетчупом"])}')
            elif adb.chance(24):
                count = 0
                for s in player.shops:
                    count += s.level
                player.money += 250 * count
                await self.monop_channel.send(f'{player.nick} получает $250 за каждую свою звезду. Всего ${250 * count}')
            elif adb.chance(32):
                player.worth += 1000
                player.slaps += 1
                await self.monop_channel.send(f'{player.nick} отказал девушке в свидании. Он получает 1000 очков и пощёчину')
            elif adb.chance(40):
                ran_moves = random.randint(2,3)
                await self.monop_channel.send(f'{player.nick} получает третий кубик на {ran_moves} хода')
                player.cubes = 3
                self.timers.append({'name': 'cube', 'expires': ran_moves, 'player': player})
            elif adb.chance(85):
                count = int(player.money * 0.3)
                player.money += count
                await self.monop_channel.send(f'{player.nick} поставил часть своих денег в казино и выиграл! +${count}')
            else:
                if not player.shops:
                    shop_list = []
                    for j in self.map.blocks:
                        if block.cat == 'shop':
                            if not block.owner:
                                shop_list.append(j)
                    if shop_list:
                        s = random.choice(shop_list)
                        s.owner = player
                        player.shops.append(s)
                        player.worth += 500
                        await self.monop_channel.send(f'{player.nick} поймал падающую с неба звезду. Он положил её под подушку, и на следующий день у него появился магазин')
                    else:
                        await self.monop_channel.send(f'{player.nick} поймал падающую с неба звезду. Он положил её под подушку, и на следующий день там лежало $3000')
                        player.money += 3000
                else:
                    await self.monop_channel.send(f'{player.nick} поймал падающую с неба звезду. Она пойдёт в один из его магазинов')
                    shop_list = []
                    for j in self.map.blocks:
                        if block.cat == 'shop':
                            if block.owner == player:
                                shop_list.append(j)
                    if not shop_list:
                        await self.monop_channel.send(f'Bugreport #001 {player.nick}')
                    else:
                        s = random.choice(shop_list)
                        s.level += 1
                        s.worth += s.up
                        s.icon = s.icons[s.level]
                        player.worth += 250
        if block.cat == 'anti':
            if adb.chance(14):
                count = len(player.monopolies)
                player.money -= 1000 * count
                await self.monop_channel.send(f'{player.nick} платит по $1000 за каждую свою монополию. Всего ${1000 * count}')
            elif adb.chance(16):
                count = 0
                for s in player.shops:
                    count += s.level
                player.money -= 250 * count
                await self.monop_channel.send(f'{player.nick} платит $250 за каждую свою звезду. Всего ${250 * count}')
            elif adb.chance(20):
                count = len([p for p in self.players if p.ikiru])
                player.money -= 500 * count
                await self.monop_channel.send(f'{player.nick} платит $500 за каждого игрока. Всего ${500 * count}')
            elif adb.chance(24):
                count = int(player.money * 0.3)
                player.money -= count
                await self.monop_channel.send(f'У {player.nick} украли с карточки ${count}')
            elif adb.chance(32):
                count = player.worth // 7
                player.money -= count
                await self.monop_channel.send(f'{player.nick} вынужден отдать акционерам сумму, пропорциональную его очкам: ${count}')
            elif adb.chance(40):
                count = 0
                for s in self.map.blocks:
                    if s.cat == 'shop':
                        count += len(s.stocks)
                player.money -= 250 * count
                await self.monop_channel.send(f'Обвал биржи! {player.nick} отдаёт сумму, пропорциональную размеру биржи: ${250 * count}')
            elif adb.chance(85):
                await self.monop_channel.send(f'{player.nick} попался на махинациях с акциями в Пятёрочке и сядет в тюрьму на 4 хода')
                player.jailed = True
                for j in self.map.blocks:
                    if j.cat == 'special':
                        if j.type == 1:
                            player.cords = j.cords
                self.timers.append({'name': 'jail', 'expires': 5, 'player': player})
            else:
                if not player.shops:
                    await self.monop_channel.send(f'{player.nick} нашёл зелёный светящийся камень. Он уже хотел было дотронуться до него, но услышал полицейские сирены и сбежал')
                    player.worth += 1000
                else:
                    shop_one = random.choice(player.shops)
                    shops_f2 = []
                    shops_f3 = []
                    for j in self.map.blocks:
                        if j.cat == 'shop':
                            if j.shop == shop_one:
                                shop_one = j
                            if j.owner == None:
                                shops_f2.append(j)
                            elif j.owner != player:
                                shops_f3.append(j)
                    if shops_f2:
                        shop_two = random.choice(shops_f2)
                    else:
                        shop_two = random.choice(shops_f3)
                    cords = shop_one.cords
                    shop_one.cords = shop_two.cords
                    shop_two.cords = cords
                    shop_one.anomale = True
                    shop_two.anomale = True
                    for j in range(len(self.map.blocks)):
                        if self.map.blocks[j].cat == 'shop':
                            if self.map.blocks[j].shop == shop_one.shop:
                                self.map.blocks[j] = shop_two
                            elif self.map.blocks[j].shop == shop_two.shop:
                                self.map.blocks[j] = shop_one
                    player.worth += 1000
                    await self.monop_channel.send(f'{player.nick} нашёл зелёный светящийся камень. Странная аномалия меняет магазины {shop_one.shop} и {shop_two.shop} местами. Плохая новость заключается в том, что игроки больше не могут строить там филиалы')
        del_list = []
        for s in self.credits:
            if s == self.ongame['cur_player'].id:
                self.credits[s]['expires'] -= 1
                if self.credits[s]['expires'] == 0:
                    for p in self.players:
                        if p.id == s:
                            p.money -= self.credits[s]['pay']
                            del_list.append(p.id)
                            p.credit = defaultdict(int)
                            self.update_player(p)
        for d in del_list:
            del self.credits[d]
        for p in self.pledges:
            if p == self.ongame['cur_player'].id:
                for s in self.pledges[p]:
                    self.pledges[p][s] -= 1
                    if self.pledges[p][s] == 0:
                        self.sellshop(p, s)
        del_list = []
        for t in range(len(self.timers)):
            if self.timers[t]['name'] == 'jail':
                self.timers[t]['expires'] -= 1
                if self.timers[t]['expires'] == 0:
                    del_list.append(self.timers[t])
                    self.timers[t]['player'].jailed = False
                    self.update_player(self.timers[t]['player'])
            if self.timers[t]['name'] == 'cube':
                if self.timers[t]['player'] == self.ongame['cur_player']:
                    self.timers[t]['expires'] -= 1
                    if self.timers[t]['expires'] == 0:
                        del_list.append(self.timers[t])
                        self.timers[t]['player'].cubes = 2
                        self.update_player(self.timers[t]['player'])
            if self.timers[t]['name'] == 'death':
                if self.timers[t]['player'] == self.ongame['cur_player']:
                    self.timers[t]['expires'] -= 1
                    if self.timers[t]['expires'] == 0:
                        del_list.append(self.timers[t])
                        self.w8react.append(('death', '', self.timers[t]['player']))
        for d in del_list:
            del self.timers[self.timers.index(d)]
        for p in self.players:
            deathFlag = False
            for t in range(len(self.timers)):
                if self.timers[t]['name'] == 'death' and self.timers[t]['player'] == p:
                    deathFlag = True
            if p.money < 0 and not deathFlag:
                days = random.randint(1, 2)
                daysword = {1: 'день', 2: 'дня'}
                await self.monop_channel.send(f'{p.nick}, закончились деньги! За вами придёт греческая мафия, если не отдадите долги через {days} {daysword[days]}')
                self.timers.append({'name': 'death', 'expires': days, 'player': p})
        self.ongame['status'] = 'cubes'
        self.map.unject_cubes()
        self.ongame['cp_id'] += 1
        if self.ongame['cp_id'] >= len(self.players):
            self.ongame['cp_id'] -= len(self.players)
            self.ongame['round'] += 1
        br = 1
        while not self.players[self.ongame['cp_id']].ikiru:
            self.ongame['cp_id'] += 1
            br += 1
            if br >= len(self.players):
                emb = discord.Embed(title='Игра закончена!', color=random.choice(adb.raincolors))
                for p in self.players:
                    if not p.ikiru:
                        text = f'Мёртв))'
                    else:
                        text = f'${p.money}\n∑{p.get_netmort()}'
                    if p.slaps:
                        text += f' {slap}{p.slaps}'
                    if p.worth:
                        text += f'\nОчки: {p.worth}'
                    emb.add_field(name=f'{p.nick}', value=text, inline=False)  # список магазов, баланс, корды и звёзды
                await self.monop_channel.send(embed=emb)
                self.on = False
                break  # завершение игры
        if not polFlag:
            if self.ongame['crm_player']:
                if player == self.ongame['crm_player'] and self.ongame['criminal'] == 'polarize':
                    if player.money < pol:
                        player.money += (pol - player.money) * 2
                        player.worth += (pol - player.money)
                        await self.monop_channel.send(f'{player.nick} вернул себе ${(pol - player.money) * 2}')
                    self.ongame['criminal'] = ''
                    self.ongame['crm_player'] = None
        self.curblock = self.map.blockinfo(player, self.players)
        self.map.show_colors(next_player)
        player.update_shop(self.map.blocks[player.si])
        self.update_player(player)
        self.ongame['cur_player'] = self.players[self.ongame['cp_id']]
        await self.showmap()
        await self.monop_channel.send(random.choice(moves).format(self.ongame['cur_player'].nick))
        if self.ongame['cur_player'].AI:
            await self.ai_processing(self.ongame['cur_player'], 'cubes', mes.content)

    @commands.Cog.listener()
    async def on_ready(self):
        if self.monop_channelid:
            self.monop_channel = self.bot.get_channel(self.monop_channelid)

    @commands.Cog.listener()
    async def on_reaction_add(self, react, user):
        if not self.on or react.message.channel.id != self.monop_channelid or user.bot:
            return
        for idx, r in enumerate(self.w8react):
            if react.message.id == r[1].id:
                if r[2].id != user.id:
                    return
                del self.w8react[idx]
                if not self.ongame:
                    await r[0].delete()
                    await r[1].delete()
                    color_idx = random.randrange(0, len(self.player_colors))
                    color = self.player_colors[color_idx]
                    del self.player_colors[color_idx]
                    self.players.append(Player(user, str(react.emoji), color, self.map.type))
                    if str(react.emoji) in self.emos:
                        del self.emos[self.emos.index(str(react.emoji))]
                    await react.message.channel.send(f'{user.mention} {str(react.emoji)}, ваш цвет — {color}')
                    return
                elif r[0] == 'death' or r[0] == 'suicide':
                    await self.monop_channel.send(f'{r[2].nick}, вы выбрали смерть (или она вас)! Спасибо, что пользуетесь нашими услугами. Следующий рейс Харона скоро вас подбёрёт')
                    return
                elif r[0] == 'up' or r[0] == 'sell':
                    sellFlag = False
                    upFlag = False
                    for shop in range(len(self.map.blocks)):
                        s = self.map.blocks[shop]
                        if s.cat == 'shop':
                            if str(react.emoji) in s.icons:
                                for p in self.players:
                                    if p.id == r[2].id:
                                        if r[0] == 'up':
                                            pol = p.money
                                            if s.buyback:
                                                if p.money < int(s.cost * 0.6):
                                                    await self.monop_channel.send(f'{self.finduser(user).nick}, недостаточно денег', delete_after=5)
                                                else:
                                                    p.money -= int(s.cost * 0.6)
                                                    s.buyback = False
                                                    s.icon = s.icons[s.level]
                                                    cur_monopoly = []
                                                    for i in self.map.blocks:
                                                        if i.cat == 'shop':
                                                            if i.monopoly == s.monopoly:
                                                                cur_monopoly.append(i)
                                                    create_monFlag = True
                                                    for i in cur_monopoly:
                                                        if i.owner != p:
                                                            create_monFlag = False
                                                    if create_monFlag:
                                                        for i in self.map.blocks:
                                                            if i in cur_monopoly:
                                                                i.in_monopoly = True
                                                                p.update_shop(i)
                                                        p.monopolies.append(s.monopoly)
                                                        p.worth += 1000
                                                    upFlag = True
                                                    self.monop_channel.send(f'{p.nick} выкупил {s.vinshop}')
                                            else:
                                                if not s.in_monopoly:
                                                    await self.monop_channel.send(f'{self.finduser(user).nick}, магазин не в монополии', delete_after=5)
                                                if p.money < s.up:
                                                    await self.monop_channel.send(f'{self.finduser(user).nick}, недостаточно денег', delete_after=5)
                                                if s.buyback:
                                                    await self.monop_channel.send(f'{self.finduser(user).nick}, вы не можете строить филиалы компании под залогом', delete_after=5)
                                                if not self.upgradeFlag:
                                                    await self.monop_channel.send(f'{self.finduser(user).nick}, нельзя улучшать больше одного магазина за раунд', delete_after=5)
                                                elif s.level < 5 and not s.anomale:
                                                    p.money -= s.up
                                                    s.level += 1
                                                    s.worth += s.up
                                                    s.icon = s.icons[s.level]
                                                    self.upgradeFlag = False
                                                    upFlag = True
                                                    p.worth += 250
                                                    await self.monop_channel.send(f'{p.nick} строит {s.level} филиал {s.rodshop}')
                                                else:
                                                    await self.monop_channel.send(f'{self.finduser(user).nick}, максимальный уровень', delete_after=5)
                                            if self.ongame['crm_player']:
                                                if p == self.ongame['crm_player'] and self.ongame['criminal'] == 'polarize':
                                                    if p.money < pol:
                                                        p.money += (pol - p.money) * 2
                                                        p.worth += (pol - p.money)
                                                        await self.monop_channel.send(f'{p.nick} вернул себе ${(pol - p.money) * 2}')
                                                    self.ongame['criminal'] = ''
                                                    self.ongame['crm_player'] = None
                                        elif r[0] == 'sell':
                                            if s.level > 0:
                                                p.money += int(s.up * 0.5)
                                                s.level -= 1
                                                s.worth -= s.up
                                                s.icon = s.icons[s.level]
                                                sellFlag = True
                                                await self.monop_channel.send(f'{p.nick} продаёт {s.level+1} филиал {s.vinshop}')
                                            else:
                                                if s.buyback:
                                                    await self.monop_channel.send(f'{self.finduser(user).nick}, уже под залогом', delete_after=5)
                                                else:
                                                    p.money += int(s.cost * 0.5)
                                                    s.buyback = True
                                                    for i in self.map.blocks:
                                                        if i.cat == 'shop':
                                                            if i.monopoly == s.monopoly:
                                                                i.in_monopoly = False
                                                                p.update_shop(i)
                                                    if s.monopoly in p.monopolies:
                                                        del p.monopolies[p.monopolies.index(s.monopoly)]
                                                    sellFlag = True
                                                    self.pledges[p.id][s.shop] = 25
                                                    await self.monop_channel.send(f'{p.nick} закладывает {s.vinshop}')
                                        self.map.blocks[shop] = s
                                        p.update_shop(s)
                                        self.update_player(p)
                    if upFlag:
                        for ind, w in enumerate(self.w8react):
                            if str(w[0]) == 'up':
                                del self.w8react[ind]
                        await self.infomes.delete()
                        self.infomes = None
                        toup, emb = self.ongame['cur_player'].to_upgrade()
                        if toup:
                            self.infomes = await self.monop_channel.send(embed=emb)
                            for e in toup:
                                await self.infomes.add_reaction(e)
                            self.w8react.append(('up', self.infomes, user))
                    if sellFlag:
                        for ind, w in enumerate(self.w8react):
                            if str(w[0]) == 'sell':
                                del self.w8react[ind]
                        await self.sellmes.delete()
                        self.sellmes = None
                        tosell, emb = self.ongame['cur_player'].to_sell()
                        if tosell:
                            self.sellmes = await self.monop_channel.send(embed=emb)
                            for e in tosell:
                                await self.sellmes.add_reaction(e)
                            self.w8react.append(('sell', self.sellmes, user))
                    return
                await r[1].delete()
                if str(react.emoji) != '☑️':
                    await self.monop_channel.send(f'Предложение {r[3][0].nick} отклонено.', delete_after=10)
                    return
                if r[0] == 'trade_ms' or r[0] == 'trade_sm':
                    if r[0] == 'trade_ms':
                        s = r[3][1]
                        p = r[3][0]
                        pp = r[2]
                        p.money += r[3][2]
                    else:
                        s = r[3][2]
                        p = r[2]
                        pp = r[3][0]
                        p.money += r[3][1]
                    if s.in_monopoly:
                        for ss in self.map.blocks:
                            if ss.cat == 'shop':
                                if ss.monopoly == s.monopoly:
                                    ss.in_monopoly = False
                                    p.update_shop(ss)
                        del p.monopolies[p.monopolies.index(s.monopoly)]
                    s.owner = pp
                    s.income = 0
                    del p.shops[p.shops.index(s)]
                    pp.shops.append(s)
                    cur_monopoly = []
                    for ss in self.map.blocks:
                        if ss.cat == 'shop':
                            if s.monopoly == ss.monopoly:
                                cur_monopoly.append(ss)
                        create_monFlag = True
                    for ss in cur_monopoly:
                        if ss.owner != pp:
                            create_monFlag = False
                    if create_monFlag:
                        for ss in self.map.blocks:
                            if ss in cur_monopoly:
                                ss.in_monopoly = True
                                pp.update_shop(ss)
                        pp.monopolies.append(s.monopoly)
                        pp.worth += 1000
                    pp.update_shop(s)
                    for j in range(len(self.map.blocks)):
                        ss = self.map.blocks[j]
                        if ss.cat == 'shop':
                            if ss.shop == s.shop:
                                self.map.blocks[j] = s
                    self.update_player(p)
                    self.update_player(pp)
                    if r[0] == 'trade_ms':
                        self.monop_channel.send(f'Обмен завершён! {p.nick} получает ${r[3][2]}, {pp.nick} получает {s.vinshop}')
                    else:
                        for block in self.map.blocks:
                            if block.cat == 'shop':
                                if block.shop == r[3][2]:
                                    r[3][2] = block.vinshop
                        self.monop_channel.send(f'Обмен завершён! {pp.nick} получает {s.vinshop}, {p.nick} получает ${r[3][2]}')
                if r[0] == 'trade_ss':
                    s = r[3][1]
                    p = r[3][0]
                    pp = r[2]
                    ts = r[3][2]

                    if s.in_monopoly:
                        del p.monopolies[p.monopolies.index(s.monopoly)]
                    if ts.in_monopoly:
                        del pp.monopolies[pp.monopolies.index(ts.monopoly)]
                    s_monopoly = []
                    ts_monopoly = []
                    for ss in self.map.blocks:
                        if ss.cat == 'shop':
                            if ss.monopoly == s.monopoly:
                                ss.in_monopoly = False
                                p.update_shop(ss)
                                s_monopoly.append(ss)
                            if ss.monopoly == ts.monopoly:
                                ss.in_monopoly = False
                                pp.update_shop(ss)
                                ts_monopoly.append(ss)
                    s.owner = pp
                    ts.owner = p
                    s.income = 0
                    ts.income = 0
                    del p.shops[p.shops.index(s)]
                    del pp.shops[pp.shops.index(ts)]
                    pp.shops.append(s)
                    p.shops.append(ts)
                    create_smonFlag = True
                    for ss in s_monopoly:
                        if ss.owner != pp:
                            create_smonFlag = False
                    create_tsmonFlag = True
                    for ss in ts_monopoly:
                        if ss.owner != p:
                            create_tsmonFlag = False
                    if create_smonFlag:
                        for ss in self.map.blocks:
                            if ss in s_monopoly:
                                ss.in_monopoly = True
                                pp.update_shop(ss)
                        pp.monopolies.append(s.monopoly)
                        pp.worth += 1000
                    if create_tsmonFlag:
                        for ss in self.map.blocks:
                            if ss in ts_monopoly:
                                ss.in_monopoly = True
                                p.update_shop(ss)
                        p.monopolies.append(ts.monopoly)
                        p.worth += 1000
                    pp.update_shop(s)
                    p.update_shop(ts)
                    for j in range(len(self.map.blocks)):
                        ss = self.map.blocks[j]
                        if ss.cat == 'shop':
                            if ss.shop == s.shop:
                                self.map.blocks[j] = s
                            if ss.shop == ts.shop:
                                self.map.blocks[j] = ts
                    self.update_player(p)
                    self.update_player(pp)
                    await self.monop_channel.send(f'Обмен завершён! {p.nick} получает {ts.vinshop}, {pp.nick} получает {s.vinshop}')

    def sellshop(self, player, shop):
        for p in self.players:
            if p.id == player:
                for i in range(len(self.map.blocks)):
                    s = self.map.blocks[i]
                    if s.cat == 'shop':
                        if s.shop == shop:
                            s.owner = None
                            s.icon = s.icons[0]
                            s.income = 0
                            s.buyback = False
                            self.map.blocks[i] = s
                            p.update_shop(s)
                            self.update_player(p)
                            del self.pledges[player][shop]
                            return

    async def sellsend(self):
        tosell, emb = self.ongame['cur_player'].to_sell()
        if tosell:
            if self.sellmes:
                await self.sellmes.delete()
                self.sellmes = None
            self.sellmes = await self.monop_channel.send(embed=emb)
            for e in tosell:
                await self.sellmes.add_reaction(e)
            self.w8react.append(('sell', self.sellmes, self.ongame['cur_player']))
        await self.monop_channel.send(f'{self.ongame["cur_player"].nick}, закончились деньги! Закладывайте филиалы, берите кредит, следайте что-нибудь!')

    async def mhelp(self):
        emb = discord.Embed(title='Добро пожаловать в Монополию!', description='Монополия — это экономическая игра в жанре рандом-стратегии. Для победы нужно покупать фирмы, строить их филиалы, собирать дань с игроков и, желательно, пореже заряжать шестёрку в револьвер')
        emb.add_field(name='Понятия, которых нет в класической монополии', value='Мы добавили новые механики', inline=False)
        emb.add_field(name='Кредиты', value='Тут всё просто — берёте деньги, потом отдаёте чуть побольше', inline=True)
        emb.add_field(name='Очки', value='Помимо последнего выжившего, победителем считается игрок с наибольшим количеством очков. Будьте активны!', inline=True)
        emb.add_field(name='Акции', value='Возможность продать часть своей компании другому игроку. Он будет получать часть вашей прибыли, а вы — много очков', inline=True)
        emb.add_field(name='Криминальный авторитет', value='Новое особое поле, наступая на которое, вы получаете возможность немного улучшить себе жизнь, испортив её другим игрокам...', inline=True)
        emb.add_field(name='Сумма активов', value='Технически, это все ваши деньги, вложенные в магазины, плюс наличка', inline=True)
        emb.add_field(name='Всё из обычной монополии', value='old but gold', inline=False)
        emb.add_field(name='Бонусы', value='Эти блоки дают вам деньги и другие полезные плюшки', inline=True)
        emb.add_field(name='Анти-бонусы', value='Наступив на эти блоки, вы теряете деньги, или того хуже...', inline=True)
        emb.add_field(name='Полицейский участок/Тюрьма', value='Здесь можно дать пощёчину заключённому', inline=True)
        emb.add_field(name='Револьвер', value='Здесь можно застрелиться, если дела идут плохо. Ну или просто так...', inline=True)
        emb.add_field(name='Полицейский участок', value='Здесь можно дать пощёчину заключённому', inline=True)
        emb.add_field(name='Облава', value='Нежелательный район, где всегда есть парочка злых полицейских...', inline=True)
        emb.add_field(name='Управление', value='Больше удобных фишечек богу удобных фишечек!', inline=False)
        emb.add_field(name='Чат', value='Все сообщения в чат пишутся через `-`', inline=True)
        emb.add_field(name='Бросок кубика', value='Кубики используют для рандома зерно, полученное из текста вашего сообщения!', inline=True)
        emb.add_field(name='Плата за аренду', value='Если вы попали на чужое поле, пишите `pay <сумма>`. На самом деле, можно написать любую фигню', inline=True)
        emb.add_field(name='Покупка', value='Для покупки поля напишите `buy <сумма>`. Можно просто `buy`', inline=True)
        emb.add_field(name='Продажа акций', value='Для продажи акций напишите `stocks __%`. Игрок, владеющий 51% акций, становится владельцем фирмы!', inline=True)
        emb.add_field(name='Покупка акций', value='Для покупки акций напишите `buystock <название>` Доступные акции видны в окне биржи', inline=True)
        emb.add_field(name='Торговля', value='Для торговли необходимо написать: `trade <с кем> <что предлагаете> <что хотите взамен>`. Торговать можно деньгами и фирмами', inline=True)
        emb.add_field(name='Покупка/продажа филиалов', value='Выберите фирму для апгрейда и поставьте реакцию в специальном окне. Окно продажи: `sell`, окно покупки автоматическое', inline=True)
        emb.add_field(name='Кредит', value='После 10 раунда можно взять деньги в кредит: $5000 на 20 раундов или $10000 на 10 раундов. `credit <сумма>`', inline=True)
        emb.add_field(name='Выбор игрока', value='Для некоторых действий необходимо написать имя игрока. Подойдёт что угодно: его ник, id или mention в дискорде, даже квадратик с цветом', inline=True)
        emb.add_field(name='И да, под суммой $5000 подразумевается $5000k, то есть 5 миллионов', value='Приятной игры!',inline=False)
        await self.monop_channel.send(embed=emb)

    @commands.Cog.listener()
    async def on_message(self, mes):
        if not self.on or mes.channel.id != self.monop_channelid:
            return
        if bool(mes.author.id == self.bot.user.id) ^ bool('↯AI' in mes.content):
            return
        if mes.content.startswith('-'):
            return
        if self.ongame:
            if mes.content.lower().startswith('buystock'):
                await mes.delete()
                shop = mes.content.split('buystock')[1].split('↯AI')[0].replace(' ', '').lower()
                for i in self.stocks:
                    if i['shop'].replace(' ', '').lower() == shop:
                        for p in self.players:
                            if p.id == i['player']:
                                for j in range(len(self.map.blocks)):
                                    s = self.map.blocks[j]
                                    if s.cat == 'shop':
                                        if s.shop == i['shop']:
                                            for pp in self.players:
                                                if mes.author.id == self.bot.user.id:
                                                    ppid = int(mes.content.split('↯AI')[1])
                                                else:
                                                    ppid = mes.author.id
                                                if pp.id == ppid:
                                                    if pp.money >= i['cost']:
                                                        cur_perc = 100 - sum([s.stocks[a] for a in s.stocks])
                                                        pp.stocks[i['shop']] += i['perc']
                                                        s.stocks[pp.id] += i['perc']
                                                        pp.money -= i['cost']
                                                        if self.ongame['crm_player']:
                                                            if pp == self.ongame['crm_player'] and self.ongame['criminal'] == 'polarize':
                                                                pp.money += i['cost'] * 2
                                                                pp.worth += i['cost']
                                                                await self.monop_channel.send(f'{pp.nick} вернул себе ${i["cost"]}')
                                                                self.ongame['criminal'] = ''
                                                                self.ongame['crm_player'] = None
                                                        p.money += i['cost']
                                                        if s.stocks[pp.id] > 50:
                                                            if s.in_monopoly:
                                                                for ss in self.map.blocks:
                                                                    if ss.cat == 'shop':
                                                                        if ss.monopoly == s.monopoly:
                                                                            ss.in_monopoly = False
                                                                            p.update_shop(ss)
                                                                del p.monopolies[p.monopolies.index(s.monopoly)]
                                                            s.owner = pp
                                                            s.income = 0
                                                            s.stocks[i['player']] = cur_perc - i['perc']
                                                            p.stocks[i['shop']] = cur_perc - i['perc']
                                                            del pp.stocks[i['shop']]
                                                            del s.stocks[pp.id]
                                                            del p.shops[p.shops.index(s)]
                                                            pp.shops.append(s)
                                                            cur_monopoly = []
                                                            for ss in self.map.blocks:
                                                                if ss.cat == 'shop':
                                                                    if s.monopoly == ss.monopoly:
                                                                        cur_monopoly.append(ss)
                                                            create_monFlag = True
                                                            for ss in cur_monopoly:
                                                                if ss.owner != pp:
                                                                    create_monFlag = False
                                                            if create_monFlag:
                                                                for ss in self.map.blocks:
                                                                    if ss in cur_monopoly:
                                                                        ss.in_monopoly = True
                                                                        pp.update_shop(ss)
                                                                pp.monopolies.append(s.monopoly)
                                                                pp.worth += 1000
                                                            pp.update_shop(s)
                                                        else:
                                                            p.update_shop(s)
                                                        self.map.blocks[j] = s
                                                        p.worth += 500
                                                        pp.worth += 500
                                                        self.update_player(p)
                                                        self.update_player(pp)
                                                        del self.stocks[self.stocks.index(i)]
                                                        await self.monop_channel.send(f'{pp.nick} покупает акцию {s.rodshop} у {p.nick} ({i["perc"]}%)')
                                                        break
                                            break
                                break
                        break
                if self.stockmes:
                    await self.stockmes.delete()
                    self.stockmes = None
                if self.stocks:
                    emb = discord.Embed(title='Игроки выставили акции своих компаний на продажу')
                    for i in self.stocks:
                        for j in range(len(self.map.blocks)):
                            s = self.map.blocks[j]
                            if s.cat == 'shop':
                                if s.shop == i['shop']:
                                    emb.add_field(name=f'{s.shop}', value=f'{s.owner.nick} выставил {i["perc"]}% за {i["cost"]}\nКупить: `buystock {s.shop}`', inline=True)
                                    break
                    self.stockmes = await self.monop_channel.send(embed=emb)
                return
            if mes.author.id == self.ongame['cur_player'].id or (mes.author.id == self.bot.user.id and self.ongame['cur_player'].AI):
                await mes.delete()
                player = self.ongame['cur_player']
                if mes.content.lower().startswith('trade'):
                    trade = mes.content.lower().split('trade ')[1].split(' ')
                    if len(trade) < 3:
                        await self.monop_channel.send(f'trade <кому> <сумма/компания> <сумма/компания взамен>', delete_after=20)
                        return
                    trade_to = self.finduser(trade[0])
                    trade_what = ''
                    trade_forwhat = ''
                    twsi = -2
                    tfwsi = -2
                    if re.findall(r'\D', trade[1]):
                        for j in range(len(self.map.blocks)):
                            s = self.map.blocks[j]
                            if s.cat == 'shop':
                                if s.onwer.id == player.id:
                                    if trade[1] in s.shop.lower():
                                        trade_what = s
                                        twsi = j
                                        trade_forwhat = mes.content.split(s.shop.lower())[1].lstrip()
                        if trade_what.in_monopoly:
                            for j in range(len(self.map.blocks)):
                                s = self.map.blocks[j]
                                if s.cat == 'shop':
                                    if s.onwer.id == player.id:
                                        if trade_what.monopoly == s.monopoly:
                                            if s.level > 0:
                                                await self.monop_channel.send(f'{player.nick}, обмениваться можно только в случае, если у монополии нет филиалов', delete_after=10)
                                                return
                    else:
                        trade_what = int(trade[1])
                        twsi = -1
                        trade_forwhat = mes.content.split(trade[1])[1].lstrip()
                    if re.findall(r'\D', trade_forwhat):
                        for j in range(len(self.map.blocks)):
                            s = self.map.blocks[j]
                            if s.cat == 'shop':
                                if s.onwer.id == trade_to.id:
                                    if trade_forwhat in s.shop.lower():
                                        trade_forwhat = s
                                        tfwsi = j
                        if trade_forwhat.in_monopoly:
                            for j in range(len(self.map.blocks)):
                                s = self.map.blocks[j]
                                if s.cat == 'shop':
                                    if s.onwer.id == player.id:
                                        if trade_forwhat.monopoly == s.monopoly:
                                            if s.level > 0:
                                                await self.monop_channel.send(f'{player.nick}, обмениваться можно только в случае, если у монополии нет филиалов', delete_after=10)
                                                return
                    else:
                        trade_forwhat = int(trade_forwhat)
                        tfwsi = -1
                    if not trade_forwhat or not trade_what or twsi == -2 or tfwsi == -2:
                        self.monop_channel.send(f'trade <кому> <сумма/компания> <сумма/компания взамен>', delete_after=20)
                        return
                    if twsi < 0 and tfwsi < 0:
                        self.monop_channel.send(f'{player.nick}, нельзя обмениваться только деньгами', delete_after=10)
                        return
                    emb = discord.Embed(title='Предложение обмена')
                    if twsi < 0:
                        emb.add_field(name='Обменять', value=f'**{player.nick}**\n${trade_what}', inline=True)
                    else:
                        emb.add_field(name='Обменять', value=f'**{player.nick}**\n{trade_what.shop} {trade_what.raw_icon}{trade_what.level*"★"}', inline=True)
                    if tfwsi < 0:
                        emb.add_field(name='На', value=f'**{trade_to.nick}**\n${trade_forwhat}', inline=True)
                    else:
                        emb.add_field(name='На', value=f'**{trade_to.nick}**\n{trade_forwhat.shop} {trade_forwhat.raw_icon}{trade_forwhat.level*"★"}', inline=True)
                    self.trademes = await mes.channel.send(embed=emb)
                    await self.trademes.add_reaction('☑️')
                    await self.trademes.add_reaction('💢')
                    if twsi < 0:
                        self.w8react.append(('trade_ms', self.trademes, trade_to, [player, trade_what, trade_forwhat]))
                    elif tfwsi < 0:
                        self.w8react.append(('trade_sm', self.trademes, trade_to, [player, trade_what, trade_forwhat]))
                    else:
                        self.w8react.append(('trade_ss', self.trademes, trade_to, [player, trade_what, trade_forwhat]))
                    return
                if mes.content.lower().startswith('sell'):
                    tosell, emb = self.ongame['cur_player'].to_sell(False)
                    if tosell:
                        self.sellmes = await mes.channel.send(embed=emb)
                        for e in tosell:
                            await self.sellmes.add_reaction(e)
                        self.w8react.append(('sell', self.sellmes, mes.author))
                    return
                if mes.content.lower().startswith('credit'):
                    if self.ongame['round'] < 10:
                        await self.monop_channel.send(f'{player.nick}, нельзя брать кредиты до 10 раунда', delete_after=10)
                        return
                    if self.credits[player.id]:
                        await self.monop_channel.send(f'{player.nick}, у вас уже есть кредит', delete_after=10)
                        return
                    credit = int(mes.content.split('credit')[1].split('↯AI')[0])
                    if credit not in [5000, 10000]:
                        await self.monop_channel.send(f'{player.nick}, введите сумму:\n5000 на 20 раундов, 10000 на 10 раундов', delete_after=20)
                        return
                    credit_dict = {5000: 20, 10000: 10}
                    pay_dict = {5000: 7000, 10000: 11000}
                    for p in self.players:
                        if p.id == player.id:
                            p.money += credit
                            p.worth += 500
                            self.credits[p.id] = {'money': credit, 'expires': credit_dict[credit], 'pay': pay_dict[credit]}
                            p.credit = self.credits[p.id]
                            self.update_player(p)
                            await self.monop_channel.send(f'{p.nick} взял в кредит ${credit} на {adb.postfix(self.credits[p.id]["expires"], ["ход", "хода", "ходов"])}')
                    return
                if self.ongame['status'] == 'cubes':
                    self.ongame['status'] = 'action'
                    pol = self.ongame['cur_player'].money
                    if self.stockmes:
                        await self.stockmes.delete()
                        self.stockmes = None
                    if self.stocks:
                        emb = discord.Embed(title='Игроки выставили акции своих компаний на продажу')
                        for i in self.stocks:
                            for j in range(len(self.map.blocks)):
                                s = self.map.blocks[j]
                                if s.cat == 'shop':
                                    if s.shop == i['shop']:
                                        emb.add_field(name=f'{s.shop}', value=f'{s.owner.nick} выставил {i["perc"]}% за {i["cost"]}\nКупить: `buystock {s.shop}`', inline=True)
                                        break
                        self.stockmes = await self.monop_channel.send(embed=emb)
                        for p in self.players:
                            if p.AI:
                                if adb.chance(25):
                                    ac = random.choice(self.stocks)
                                    await self.ai_processing(p, 'buystock', ac)
                                    break
                    retFlag = False
                    if self.ongame['cur_player'].jailed:
                        random.seed(mes.content)
                        vs = [random.randint(1, 6) for _ in range(self.ongame['cur_player'].cubes)]
                        cubes = [Cube(vs[i]) for i in range(self.ongame['cur_player'].cubes)]
                        player = self.ongame["cur_player"]
                        if mes.content.lower().startswith('aaa') or mes.content.lower().startswith('ааа') or self.ongame['cur_player'].AI:
                            if vs[0] == vs[1]:
                                player.jailed = False
                                self.update_player(player)
                                self.map.inject_cubes(cubes, sum(vs))
                                self.map.move_player(player, sum(vs))
                                self.curblock = self.map.blockinfo(player, self.players)
                                self.map.show_shops(self.players, player)
                                self.update_player(player)
                                await self.monop_channel.send(f'{self.ongame["cur_player"].nick} выбросил дубль и теперь глотает свежий воздух')
                            else:
                                await self.monop_channel.send(f'{self.ongame["cur_player"].nick}, вы остаётесь в тюрьме, жрите мыло!')
                                retFlag = True
                        else:
                            await self.monop_channel.send(f'{self.ongame["cur_player"].nick}, вы в тюрьме, считайте мыло!')
                            retFlag = True
                    else:
                        await self.cubes(mes, self.ongame['cur_player'])
                    if retFlag:
                        if self.infomes:
                            await self.infomes.delete()
                            self.infomes = None
                        if self.sellmes:
                            await self.sellmes.delete()
                            self.sellmes = None
                        del_list = []
                        for s in self.credits:
                            if s == self.ongame['cur_player'].id:
                                self.credits[s]['expires'] -= 1
                                if self.credits[s]['expires'] == 0:
                                    for p in self.players:
                                        if p.id == s:
                                            p.money -= self.credits[s]['pay']
                                            del_list.append(p.id)
                                            p.credit = defaultdict(int)
                                            self.update_player(p)
                        for d in del_list:
                            del self.credits[d]
                        for p in self.pledges:
                            if p == self.ongame['cur_player'].id:
                                for s in self.pledges[p]:
                                    self.pledges[p][s] -= 1
                                    if self.pledges[p][s] == 0:
                                        self.sellshop(p, s)
                        del_list = []
                        for t in range(len(self.timers)):
                            if self.timers[t]['name'] == 'jail':
                                self.timers[t]['expires'] -= 1
                                if self.timers[t]['expires'] == 0:
                                    del_list.append(self.timers[t])
                                    self.timers[t]['player'].jailed = False
                                    self.update_player(self.timers[t]['player'])
                            if self.timers[t]['name'] == 'cube':
                                if self.timers[t]['player'] == self.ongame['cur_player']:
                                    self.timers[t]['expires'] -= 1
                                    if self.timers[t]['expires'] == 0:
                                        del_list.append(self.timers[t])
                                        self.timers[t]['player'].cubes = 2
                                        self.update_player(self.timers[t]['player'])
                            if self.timers[t]['name'] == 'death':
                                if self.timers[t]['player'] == self.ongame['cur_player']:
                                    self.timers[t]['expires'] -= 1
                                    if self.timers[t]['expires'] == 0:
                                        del_list.append(self.timers[t])
                                        self.w8react.append(('death', '', self.timers[t]['player']))
                        for d in del_list:
                            del self.timers[self.timers.index(d)]
                        for p in self.players:
                            deathFlag = False
                            for t in range(len(self.timers)):
                                if self.timers[t]['name'] == 'death' and self.timers[t]['player'] == p:
                                    deathFlag = True
                            if p.money < 0 and not deathFlag:
                                days = random.randint(1, 2)
                                daysword = {1: 'день', 2: 'дня'}
                                await self.monop_channel.send(f'{p.nick}, закончились деньги! За вами придёт греческая мафия, если не отдадите долги через {days} {daysword[days]}')
                                self.timers.append({'name': 'death', 'expires': days, 'player': p})
                        self.ongame['status'] = 'cubes'
                        self.ongame['cp_id'] += 1
                        if self.ongame['cp_id'] >= len(self.players):
                            self.ongame['cp_id'] -= len(self.players)
                            self.ongame['round'] += 1
                        br = 1
                        while not self.players[self.ongame['cp_id']].ikiru:
                            self.ongame['cp_id'] += 1
                            br += 1
                            if br >= len(self.players):
                                emb = discord.Embed(title='Игра закончена!', color=random.choice(adb.raincolors))
                                for p in self.players:
                                    if not p.ikiru:
                                        text = f'Мёртв))'
                                    else:
                                        text = f'${p.money}\n∑{p.get_netmort()}'
                                    if p.slaps:
                                        text += f' {slap}{p.slaps}'
                                    if p.worth:
                                        text += f'\nОчки: {p.worth}'
                                    emb.add_field(name=f'{p.nick}', value=text, inline=False)  # список магазов, баланс, корды и звёзды
                                await self.monop_channel.send(embed=emb)
                                self.on = False
                                break  # завершение игры
                        player = self.ongame['cur_player']
                        if self.ongame['crm_player']:
                            if player == self.ongame['crm_player'] and self.ongame['criminal'] == 'polarize':
                                if player.money < pol:
                                    player.money += (pol - player.money) * 2
                                    player.worth += (pol - player.money)
                                    await self.monop_channel.send(f'{player.nick} вернул себе ${(pol - player.money) * 2}')
                            self.ongame['criminal'] = ''
                            self.ongame['crm_player'] = None
                            self.update_player(player)
                        self.ongame['cur_player'].update_shop(self.map.blocks[self.ongame['cur_player'].si])
                        self.curblock = self.map.blockinfo(self.ongame["cur_player"], self.players)
                        self.ongame['cur_player'] = self.players[self.ongame['cp_id']]
                        await self.monop_channel.send(random.choice(moves).format(self.ongame['cur_player'].nick))
                        await self.showmap()
                        if self.ongame['cur_player'].AI:
                            await self.ai_processing(self.ongame['cur_player'], 'cubes', mes.content)
                        return
                    self.upgradeFlag = True
                    if self.ongame['cur_player'].AI:
                        await self.ai_processing(self.ongame['cur_player'], 'up', '')
                    else:
                        toup, emb = self.ongame['cur_player'].to_upgrade()
                        if toup:
                            if self.infomes:
                                await self.infomes.delete()
                                self.infomes = None
                            self.infomes = await self.monop_channel.send(embed=emb)
                            for e in toup:
                                await self.infomes.add_reaction(e)
                            self.w8react.append(('up', self.infomes, mes.author))
                    block = self.map.blocks[self.ongame['cur_player'].si]
                    if block.cat == 'shop':
                        if block.owner:
                            if self.ongame['cur_player'].id != block.owner.id:
                                if not block.buyback:
                                    if self.ongame['cur_player'].AI:
                                        await self.ai_processing(self.ongame['cur_player'], 'pay', block.get_mort())
                                    elif self.ongame['cur_player'].money < block.get_mort():
                                        await self.sellsend()
                                else:
                                    await self.ai_processing(self.ongame['cur_player'], 'idle', block.get_mort())
                            elif self.ongame['cur_player'].AI:
                                await self.ai_processing(self.ongame['cur_player'], 'stocks', '')
                        elif self.ongame['cur_player'].AI:
                            await self.ai_processing(self.ongame['cur_player'], 'buy', block.cost)
                        await self.showmap()
                    else:
                        await self.passion(mes)
                elif self.ongame['status'] == 'action':
                    pol = self.ongame['cur_player'].money
                    if self.infomes:
                        await self.infomes.delete()
                        self.infomes = None
                    if self.sellmes:
                        await self.sellmes.delete()
                        self.sellmes = None
                    if self.stockmes:
                        await self.stockmes.delete()
                        self.stockmes = None
                    del_list = []
                    for s in self.credits:
                        if s == self.ongame['cur_player'].id:
                            self.credits[s]['expires'] -= 1
                            if self.credits[s]['expires'] == 0:
                                for p in self.players:
                                    if p.id == s:
                                        p.money -= self.credits[s]['pay']
                                        del_list.append(p.id)
                                        p.credit = defaultdict(int)
                                        self.update_player(p)
                    for d in del_list:
                        del self.credits[d]
                    for p in self.pledges:
                        if p == self.ongame['cur_player'].id:
                            for s in self.pledges[p]:
                                self.pledges[p][s] -= 1
                                if self.pledges[p][s] == 0:
                                    self.sellshop(p, s)
                    del_list = []
                    for t in range(len(self.timers)):
                        if self.timers[t]['name'] == 'jail':
                            self.timers[t]['expires'] -= 1
                            if self.timers[t]['expires'] == 0:
                                del_list.append(self.timers[t])
                                self.timers[t]['player'].jailed = False
                                self.update_player(self.timers[t]['player'])
                        if self.timers[t]['name'] == 'cube':
                            if self.timers[t]['player'] == self.ongame['cur_player']:
                                self.timers[t]['expires'] -= 1
                                if self.timers[t]['expires'] == 0:
                                    del_list.append(self.timers[t])
                                    self.timers[t]['player'].cubes = 2
                                    self.update_player(self.timers[t]['player'])
                        if self.timers[t]['name'] == 'death':
                            if self.timers[t]['player'] == self.ongame['cur_player']:
                                self.timers[t]['expires'] -= 1
                                if self.timers[t]['expires'] == 0:
                                    del_list.append(self.timers[t])
                                    self.w8react.append(('death', '', self.timers[t]['player']))
                    for d in del_list:
                        del self.timers[self.timers.index(d)]
                    for p in self.players:
                        deathFlag = False
                        for t in range(len(self.timers)):
                            if self.timers[t]['name'] == 'death' and self.timers[t]['player'] == p:
                                deathFlag = True
                        if p.money < 0 and not deathFlag:
                            days = random.randint(1, 2)
                            daysword = {1: 'день', 2: 'дня'}
                            await self.monop_channel.send(f'{p.nick}, закончились деньги! За вами придёт греческая мафия, если не отдадите долги через {days} {daysword[days]}')
                            self.timers.append({'name': 'death', 'expires': days, 'player': p})
                    for i in self.w8react:
                        if i[0] == 'death' or i[0] == 'suicide':
                            if i[2].money < 0 or i[0] == 'suicide':
                                if adb.chance(10) and i[0] == 'death':
                                    await self.monop_channel.send(f'Смерть пытается спасти парнишу {i[2].nick} от гибели, забашляв ему $5000. Давайте посмотрим на это')
                                    await asyncio.sleep(5)
                                    i[2].money += 5000
                                    if i[2].money < 0:
                                        await self.monop_channel.send(f'Старина Смерть не смог спасти {i[2].nick}. Парень слишком много задолжал и теперь идёт в Тартар работать ~~минетчиком Церберу~~ на рудники Сизифа')
                                    else:
                                        i[2].worth += 5000
                                        await self.monop_channel.send(f'Смерть спас {i[2].nick}, одолжив ему денег. Не волнуйся, вернёшь в следующей жизни!')
                                        self.update_player(i[2])
                                        continue
                                for j in range(len(self.map.blocks)):
                                    s = self.map.blocks[j]
                                    if s.cat == 'shop':
                                        if i[2] == s.owner:
                                            s.level = 0
                                            s.owner = None
                                            s.worth = 0
                                            s.income = 0
                                            s.in_monopoly = False
                                            s.buyback = False
                                            s.stocks = defaultdict(int)
                                            self.map.blocks[j] = s
                                i[2].ikiru = False
                                self.update_player(i[2])
                                emb = discord.Embed(title=f"Минус один", description=f"{i[2].nick}, вы умерли! Удачи на том свете!\nФинальный счёт:{i[2].networth()}")
                                await self.monop_channel.send(embed=emb)
                    self.w8react = []
                    self.ongame['status'] = 'cubes'
                    self.map.unject_cubes()
                    self.ongame['cp_id'] += 1
                    if self.ongame['cp_id'] >= len(self.players):
                        self.ongame['cp_id'] -= len(self.players)
                        self.ongame['round'] += 1
                    br = 1
                    while not self.players[self.ongame['cp_id']].ikiru:
                        self.ongame['cp_id'] += 1
                        br += 1
                        if br >= len(self.players):
                            emb = discord.Embed(title='Игра закончена!', color=random.choice(adb.raincolors))
                            for p in self.players:
                                if not p.ikiru:
                                    text = f'Мёртв))'
                                else:
                                    text = f'${p.money}\n∑{p.get_netmort()}'
                                if p.slaps:
                                    text += f' {slap}{p.slaps}'
                                if p.worth:
                                    text += f'\nОчки: {p.worth}'
                                emb.add_field(name=f'{p.nick}', value=text,
                                              inline=False)  # список магазов, баланс, корды и звёзды
                            await self.monop_channel.send(embed=emb)
                            self.on = False
                            break  # завершение игры
                    player = self.ongame['cur_player']
                    if self.ongame['crm_player']:
                        if player == self.ongame['crm_player'] and self.ongame['criminal'] == 'polarize':
                            if player.money < pol:
                                player.money += (pol - player.money) * 2
                                player.worth += (pol - player.money)
                                await self.monop_channel.send(f'{player.nick} вернул себе ${(pol - player.money) * 2}')
                            self.ongame['criminal'] = ''
                            self.ongame['crm_player'] = None
                            self.update_player(player)
                    await self.action(mes, self.ongame['cur_player'], self.players[self.ongame['cp_id']])
                    self.ongame['cur_player'] = self.players[self.ongame['cp_id']]
                    await self.showmap()
                    await self.monop_channel.send(random.choice(moves).format(self.ongame['cur_player'].nick))
                    if self.ongame['cur_player'].AI:
                        await self.ai_processing(self.ongame['cur_player'], 'cubes', mes.content)
            return

        if mes.content == '+AI':
            await mes.delete()
            if len(self.players) > len(player_colors):
                await mes.channel.send(f"{mes.author.mention}, достигнуто максимальное количество игроков",
                                       delete_after=5)
                return
            color_idx = random.randrange(0, len(self.player_colors))
            color = self.player_colors[color_idx]
            del self.player_colors[color_idx]
            emo_idx = random.randrange(0, len(self.ai_emos))
            emo = self.ai_emos[emo_idx]
            del self.ai_emos[emo_idx]
            name_idx = random.randrange(0, len(self.ai_names))
            name = self.ai_names[name_idx]
            del self.ai_names[name_idx]
            self.players.append(Player(mes.author, emo, color, self.map.type, name))
            await mes.channel.send(f'{name} {emo}, ваш цвет — {color}')

        if mes.content == '+':
            await mes.delete()
            for p in self.players:
                if p.id == mes.author.id:
                    await mes.channel.send(f"{mes.author.mention}, вы уже играете", delete_after=5)
                    return
            if len(self.players) > len(player_colors):
                await mes.channel.send(f"{mes.author.mention}, достигнуто максимальное количество игроков", delete_after=5)
                return
            emos = self.emosdict[self.userlist[mes.author.id]['bbagid']]
            if not emos:
                emos = self.emos
            mes_one = await mes.channel.send(f"{mes.author.mention}\nCHOOSE YOUR HERO", delete_after=25)
            mes_two = await mes.channel.send(f"{' '.join(emos)}", delete_after=25)
            for e in emos:
                await mes_two.add_reaction(e)
            self.w8react.append((mes_one, mes_two, mes.author))

        if mes.content == '++':
            await mes.delete()
            if len(self.players) < 2:
                await mes.channel.send(f"Недостаточно игроков!", delete_after=5)
                return
            self.monop_channel = self.bot.get_channel(self.monop_channelid)
            self.map = Map(self.maptype)
            random.shuffle(self.players)
            self.ongame = {'cp_id': 0, 'cur_player': self.players[0], 'status': 'cubes', 'round': 1, 'criminal': '', 'crm_player': None}
            self.w8react = []
            await self.mhelp()
            self.map.show_colors(self.players[1])
            await self.showmap()
            await mes.channel.send(f"Игра начинается!")
            await mes.channel.send(f"Для броска кубика напишите в чат зерно. Для использования чата перед сообщением поставьте -. Первым ходит {self.ongame['cur_player'].men}!")
            if self.ongame['cur_player'].AI:
                await self.ai_processing(self.ongame['cur_player'], 'cubes', mes.content)

    @commands.command()
    async def monopoly_test(self, ctx, ais=0, t: int = 2):
        if self.ongame:
            await ctx.send(f"Игра уже началась!", delete_after=10)
            return
        if not self.monop_channelid == ctx.channel.id:
            if self.monop_channel:
                monop_channel = self.bot.get_channel(self.monop_channelid)
                await ctx.send(f"Вы не можете играть в этом канале. Играть в {monop_channel.mention}", delete_after=10)
            else:
                await ctx.send("У нас нет канала для монополии. Задать канал командой **monop_setchannel**", delete_after=10)
            return
        evrv = ctx.guild.default_role
        await self.monop_channel.set_permissions(evrv, view_channel=True)
        self.map = Map(t)
        self.on = True
        self.player_colors = [pc for pc in player_colors]
        self.ai_names = [a for a in ai_names]
        self.ai_emos = [e for e in ai_emos]
        noPlayer = False
        if ais < 0:
            ais = abs(ais)
            noPlayer = True
        colors = adb.sevranchoice(self.player_colors, ais+1)
        emos = adb.sevranchoice(self.ai_emos, ais)
        names = adb.sevranchoice(self.ai_names, ais)
        for i in range(ais+1):
            if i == ais:
                if not noPlayer:
                    self.players.append(Player(ctx.author, '🤪', colors[i], t))
                    await ctx.channel.send(f'{ctx.author.mention} 🤪, ваш цвет — {colors[i]}')
            else:
                self.players.append(Player(ctx.author, emos[i], colors[i], t, ai=names[i]))
                await ctx.channel.send(f'{names[i]} {emos[i]}, ваш цвет — {colors[i]}')
        self.monop_channel = self.bot.get_channel(self.monop_channelid)
        random.shuffle(self.players)
        self.ongame = {'cp_id': 0, 'cur_player': self.players[0], 'status': 'cubes', 'round': 1, 'criminal': '', 'crm_player': None}
        self.w8react = []
        await self.mhelp()
        self.map.show_colors(self.players[1])
        await self.showmap()
        await ctx.send(f"Игра начинается!")
        if self.ongame['cur_player'].AI:
            await self.ai_processing(self.ongame['cur_player'], 'cubes', ctx.message.content)

    @commands.command()
    async def monopoly_stop(self, ctx):
        self.maptype = 0
        self.map = None
        self.mapmes = None
        self.playmes = None
        self.infomes = None
        self.sellmes = None
        self.stockmes = None
        self.trademes = None
        self.curblock = ''
        self.players = []
        self.player_colors = []
        self.w8react = []
        self.on = False
        self.ongame = {}
        self.credits = defaultdict(dict)
        self.pledges = defaultdict(dict)
        self.stocks = []
        self.upgradeFlag = False
        self.userlist = defaultdict(dict)
        self.emosdict = defaultdict(list)
        self.emos = []
        self.ai_emos = []
        self.ai_names = []
        self.timers = []

    @commands.command()
    async def monopoly_pause(self, ctx):
        self.on = False

    @commands.command()
    async def monopoly_on(self, ctx):
        self.on = True

    @commands.command()
    async def monopoly_help(self, ctx):
        await self.mhelp()

    @commands.command()
    async def monopoly(self, ctx, t=0):
        if self.monop_channel:
            evrv = ctx.guild.default_role
            await self.monop_channel.set_permissions(evrv, view_channel=True)
        if t == 'help':
            await self.mhelp()
            return
        if self.ongame:
            await ctx.send(f"Игра уже началась!", delete_after=10)
            return
        if not self.monop_channelid == ctx.channel.id:
            if self.monop_channel:
                monop_channel = self.bot.get_channel(self.monop_channelid)
                await ctx.send(f"Вы не можете играть в этом канале. Играть в {monop_channel.mention}", delete_after=10)
            else:
                await ctx.send("У нас нет канала для монополии. Задать канал командой **monop_setchannel**", delete_after=10)
            return

        self.maptype = int(t)
        self.map = Map(self.maptype)

        db = sqlite3.connect(os.path.join(self.DIR, "Akari.db"))
        SQL = db.cursor()

        for m in ctx.guild.members:
            try:
                SQL.execute(f'SELECT bbagid, name, roleid FROM exp WHERE id = {m.id} AND server = {ctx.guild.id}')
                data = SQL.fetchone()
                self.userlist[m.id] = {'id': m.id, 'bbagid': int(data[0]), 'name': data[1], 'roleid': int(data[2])}
            except:
                pass
        db.close()

        self.on = True
        self.player_colors = [pc for pc in player_colors]
        self.emos = [e for e in emos]
        self.ai_names = [a for a in ai_names]
        self.ai_emos = [e for e in ai_emos]
        await ctx.send("Добро пожаловать в Монополию! Ставьте +, чтобы присоединиться, и ++, чтобы закончить набор игроков")

    @commands.command()
    async def monop_setchannel(self, ctx):
        self.monop_channelid = ctx.channel.id
        self.monop_channel = ctx.channel
        await ctx.send(f"Монополия теперь в канале {ctx.channel.mention}", delete_after=10)

    @commands.command()
    async def monopoly_hide(self, ctx, t=0):
        evrv = ctx.guild.default_role
        await self.monop_channel.set_permissions(evrv, view_channel=False)


class Shop:
    def __init__(self, cords, data, number):
        self.cat = 'shop'
        self.shop = data['name']
        self.vinshop = data['name']
        self.rodshop = data['name']
        if 'vin' in data['special']:
            self.vinshop = data['special']['vin']
        if 'rod' in data['special']:
            self.rodshop = data['special']['rod']
        self.monopoly = data['mon_name']
        self.cost = data['buyfor']
        self.mortgage = [self.cost//10, self.cost//2, self.cost, self.cost*2, self.cost*3, self.cost*5]
        self.up = data['up']
        self.icons = iconfinder(data['brief'])
        self.icon = self.icons[0]
        self.raw_icon = self.icons[0]
        self.special = data['special']
        self.level = 0
        self.owner = None
        self.cords = cords
        self.number = number
        self.desc = ''
        self.worth = data['buyfor']
        self.income = 0
        self.in_monopoly = False
        self.buyback = False
        self.stocks = defaultdict(int)
        self.anomale = False

    def get_mort(self):
        try:
            res = self.mortgage[self.level]
        except:
            res = self.mortgage[-1]
        return res

    def __eq__(self, other):
        if not hasattr(other, 'shop'):
            if self.shop == other:
                return True
            return False
        if self.shop == other.shop:
            return True
        return False

    def __str__(self):
        return f'{self.shop}{self.raw_icon} {self.cords} owner={self.owner} level={self.level}'


class Special:
    def __init__(self, cords, typ):
        self.cat = 'special'
        self.type = typ
        self.cords = cords
        self.icons = ['<:mss:829981282649899030>', '<:msp:829981282511486977>', '<:msr:829981282310160414>', '<:msj:829981282167029760>', '<:msc:829981281973567499>', '<:msd:829981282830123059>']
        self.icon = self.icons[typ]
        self.brief = ['start', 'police', 'roulette', 'jail', 'criminal', 'ruins']
        self.roulettes = ['<:msr0:829981282486059038>', '<:msr1:829981282946777088>', '<:msr2:829981282036744203>', '<:msr3:829981282586198036>', '<:msr4:829981282464169984>', '<:msr5:829981282569158676>', '<:msr6:829981282200584243>']
        self.desc = ''
        self.chanced = 0


class Bonus:
    def __init__(self, cords, typ):
        self.cat = 'bonus'
        self.type = typ
        self.cords = cords
        self.icon = '<:msb:829981283366076457>'
        self.desc = ''


class Anti:
    def __init__(self, cords, typ):
        self.cat = 'anti'
        self.type = typ
        self.cords = cords
        self.icon = '<:msa:829981282263629835>'
        self.desc = ''


class Cube:
    def __init__(self, value):
        self.value = value
        self.icon = cube_values[value-1]


class Player:
    def __init__(self, mem, icon, color, mt=0, ai=''):
        self.mem = mem
        self.name = mem.display_name
        self.men = mem.mention
        self.id = mem.id
        self.icon = icon
        self.lockicon = locked_icons[player_colors.index(color)]
        self.levelicons = player_color_icons[player_colors.index(color)]
        self.color = color
        self.nick = color + mem.display_name + icon
        self.money = 15000
        self.cords = adb.monop_sequences[mt][0]
        self.si = 0  # sequence_i
        self.shops = []
        self.monopolies = []
        self.credit = defaultdict(int)
        self.stocks = defaultdict(int)
        self.AI = ai
        if ai:
            self.mem = ai + ' <:msi:830199941640618005>'
            self.name = ai
            self.men = ai + ' <:msi:830199941640618005>'
            self.id = random.randint(100000000, 999999999)
            self.nick = color + self.men + icon
        self.worth = 0
        self.jailed = False
        self.slaps = 0
        self.circle = 0
        self.ikiru = True
        self.cubes = 2

    def show_shops(self):
        res = ''
        for m in self.monopolies:
            for s in self.shops:
                if s.monopoly == m:
                    res += s.icon
            res += '◈'
        for s in self.shops:
            if s.monopoly not in self.monopolies:
                res += s.icon + ' '
        return res

    def to_upgrade(self, ai=''):
        toup = []
        emb_dict = {m: [] for m in self.monopolies}
        for m in self.monopolies:
            for s in self.shops:
                if s.monopoly == m and s.level < 5 and not s.anomale:
                    if ai:
                        toup.append(s)
                    else:
                        toup.append(s.raw_icon)
                        emb_dict[m].append(f'{s.icon}{s.up}')
        backs = []
        for s in self.shops:
            if s.buyback:
                if ai:
                    backs.append(s)
                else:
                    toup.append(s.raw_icon)
                    backs.append(f'{s.icon}{int(s.cost * 0.6)}')
        if ai:
            return toup, backs
        emb = discord.Embed(title='Доступно для апгрейда')
        for m in self.monopolies:
            if emb_dict[m]:
                emb.add_field(name=m, value=' '.join(emb_dict[m]), inline=True)
        if backs:
            emb.add_field(name='Доступно для выкупа', value=' '.join(backs), inline=False)
        return toup, emb

    def to_sell(self, pledge=True, ai=''):
        tosell = []
        emb_dict = {m: [] for m in self.monopolies}
        for m in self.monopolies:
            for s in self.shops:
                if s.monopoly == m and s.level > 0:
                    if ai:
                        tosell.append(s)
                    else:
                        tosell.append(s.raw_icon)
                    emb_dict[m].append(f'{s.icon}{int(s.up * 0.5)}')
        pleds = []
        if pledge or ai:
            for m in self.monopolies:
                mFlag = True
                for s in self.shops:
                    if s.monopoly == m and s.level > 0:
                        mFlag = False
                if mFlag:
                    for s in self.shops:
                        if s.monopoly == m:
                            if ai:
                                pleds.append(s)
                            else:
                                tosell.append(s.raw_icon)
                                pleds.append(f'{s.icon}{int(s.cost * 0.5)}')
            for s in self.shops:
                if s.monopoly not in self.monopolies:
                    if ai:
                        pleds.append(s)
                    else:
                        tosell.append(s.raw_icon)
                        pleds.append(f'{s.icon}{int(s.cost * 0.5)}')
        if ai:
            return tosell, pleds
        emb = discord.Embed(title='Доступно для продажи')
        for m in self.monopolies:
            if emb_dict[m]:
                emb.add_field(name=m, value=' '.join(emb_dict[m]), inline=True)
        if pleds:
            emb.add_field(name='Доступно под залог', value=' '.join(pleds), inline=False)
        return tosell, emb

    def update_shop(self, shop):
        for i in range(len(self.shops)):
            if shop.cat == 'shop':
                if self.shops[i].shop == shop.shop:
                    self.shops[i] = shop

    def get_netmort(self):
        return self.money + int(sum([s.worth for s in self.shops]))

    def get_sellmort(self):
        return self.money + int(sum([s.worth for s in self.shops]) // 2)

    def networth(self):
        res = self.money + self.worth
        return res

    def __eq__(self, other):
        if not other:
            return False
        if self.id == other.id:
            return True
        return False


class Map:
    def __init__(self, typ):
        self.type = typ
        map_grid = adb.monop_maps[typ]
        self.sequence = adb.monop_sequences[typ]
        self.prefs = adb.monop_prefs[typ]
        self.cubes = adb.monop_cubes[typ]
        self.cube_nums = adb.monop_cube_nums[typ]
        sizes = self.prefs[5]
        self.base = [['⬛' for _ in range(sizes[0])] for _ in range(sizes[1])]
        for i in self.cubes:
            self.base[i[0]][i[1]] = '🧊'
        for i in self.sequence:
            self.base[i[0]][i[1]] = '⬜'
        self.blocks = []
        get_shops, self.monopolies = self.get_shops(self.prefs[0])
        shops_idx = 0
        spec_idx = 0
        bonus_idx = 0
        anti_idx = 0
        bonuses = adb.sevranchoice([1, 2, 3, 4], self.prefs[2])
        antis = adb.sevranchoice([1, 2, 3, 4, 5], self.prefs[3])
        for i, s in enumerate(self.sequence):
            ind = map_grid[s[0]][s[1]]
            obj = None
            if ind == 1:
                obj = Shop(s, get_shops[shops_idx], shops_idx)
                shops_idx += 1
            elif ind == 2:
                obj = Special(s, spec_idx)
                spec_idx += 1
            elif ind == 3:
                obj = Bonus(s, bonuses[bonus_idx])
                bonus_idx += 1
            elif ind == 4:
                obj = Anti(s, antis[anti_idx])
                anti_idx += 1
            self.blocks.append(obj)
        #не забыть бум

    def get_shops(self, count):
        res = []
        shops = [i for i in all_shops if i['special'] != 'add' and i['name'] != 'Disabled']  # основные монополии
        addictional = [i for i in all_shops if i['special'] == 'add' and i['name'] != 'Disabled']  # дополнительные могут включиться случайно
        c = 0
        i = 0
        while c != count:  # заполняем res количеством магазов = count
            if c > count:   # если превышает, заменяем одну 4-монополию на 3- и удаляем её из addictional
                idxs = [idx for idx, j in enumerate(res) if j['length'] == 4 and j['special'] != 'shuffled']
                idx = random.choice(idxs)
                res[idx] = random.choice([k for k in addictional if k['length'] == 3])
                del addictional[addictional.index(res[idx])]
                c -= 1
                break
            else:
                res.append(shops[i])
                c += shops[i]['length']
                i += 1

        idxs = []
        for i in addictional: # дополнительные монополии (шанс начать игру не имея ни одной такой = 40,5%)
            if adb.chance(14):
                choice_list = [j for j, k in enumerate(res) if k['length'] == i['length'] and k['special'] != 'shuffled' and j not in idxs]
                if choice_list:
                    idx = random.choice(choice_list)
                    idxs.append(idx) # во избежание замены одной и той же монополии два раза
                    res[idx] = i

        monopolies = {} # список монополий
        mons = [m for m in res]
        for m in mons:
            monopolies[m['name']] = {'name': m['name'], 'length': m['length'], 'special': m['special']}

        shuffled_monopoly = None
        shuf_idxs = [] # добавляем индексы для монополии, ячейки которой разбросаны по всей карте
        if_shuf = [k for k in res if k['special'] == 'shuffled']
        if if_shuf:
            space = count // if_shuf[0]['length'] # для монополии длиной 4 и count = 31: space = 7
            cur_shuf_idx = space // 2             # первая клетка будет иметь индекс 3 (отсчёт от 0)
            shuf_idxs.append(cur_shuf_idx)
            for i in range(1, if_shuf[0]['length']):
                cur_shuf_idx += space             # следующие соответственно: 10, 17, 24
                shuf_idxs.append(cur_shuf_idx)    # разрыв между первым и последним: 11 (в случае с count = 32 будет 8)
            shuffled_monopoly = if_shuf[0]
            del res[res.index(shuffled_monopoly)] # удаляем эту монополию из общего списка и рассматриваем отдельно

        result = [{} for _ in range(count)]
        c = 0
        if shuffled_monopoly:
            for i, shop in enumerate(shuffled_monopoly['shops']):
                result[shuf_idxs[i]] = shop
        for mon in res:
            for shop in mon['shops']:
                while result[c]:
                    c += 1
                result[c] = shop
                c += 1
        return result, monopolies

    def blockinfo(self, player, players):
        si = player.si
        block = self.blocks[player.si]
        res = ''
        if block.cat == 'shop':
            res = f'{block.shop} {block.raw_icon}{block.level*"★"}\n'
            if block.owner:
                res += f'Владелец: {block.owner.nick}\nПрибыль: {block.income}'
                if player.id == block.owner.id:
                    res += f' (Ваш ход)'
                    if block.buyback:
                        res += f' (Под залогом)'
                        res += f'\nПлата: {block.get_mort()}'
                        return res
                    res += f'\nПлата: {block.get_mort()}\n'
                    res += f'Продать акции: {block.cost}\n'
                    res += f'`stocks __%` (до {100 - sum([block.stocks[a] for a in block.stocks])})'
                else:
                    if block.buyback:
                        res += f' (Под  залогом)'
                        res += f'\nПлата: {block.get_mort()}'
                        if block.anomale:
                            res += f'\nЭтот блок подвергся аномалии. В нём нельзя строить филиалы'
                        return res
                    res += f'\nПлата: {block.get_mort()}\n'
                    res += f'`pay {block.get_mort()}`'
            else:
                res += f'Купить: {block.cost}\n'
                res += f'`buy {block.cost}`'
            if block.anomale:
                res += f'\nЭтот блок подвергся аномалии. В нём нельзя строить филиалы'
        if block.cat == 'special':
            if block.type == 0:
                res = f'Старт. Здесь получают деньги. Вы на круге {player.circle}'
            if block.type == 1:
                if player.jailed:
                    res = f'Вы в тюряжке. Вокруг политзеки. Жизнь по понятиям. Падающее мыло. Если хотите выйти, пишите ААА'
                else:
                    jailed = [p.name for p in players if p.jailed]
                    if jailed:
                        res = f'Полицейский участок. Здесь можно навестить {", ".join(jailed)}'
                    else:
                        res = f'Полицейский участок. Здесь пока пусто (пока)'
            if block.type == 2:
                res = 'Заброшенный оружейный склад. Выберите, сколько партонов зарядить в револьвер (0-6)'
            if block.type == 3:
                res = 'Здесь тусуются наркоманы. Сюда часто приезжает полиция и... Они уже здесь'
            if block.type == 4:
                res = 'Криминальная лотерея. Вы сможете сделать много нехороших вещей'
            if block.type == 5:
                res = block.desc
        if block.cat == 'bonus':
            res = 'Лепреконы собрали все свои деньги и бегут сюда по радуге. Здесь вы можете получить бонусы'
        if block.cat == 'anti':
            res = 'Попал сюда — жди беды. Обитель несчастья, суеверий и пиццы с изюмом'
        return res

    def inject_cubes(self, cubes, sum):
        a = adb.sevranchoice(self.cubes, len(cubes))
        for idx, i in enumerate(a):
            self.base[i[0]][i[1]] = cubes[idx].icon
        dec = self.cube_nums[0]
        uni = self.cube_nums[1]
        if sum >= 10:
            self.base[dec[0]][dec[1]] = cube_numbers[sum // 10]
        self.base[uni[0]][uni[1]] = cube_numbers[sum % 10]

    def move_player(self, player, value):
        player.si += value
        if player.si >= len(self.sequence):
            player.si -= len(self.sequence)
            player.circle += 1
            player.money += 2000
        player.cords = self.sequence[player.si]

    def unject_cubes(self):
        for i in self.cubes:
            self.base[i[0]][i[1]] = '🧊'
        for i in self.cube_nums:
            self.base[i[0]][i[1]] = '⬛'

    def show_colors(self, next_player):
        for idx, i in enumerate(self.sequence):
            if self.blocks[idx].cat == 'shop':
                if self.blocks[idx].owner:
                    if self.blocks[idx].buyback:
                        self.base[i[0]][i[1]] = self.blocks[idx].owner.lockicon
                    elif self.blocks[idx].level > 0:
                        self.base[i[0]][i[1]] = self.blocks[idx].owner.shopcolors[self.blocks[idx].level - 1]
                    else:
                        self.base[i[0]][i[1]] = self.blocks[idx].owner.color
                else:
                    self.base[i[0]][i[1]] = '⬜'
        i = next_player.cords
        self.base[i[0]][i[1]] = next_player.icon

    def show_shops(self, players, cur_player):
        for idx, i in enumerate(self.sequence):
            self.base[i[0]][i[1]] = self.blocks[idx].icon
        for p in players:
            if p.ikiru:
                i = p.cords
                self.base[i[0]][i[1]] = p.icon
        i = cur_player.cords
        self.base[i[0]][i[1]] = cur_player.icon

    def __str__(self):
        monopoly = ''
        for i in self.base:
            for j in i:
                monopoly += j
            monopoly += '\n'
        return monopoly


def setup(bot):
    bot.add_cog(Monopoly(bot))
