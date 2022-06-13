import discord
from discord.ext import commands
import os
import sqlite3
import time
import shutil
import asyncio
import random
import AkariDB as adb
import math
from collections import defaultdict
import numpy as np


class Tables(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.mainchannel = None
        if not os.path.exists('tables'):
            os.mkdir('tables')

    @commands.Cog.listener()
    async def on_ready(self):
        self.mainchannel = self.bot.get_guild(adb.bbag).get_channel(adb.bbagmain)

    @commands.command()
    async def tablehelp(self, ctx):
        emb = discord.Embed(title='Akari Таблицы')
        emb.add_field(name='Создание таблицы', value='create_table <название> <размеp x> <размер y>\nМаксимальный размер: 75х50')
        await ctx.send(embed=emb)

    @commands.command()
    async def create_table(self, ctx, *args):
        name = ' '.join(args[:-2])
        if f'{name}.npy' in os.listdir(f'tables'):
            await ctx.send('Такая таблица уже есть!')
            return
        x, y = int(args[-2]), int(args[-1])
        if not 0 < x <= 75 or not 0 < y <= 50:
            await ctx.send('Максимальный размер — 75х50!')
            return
        tb = np.zeros((x, y), 'int')
        np.save(f'tables\\{name}', tb)
        await self.show(ctx, name)

    @commands.command()
    async def show(self, ctx, *args):
        name = ' '.join(args)
        if f'{name}.npy' not in os.listdir(f'tables'):
            await ctx.send('Такой таблицы нет!')
            return
        tb = np.load(f'{name}.npy')
        

def setup(bot):
    bot.add_cog(Tables(bot))
