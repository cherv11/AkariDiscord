import asyncio
import discord
from discord.ext import commands
from collections import defaultdict

pong_a = "<:pong_a:986404127988908103>"
pong_z = "<:pong_z:986404133961613342>"
pong_k = "<:pong_k:986404130291580968>"
pong_m = "<:pong_m:986404132174856212>"


class Pong:
    def __init__(self, channel_id, mem1, mem2):
        self.FIELD_SIZE = [70, 25]
        self.paddle_a_y = self.paddle_b_y = self.FIELD_SIZE[1] // 2
        self.ball_cords = [self.FIELD_SIZE[0] // 2, self.FIELD_SIZE[1] // 2]
        self.ball_speed = [2, 2]
        self.a_score, self.b_score = 0, 0
        self.player = 1
        self.channel = channel_id
        self.message = None
        self.active = True
        self.mem1 = mem1
        self.mem2 = mem2
        
    def draw_field(self):
        res = ''
        for y in range(self.FIELD_SIZE[1]+4):
            y -= 3
            res += '|'
            if y == -2:
                sign, a_chars, b_chars = self.FIELD_SIZE[0] // 2, 1, 1
                if self.a_score > 9:
                    a_chars += 1
                if self.b_score > 9:
                    b_chars += 1
                if self.player == 1:
                    a_chars += 1
                else:
                    b_chars += 1
                res += ' '*(sign-a_chars)
                if self.player == 1:
                    res += "<"
                res += f"{self.a_score}:{self.b_score}"
                if self.player == 2:
                    res += ">"
                res += ' '*(self.FIELD_SIZE[0]-(sign+1+b_chars))
                res += '|\n'
                continue
            for x in range(self.FIELD_SIZE[0]):
                if y in [-3, -1, self.FIELD_SIZE[1]]:
                    res += '-'
                elif (x == 0 and -1 <= self.paddle_a_y-y <= 1) or (x == self.FIELD_SIZE[0]-1 and -1 <= self.paddle_b_y-y <= 1):
                    res += '|'
                elif x == self.ball_cords[0] and y == self.ball_cords[1]:
                    res += '@'
                else:
                    res += ' '
            res += "|\n"
        return res
        
    def move_paddle(self, moving_player, value):
        if moving_player == 1:
            self.paddle_a_y = max(min(self.paddle_a_y+value, self.FIELD_SIZE[1]-1), 1) 
        elif moving_player == 2:
            self.paddle_b_y = max(min(self.paddle_b_y+value, self.FIELD_SIZE[1]-1), 1) 
            
    def tick(self):
        self.ball_cords[0] += self.ball_speed[0]
        self.ball_cords[1] += self.ball_speed[1]
        defaultFlag = False
        if self.ball_cords[0] < 1:
            if -1 <= self.ball_cords[1] - self.paddle_a_y <= 1:
                self.ball_cords[0] += (1 - self.ball_cords[0]) * 2
                self.ball_speed[0] *= -1
            else:
                self.b_score += 1
                self.player = 2
                defaultFlag = True
        elif self.ball_cords[0] > self.FIELD_SIZE[0] - 2:
            if -1 <= self.ball_cords[1] - self.paddle_b_y <= 1:
                self.ball_cords[0] += (self.ball_cords[0] - (self.FIELD_SIZE[0]-2)) * 2
                self.ball_speed[0] *= -1
            else:
                self.a_score += 1
                self.player = 1
                defaultFlag = True
        if self.ball_cords[1] < 0:
            self.ball_cords[1] *= -1
            self.ball_speed[1] *= -1
        elif self.ball_cords[1] > self.FIELD_SIZE[1] - 1:
            self.ball_cords[1] -= (self.ball_cords[1] - (self.FIELD_SIZE[1]-1)) * 2
            self.ball_speed[1] *= -1
        if self.a_score > 20:
            self.active = False
            return 1
        if self.b_score > 20:
            self.active = False
            return 2
        if defaultFlag:
            self.set_default_values()
        return 0

    def set_default_values(self):
        self.ball_cords[0] = self.FIELD_SIZE[0] // 2
        self.ball_cords[1] = self.FIELD_SIZE[1] // 2
        self.ball_speed[0] = 1 if self.paddle_a_y % 2 == 0 else -1
        self.ball_speed[1] = 1 if self.paddle_b_y % 2 == 0 else -1
        self.paddle_a_y = self.FIELD_SIZE[0] // 2
        self.paddle_b_y = self.FIELD_SIZE[0] // 2
            

class PongCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.pongs = defaultdict(int)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if self.pongs[payload.channel_id]:
            pong = self.pongs[payload.channel_id]
            if payload.user_id == pong.mem1:
                if payload.emoji == pong_a:
                    pong.move_paddle(1, -1)
                elif payload.emoji == pong_z:
                    pong.move_paddle(1, 1)
            elif payload.user_id == pong.mem2:
                if payload.emoji == pong_k:
                    pong.move_paddle(2, -1)
                elif payload.emoji == pong_m:
                    pong.move_paddle(2, 1)

    @commands.command(aliases=["pong"])
    async def run_pong(self, ctx, mem1: discord.Member, mem2: discord.Member = None):
        if mem2 is None:
            mem2 = mem1
            mem1 = ctx.author
        if not self.pongs[ctx.channel.id]:
            self.pongs[ctx.channel.id] = Pong(ctx.channel.id, mem1.id, mem2.id)
        else:
            self.pongs[ctx.channel.id].mem1 = mem1.id
            self.pongs[ctx.channel.id].mem2 = mem2.id
        pong = self.pongs[ctx.channel.id]
        if not pong.message:
            pong.message = await ctx.send(pong.draw_field())
            await pong.message.add_reaction(pong_a)
            await pong.message.add_reaction(pong_z)
            await pong.message.add_reaction(pong_k)
            await pong.message.add_reaction(pong_m)
        while not self.bot.is_closed() and pong.active:
            await asyncio.sleep(0.5)
            tick = pong.tick()
            if tick:
                await pong.message.channel.send(f"Player {tick} wins!")
                return
            await pong.message.edit(content=pong.draw_field())


def setup(bot):
    bot.add_cog(PongCog(bot))