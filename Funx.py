import discord
from discord.ext import tasks, commands
import os
import sqlite3
import time
import shutil
import asyncio
import random
import AkariDB as adb
from collections import defaultdict
from google_trans_new import google_translator
import requests

translator = google_translator()


class Funx(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.DIR = os.path.dirname(__file__)
        self.reminder_list = []
        self.transchan_mode = 'en'
        self.nikki_en = None
        self.nikki_ja = None
        self.nikki_es = None

    @tasks.loop(seconds=15)
    async def rainbow(self):
        rainbowrole = self.bot.get_guild(adb.dmh).get_role(393305847930945536)
        await rainbowrole.edit(colour=discord.Colour(random.choice(adb.raincolors)))

    @tasks.loop(seconds=adb.reminder_cd)
    async def reminder(self):
        remchannel = self.bot.get_channel(388321118269734922)
        adm = self.bot.get_guild(adb.dmh).get_member(262288342035595268)
        if self.reminder_list:
            async for i in remchannel.history(limit=100):
                if i.embeds:
                    if i.embeds[0].title in adb.businesses:
                        await i.delete()
            emb = discord.Embed(title=random.choice(adb.businesses), colour=random.choice(adb.raincolors))
            for i in range(len(self.reminder_list)):
                t = self.reminder_list[i][1]
                if t <= 0:
                    await remchannel.send(f'{adm.mention}, настала пора {self.reminder_list[i][0]}')
                    del self.reminder_list[i]
                    continue
                send = ""
                if t // 86400 > 0: send += adb.postfix(t // 86400, ['день', 'дня', 'дней']) + ' '
                m = t % 86400
                if m // 3600 > 0: send += adb.postfix(m // 3600, ['час', 'часа', 'часов']) + ' '
                m = m % 3600
                if m // 60 > 0: send += adb.postfix(m // 60, ['минута', 'минуты', 'минут']) + ' '
                m %= 60
                if m >= 0: send += adb.postfix(m, ['секунда', 'секунды', 'секунд'])
                emb.add_field(name=f'{random.choice(adb.business)} #{i + 1}: {self.reminder_list[i][0]}',
                              value=f"Осталось: {send}", inline=False)
                self.reminder_list[i][1] -= adb.reminder_cd
            if len(emb.fields) > 0:
                await remchannel.send(embed=emb)

    @commands.Cog.listener()
    async def on_ready(self):
        self.rainbow.start()
        remchannel = self.bot.get_channel(388321118269734922)
        async for i in remchannel.history(limit=100):
            if i.embeds:
                for f in i.embeds[0].fields:
                    one = f.name.split(':')[1].lstrip()
                    two = 0
                    v = f.value
                    if 'де' in v or 'дн' in v:
                        two += int(v.split('д')[0].split(' ')[-2])
                    if 'ча' in v:
                        two += int(v.split('ча')[0].split(' ')[-2])
                    if 'мин' in v:
                        two += int(v.split('мин')[0].split(' ')[-2])
                    self.reminder_list.append([one, two])
        self.reminder.start()
        self.nikki_en = self.bot.get_channel(adb.nikkis[1])
        self.nikki_ja = self.bot.get_channel(adb.nikkis[2])
        self.nikki_es = self.bot.get_channel(adb.nikkis[3])

    async def nikkisend(self, tr, chan):
        tr1 = ''
        tr2 = ''
        if len(tr[0]) > 1900:
            tr1 = tr[0][1900:]
            tr[0] = tr[0][:1900]
        if tr[2]:
            if len(tr[2]) > 1900:
                tr2 = tr[2][1900:]
                tr[2] = tr[2][:1900]
        await chan.send(tr[0])
        if tr1:
            await chan.send(tr1)
        if tr[2]:
            await chan.send(tr[2])
            if tr2:
                await chan.send(tr2)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.type is discord.MessageType.pins_add:
            await message.delete()
        if message.channel.id == adb.transchan:
            if message.author.bot:
                return
            if message.content.startswith(adb.prefix):
                return
            tr = translator.translate(message.clean_content, lang_tgt=self.transchan_mode, pronounce=True)
            await message.channel.send(tr[0])
            if tr[2]:
                await message.channel.send(tr[2])
        if message.channel.id == adb.nikkis[0] and message.author.id != self.bot.user.id and not message.content.startswith(adb.prefix):
            if message.content:
                tr_en = translator.translate(message.clean_content, lang_tgt='en', pronounce=True)
                tr_ja = translator.translate(message.clean_content, lang_tgt='ja', pronounce=True)
                tr_es = translator.translate(message.clean_content, lang_tgt='es', pronounce=True)
                await self.nikkisend(tr_en, self.nikki_en)
                await self.nikkisend(tr_ja, self.nikki_ja)
                await self.nikkisend(tr_es, self.nikki_es)
            for a in message.attachments:
                if a.filename.endswith((".png", ".jpg", ".gif")):
                    pic = requests.get(a.url)
                    pf = open(a.filename, 'wb')
                    pf.write(pic.content)
                    pf.close()
                    await self.nikki_en.send(file=discord.File(fp=a.filename))
                    await self.nikki_ja.send(file=discord.File(fp=a.filename))
                    await self.nikki_es.send(file=discord.File(fp=a.filename))
                    await asyncio.sleep(1)
                    os.remove(a.filename)

    @commands.command()
    async def imacoder(self, ctx):
        await ctx.send("Мантра программиста перед началом проекта. Аминь", file=adb.progerpic)

    @commands.command()
    async def memeload(self, ctx, de=None):
        if not os.path.exists('memeUpload'):
            os.mkdir('memeUpload')
        for a in os.listdir('memeUpload'):
            if a.endswith((".png", ".jpg", ".gif")):
                file = discord.File(fp=f'memeUpload/{a}')
                try:
                    await ctx.send(file=file)
                    await asyncio.sleep(0.5)
                    if not de:
                        os.remove(f'memeUpload/{a}')
                except:
                    pass

    @commands.command()
    async def clear(self, ctx, amount: int):
        limit = 20
        if amount > limit:
            await ctx.message.delete()
            await ctx.send(f"Не больше {limit}", file=adb.errorpic, delete_after=5)
        else:
            await ctx.channel.purge(limit=amount + 1)
            clearemb = discord.Embed(
                title=f"{random.choice(adb.clears)} {adb.postfix(amount, ['сообщение', 'сообщения', 'сообщений'])}",
                colour=random.choice(adb.raincolors))
            await ctx.send(embed=clearemb, delete_after=5)

    @commands.command()
    async def remind(self, ctx, desc, t='0'):
        if desc == 'delete':
            del self.reminder_list[t-1]
            return
        t = str(t)
        ti = 0
        if 'd' in t: ti += int(t.split('d')[0]) * 86400
        elif 'h' in t: ti += int(t.split('h')[0]) * 3600
        elif 'm' in t: ti += int(t.split('m')[0]) * 60
        else: ti += int(t)
        t = int(ti)
        self.reminder_list.append([desc, t])

    @commands.command()
    async def r(self, ctx, *text: str):
        text = ' '.join(text)
        ctx.send(reversed(text))

    @commands.command()
    async def phrase(self, ctx, *text: str):
        text = ' '.join(text)
        file = open('pips/phrases.txt', 'a', encoding='utf-8')
        file.write(text+'\n')
        file.close()

    async def picfinder(self, text, ch=None):
        if not ch:
            ch = adb.enpics
        async for m in self.bot.get_channel(ch).history():
            if m.content == text:
                if m.attachments:
                    return m.attachments[0].url

    @commands.command()
    async def bigleha(self, ctx):
        one = await self.picfinder('Lt1')
        two = await self.picfinder('Lt2')
        three = await self.picfinder('Lt3')
        four = await self.picfinder('Lt4')
        await ctx.send(one)
        await ctx.send(two)
        await ctx.send(three)
        await ctx.send(four)

    @commands.command()
    async def leha(self, ctx):
        one = await self.picfinder('Lt21')
        two = await self.picfinder('Lt22')
        three = await self.picfinder('Lt23')
        four = await self.picfinder('Lt24')
        await ctx.send(one)
        await ctx.send(two)
        await ctx.send(three)
        await ctx.send(four)

    @commands.command()
    async def trans(self, ctx, url, lang='ru'):
        if url == 'help':
            emb = discord.Embed(description=f'Доступные языки [здесь](https://github.com/lushan88a/google_trans_new/blob/main/constant.py)')
            await ctx.send(embed=emb)
            return
        mes_id = url.split('/')[-1]
        mes = await ctx.message.channel.fetch_message(mes_id)
        tr = translator.translate(mes.clean_content, lang_tgt=lang, pronounce=True)
        emb = discord.Embed(description=f'Перевод:\n{tr[0]}\nПроизношение:{tr[2]}\n\n[Оригинал]({mes.jump_url})')
        emb.set_footer(text=f"{mes.author.name}", icon_url=mes.author.avatar_url)
        await ctx.send(embed=emb)

    @commands.command()
    async def changemode(self, ctx, lang):
        self.transchan_mode = lang
        await ctx.send(f'Language is successfully set to **{lang}**')


def setup(bot):
    bot.add_cog(Funx(bot))
