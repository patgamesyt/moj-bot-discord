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
bot = commands.Bot(command_prefix="!", intents=intents)
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
