import discord
from discord.ext import commands
import asyncio
import random
import AkariDB as adb
import math

alphabet = [[':heart:', ':orange_heart:', ':yellow_heart:', ':green_heart:', ':blue_heart:', ':purple_heart:', ':black_heart:', ':brown_heart:', ':white_heart:', ':heartpulse:'],
                         [':red_square:', ':orange_square:', ':yellow_square:', ':green_square:', ':blue_square:',':purple_square:', ':black_large_square:', ':brown_square:', ':white_large_square:', ':white_square_button:'],
                         [':red_circle:', ':orange_circle:', ':yellow_circle:', ':green_circle:', ':blue_circle:', ':purple_circle:', ':black_circle:', ':brown_circle:', ':white_circle:', ':radio_button:'],
                         [':apple:', ':tangerine:', ':lemon:', ':cucumber:', ':teapot:', ':eggplant:', ':cooking:', ':potato:', ':garlic:', ':fish_cake:'],
                         [':crab:', ':orangutan:', ':tropical_fish:', ':beetle:', ':butterfly:', ':octopus:', ':black_cat:', ':monkey:', ':panda_face:', ':squid:']]


class GenX(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.sounds = []
        self.cats = len(alphabet)
        self.colors = len(alphabet[0])
        self.mainchannel = None
        self.dyingFlag = True # Смерть существ, не нашедших себе пару

    @commands.Cog.listener()
    async def on_ready(self):
        self.mainchannel = self.bot.get_guild(adb.bbag).get_channel(adb.programistishe)
        self.bot.loop.create_task(self.tick())

    async def tick(self):
        gener = 0
        while True:
            if len(self.sounds) <= 1:
                await asyncio.sleep(2)
                continue
            new_sounds = []
            died = 0
            ddied = 0
            cells = 0
            half = math.floor(len(self.sounds) / 2)
            random.shuffle(self.sounds)
            one = self.sounds[:half]
            two = self.sounds[half:]
            for i in range(half):
                if one[i].nextgen(two[i]):
                    new_sounds.append(one[i])
                else:
                    died += 2
                    ddied += one[i].length + two[i].length
            if len(self.sounds) % 2 == 1:
                if not self.dyingFlag:
                    new_sounds.append(two[-1])
                else:
                    died += 1
                    ddied += two[-1].length
            self.sounds = new_sounds
            if self.sounds:
                send_list = [str(s) for s in self.sounds]
                cells = sum([s.length for s in self.sounds])
                gener = self.sounds[0].generation
                desc = '\n'.join(send_list)
                if len(desc) > 2000:
                    desc = desc[:2000] + '...'
                emb = discord.Embed(title=f'{gener} поколение', description=desc)
            else:
                emb = discord.Embed(title=f'{gener+1} поколение', description='Нет живых')
            emb.set_footer(text=f'Существ: {len(self.sounds)}, клеток: {cells} // Умерло: {died}, клеток: {ddied}')
            await self.mainchannel.send(embed=emb, delete_after=180)
            await asyncio.sleep(2)

    @commands.command()
    async def simulate(self, ctx, count):
        for i in range(int(count)):
            sound = Sound(random.randrange(0, self.cats), random.randrange(0, self.colors))
            self.sounds.append(Creature([sound], i+1))

    @commands.command()
    async def stop(self):
        self.sounds = []


class Sound:
    def __init__(self, cat, color):
        self.cat = cat
        self.color = color

    def __str__(self):
        return alphabet[self.cat][self.color]

    def __eq__(self, other):
        if self.cat == other.cat and self.color == other.color:
            return True
        return False


class Creature:
    def __init__(self, sounds, num):
        self.length = len(sounds)
        self.gen = sounds
        self.generation = 1
        self.luxury = 0
        self.num = num

    def nextgen(self, other):
        if self.length != other.length:
            print(f'{self.num}-{other.num} Смерть от мутации: неправильная длина')
            return False
        elif self.length == 1:
            if self.gen[0].cat != other.gen[0].cat and self.gen[0].color != other.gen[0].color:
                self.gen += other.gen
                self.length = 2
                self.generation = 1
                return True
            else:
                print(f'{self.num}-{other.num} Смерть на этапе 1')
                return False
        cats = set([i.cat for i in self.gen+other.gen])
        colors = set([i.color for i in self.gen+other.gen])
        cator = (len(cats),len(colors))
        #if self.gen[-1] == other.gen[0]:
            #print(f'{self.num} Смерть от одинаковых концов')
            #return False
        if self.length <= 2:
            for i in self.gen:
                for j in other.gen:
                    if i == j:
                        print(f'{self.num}-{other.num} Смерть от одинаковых клеток на этапе 2')
                        return False
            if cator == (2,2) or cator == (2,3) or cator == (3,2) or cator == (4,2):
                print(f'{self.num}-{other.num} Смерть от плохих генов на этапе 2')
                return False
            self.gen += other.gen
            self.length = 4
            self.generation = 2
            if cator == (2,4) or cator == (3,3) or cator == (4,3):
                self.luxury = 1
            elif cator == (3,4):
                self.luxury = 2
            elif cator == (4,4):
                self.luxury = 3
            return True
        elif self.length <= 4:
             if len(cats) < 5 or len(colors) < 5:
                 print(f'{self.num}-{other.num} Смерть от плохих генов на этапе 3')
                 return False
             gen = self.gen + other.gen
             cur_gen = self.gen[0]
             for i in range(1, self.length+other.length):
                 if cur_gen.cat == gen[i].cat or cur_gen.color == gen[i].color:
                     print(f'{self.num}-{other.num} Смерть от клеток подряд на этапе 3')
                     return False
                 cur_gen = gen[i]
             self.gen += other.gen
             self.length = 8
             self.generation = 3
             return True
        elif self.length <= 8:
            if len(colors) < 9:
                print(f'{self.num}-{other.num} Смерть от плохих генов на этапе 4')
                return False
            self.gen += other.gen
            self.length = 16
            self.generation = 4
            return True
        elif self.length <= 16:
            if len(colors) < 10:
                print(f'{self.num}-{other.num} Смерть от плохих генов на этапе 5')
                return False
            self.gen += other.gen
            self.length = 32
            self.generation = 5
            return True
        elif self.length <= 32:
            self.gen += other.gen
            self.length = 64
            self.generation = 6
            return True
        elif self.length <= 64:
            self.gen += other.gen
            self.length = 128
            self.generation = 7
            return True
        else:
            self.gen += other.gen
            self.length += other.length
            self.generation += 1
            return True

    def nextgen2(self, other):
        if self.length != other.length:
            print(f'{self.num}-{other.num} Смерть от мутации: неправильная длина')
            return False
        elif self.length == 1:
            if self.gen[0].cat == other.gen[0].cat or self.gen[0].color == other.gen[0].color:
                self.gen += other.gen
                self.length = 2
                self.generation = 1
                return True
            else:
                print(f'{self.num}-{other.num} Смерть на этапе 1')
                return False
        cats = set([i.cat for i in self.gen+other.gen])
        colors = set([i.color for i in self.gen+other.gen])
        cator = (len(cats),len(colors))
        if self.length <= 2:
            if cator == (4,4) or cator == (3,4):
                print(f'{self.num}-{other.num} Смерть от плохих генов на этапе 2')
                return False
            self.gen += other.gen
            self.length = 4
            self.generation = 2
            if cator == (2,4) or cator == (3,3) or cator == (4,3):
                self.luxury = 1
            if cator == (2, 2) or cator == (2, 3) or cator == (3, 2) or cator == (4, 2):
                self.luxury = 2
            return True
        elif self.length <= 4:
             if len(cats) > 4 and len(colors) > 4:
                 print(f'{self.num}-{other.num} Смерть от плохих генов на этапе 3')
                 return False
             self.gen += other.gen
             self.length = 8
             self.generation = 3
             return True
        elif self.length <= 8:
            self.gen += other.gen
            self.length = 16
            self.generation = 4
            return True
        elif self.length <= 16:
            self.gen += other.gen
            self.length = 32
            self.generation = 5
            return True
        elif self.length <= 32:
            self.gen += other.gen
            self.length = 64
            self.generation = 6
            return True
        elif self.length <= 64:
            self.gen += other.gen
            self.length = 128
            self.generation = 7
            return True
        elif self.length <= 128:
            self.gen += other.gen
            self.length = 256
            self.generation = 8
            return True
        else:
            self.gen += other.gen
            self.length += other.length
            self.generation += 1
            return True

    def __str__(self):
        sgen = [str(g) for g in self.gen]
        return ''.join(sgen)


def setup(bot):
    bot.add_cog(GenX(bot))
