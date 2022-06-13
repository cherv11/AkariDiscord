import discord
from discord.ext import commands, tasks
import AkariDB as adb
import vk_api
import asyncio
import os
import time
import math
import random
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.longpoll import VkLongPoll, VkEventType
from collections import defaultdict
import json
import requests

start_time = time.time()
group_id = 194025963
vk_session = vk_api.VkApi(token=open('vktoken.txt').readlines()[0])
longpoll = VkBotLongPoll(vk_session, group_id)
vk = vk_session.get_api()

logchannel = None
vkchannel = None
client = discord.Client()
prefix = '*'
bot = commands.Bot(command_prefix=prefix, intents=discord.Intents.all())
bot.remove_command("help")


def sendls(event, mes, keyboard='', att=''):
    user = vk_session.method('users.get', {'user_ids': event.object['message']['from_id'], 'name_case':'dat'})[0]
    print(f"{user['first_name']} {user['last_name']}: {mes}")
    return vk.messages.send(user_id=event.object['message']['from_id'], message=mes, random_id=random.randint(0, 1000000), keyboard=keyboard, attachment=att)


def sendchat(event, mes, keyboard='', att=''):
    user = vk_session.method('users.get', {'user_ids': event.object['message']['from_id'], 'name_case':'dat'})[0]
    print(f"{user['first_name']} {user['last_name']} (беседа): {mes}")
    return vk.messages.send(random_id=random.randint(0, 1000000), message=mes, chat_id=event.chat_id, keyboard=keyboard, attachment=att)


def sendmes(chat_id, mes, keyboard='', att=''):
    print(f"В беседу: {mes}")
    return vk.messages.send(random_id=random.randint(0, 1000000), message=mes, chat_id=chat_id, keyboard=keyboard, attachment=att)


def getbutton(label, color, payload=''):
    return {
        'action': {
            'type': 'text',
            'payload': json.dumps(payload),
            'label': label
        },
        'color': color
    }


def newkb(buttons, ot=False):
    kb = {'one_time': ot, 'buttons': buttons}
    kb = json.dumps(kb, ensure_ascii=False).encode('utf-8')
    kb = str(kb.decode('utf-8'))
    return kb


def postfix(v, ps, rv=True):
    if v % 10 in [0, 5, 6, 7, 8, 9] or v % 100 in [11, 12, 13, 14]:
        p = ps[2]
    elif v % 10 == 1:
        p = ps[0]
    else:
        p = ps[1]
    if rv: return f'{v} {p}'
    return p


def longsplit(mes, n):
    l = len(mes)
    if l <= n:
        return [mes]
    c = math.ceil(l/n)
    res = []
    for i in range(c-1):
        res.append(mes[:n])
        mes = mes[n:]
    res.append(mes)
    return res


antikeyboard = newkb([])
mainkb = newkb([[getbutton('Поддержка 🔨', 'negative'), getbutton('О нас', 'secondary')], [getbutton('Таблица лидеров', 'positive')]], True)


async def vkmessage(obj):
    text = f"α{obj['from_id']}"
    if obj['text']:
        text += f", β{obj['text'][:1800]}"
    if obj['attachments']:
        if obj['attachments'][0]['type'] == 'photo':
            text += f", γ{obj['attachments'][0]['photo']['id']}"
            if obj['text'].startswith(adb.prefix+'ds'):
                name = obj['attachments'][0]['photo']['id']
                pic = requests.get(obj['attachments'][0]['photo']['sizes'][-1]['url'].split('/')[-1])
                pf = open(f'vk\\{name}', 'wb')
                pf.write(pic.content)
                pf.close()
        if obj['attachments'][0]['type'] == 'sticker':
            text += f", δ{obj['attachments'][0]['sticker']['sticker_id']}"
    if len(obj['text']) > 1800:
        text += f", ε{len(obj['text'])}"
    await vkchannel.send(text)
    print(f"Передаю сообщение: id: {obj['from_id']}, text: {obj['text']}, atts: {len(obj['attachments'])}")


async def bbag_listener():
    while not bot.is_closed():
        try:
            for event in longpoll.listen():
                if event.type == VkBotEventType.MESSAGE_NEW:
                    b = event.object['message']['text'].lower()
                    print(event)
                    if event.object['message']['id'] <= 0:              # часть для беседы
                        obj = event.object['message']
                        await vkmessage(obj)
                        if b.startswith('привет'):
                            sendchat(event, 'привет')
                        elif b.startswith('клавиатура'):
                            sendchat(event, 'вотъ', mainkb)
                        elif b.startswith('зиг хайль'):
                            sendchat(event, 'НАШЕСТВИЕ ПОПУГАЕВ')
                            sendchat(event, 'НАШЕСТВИЕ ПОПУГЕЕВ')
                            sendchat(event, 'НАШЕСТВИЕ ПОПУГЕЕВ')
                    else:                                               # часть для лички
                        if b.startswith('привет'):
                            sendls(event, 'ДА РО УУ')
                        elif b.startswith('клавиатура'):
                            sendls(event, 'клава', mainkb)
                        else:
                            sendls(event, 'клаваjkjl')
                await asyncio.sleep(1)
        except Exception as e:
            print(e)
        await asyncio.sleep(1)


@bot.event
async def on_ready():
    global logchannel
    global vkchannel
    gr = 'Птичка в гнезде'
    logchannel = bot.get_channel(adb.botcage)
    vkchannel = bot.get_channel(adb.vkchannel)
    await logchannel.send(gr)
    print(gr)
    bot.loop.create_task(bbag_listener())


@bot.command()
async def ping(ctx):
    await logchannel.send('pong')


token = open('haidori_token.txt').readlines()[0]
bot.run(token)

