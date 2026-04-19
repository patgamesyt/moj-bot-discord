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

# --- KONFIGURACJA INTENTS ---
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Symulacja bazy danych dla ekonomii (w pamięci bota)
db = {}

@bot.event
async def on_ready():
    print(f'🚢 Zabawna Łódź gotowa! Zalogowano jako: {bot.user.name}')

# --- KOMENDA: !pomoc ---
@bot.command()
async def pomoc(ctx):
    embed = discord.Embed(title="⚓ Panel Sterowania Zabawnej Łodzi", color=0xbc13fe)
    embed.description = "Witaj na pokładzie! Oto dostępne komendy:"
    embed.add_field(name="🎲 Zabawa", value="`!moneta`, `!pirat`, `!ping` ", inline=False)
    embed.add_field(name="💰 Ekonomia", value="`!bal`, `!daily`, `!praca` ", inline=False)
    embed.add_field(name="🛡️ Ogólne", value="`!regulamin`, `!strona` ", inline=False)
    embed.set_footer(text="Funy Boat - Polskie Wydanie")
    await ctx.send(embed=embed)

# --- KOMENDY ZABAWY ---
@bot.command()
async def moneta(ctx):
    wynik = random.choice(["Orzeł! 🦅", "Reszka! 🪙"])
    await ctx.send(f"Wypadło: **{wynik}**")

@bot.command()
async def pirat(ctx):
    teksty = [
        "Ahoj, kamracie! Skarb jest blisko!",
        "Arrr! Kto ukradł moją butelkę soku?",
        "Wciągać kotwicę! Płyniemy na koniec serwera!",
        "Szczur lądowy na horyzoncie! 🏴‍☠️"
    ]
    await ctx.send(random.choice(teksty))

@bot.command()
async def ping(ctx):
    await ctx.send(f"🏓 Pong! Opóźnienie: **{round(bot.latency * 1000)}ms**")

@bot.command()
async def regulamin(ctx):
    await ctx.send("📜 **Regulamin Serwera:**\n1. Nie spamuj.\n2. Bądź miły dla innych piratów.\n3. Baw się dobrze!")

@bot.command()
async def strona(ctx):
    await ctx.send("🌐 Nasza strona: **funy-boat.carrd.co**")

# --- SYSTEM EKONOMII ---
@bot.command()
async def bal(ctx):
    user_id = str(ctx.author.id)
    money = db.get(user_id, 0)
    await ctx.send(f"💰 {ctx.author.name}, Twój stan konta to: {money} monet.")

@bot.command()
@commands.cooldown(1, 604800, commands.BucketType.user) # Raz na tydzień
async def daily(ctx):
    user_id = str(ctx.author.id)
    money = db.get(user_id, 0)
    db[user_id] = money + 500
    await ctx.send(f"🎁 Otrzymałeś swoje codzienne 500 monet! Teraz masz: {db[user_id]}.")

@bot.command()
async def praca(ctx):
    user_id = str(ctx.author.id)
    zarobek = random.randint(10, 50)
    money = db.get(user_id, 0)
    db[user_id] = money + zarobek
    jobs = ["Wyczyściłeś pokład", "Złowiłeś złotą rybkę", "Naprawiłeś żagiel"]
    await ctx.send(f"⚓ {random.choice(jobs)}! Zarobiłeś `{zarobek}` monet.")

# Obsługa błędu cooldownu (jeśli ktoś wpisze !daily za szybko)
@daily.error
async def daily_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"⏳ Nie tak szybko! Kolejny prezent możesz odebrać za kilka dni.")

# --- START BOTA ---
token = os.environ.get('DISCORD_TOKEN')
if token:
    bot.run(token)
else:
    print("BŁĄD: Brak tokena w Variables!")

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
