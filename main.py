import discord
from discord.ext import commands
import os
import random

# 1. Podstawowa konfiguracja
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)
db = {} # Tymczasowy portfel bota

@bot.event
async def on_ready():
    print(f'🚢 Zabawna Łódź gotowa! Zalogowano jako: {bot.user.name}')

# 2. Komendy bota
@bot.command()
async def pomoc(ctx):
    embed = discord.Embed(title="⚓ Panel Sterowania Zabawnej Łodzi", color=0xbc13fe)
    embed.add_field(name="🎲 Zabawa", value="`!moneta`, `!pirat`, `!ping` ", inline=False)
    embed.add_field(name="💰 Ekonomia", value="`!bal`, `!daily`, `!praca` ", inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def moneta(ctx):
    wynik = random.choice(["Orzeł! 🦅", "Reszka! 🪙"])
    await ctx.send(f"Wypadło: **{wynik}**")

@bot.command()
async def pirat(ctx):
    teksty = ["Ahoj, kamracie!", "Arrr! Skarb jest blisko!", "Wciągać kotwicę!"]
    await ctx.send(random.choice(teksty))

@bot.command()
async def ping(ctx):
    await ctx.send(f"🏓 Pong! Opóźnienie: **{round(bot.latency * 1000)}ms**")

@bot.command()
async def bal(ctx):
    user_id = str(ctx.author.id)
    money = db.get(user_id, 0)
    await ctx.send(f"💰 {ctx.author.name}, Twój stan konta to: {money} monet.")

@bot.command()
async def praca(ctx):
    user_id = str(ctx.author.id)
    zarobek = random.randint(10, 50)
    db[user_id] = db.get(user_id, 0) + zarobek
    await ctx.send(f"⚓ Zarobiłeś `{zarobek}` monet!")

# 3. Odpalanie bota
token = os.environ.get('DISCORD_TOKEN')
bot.run(token)
