import discord
from discord.ext import commands
import os
from flask import Flask
from threading import Thread

# --- SEKCJA UTRZYMYWANIA BOTA (DLA CRON-JOB) ---
app = Flask('')

@app.route('/')
def home():
    return "Funny Boat is Alive!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- SEKCJA BOTA DISCORD ---
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)import discord
from discord.ext import commands
import os
import random

# --- KONFIGURACJA ---
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Baza danych w pamięci
db = {}

@bot.event
async def on_ready():
    print(f'🚢 Zabawna Łódź gotowa! Zalogowano jako: {bot.user.name}')

# --- TWOJE KOMENDY ---

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
async def bal(ctx):
    user_id = str(ctx.author.id)
    money = db.get(user_id, 0)
    await ctx.send(f"💰 {ctx.author.name}, stan konta: {money} monet.")

# --- START BOTA ---
token = os.environ.get('DISCORD_TOKEN')
bot.run(token)
@bot.event
async def on_ready():
    print(f'Zalogowano jako {bot.user.name}')

@bot.command()
async def ping(ctx):
    await ctx.send('Pong!')

# Odpalenie serwera i bota
keep_alive()
# Tutaj musisz wkleić swój TOKEN (patrz krok 3)
import os
bot.run(os.getenv('DISCORD_TOKEN'))
