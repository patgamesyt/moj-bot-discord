import discord
from discord.ext import commands
import os
import random

# --- KONFIGURACJA ---
intents = discord.Intents.default()
intents.message_content = True
intents.members = True # Kluczowe dla powitań!

bot = commands.Bot(command_prefix="!", intents=intents)

# Baza danych w pamięci (zniknie po restarcie bota)
db = {}
ustawienia = {
    "kanal_powitan": None,
    "kanal_logow": None
}

@bot.event
async def on_ready():
    print(f'🚢 Zabawna Łódź gotowa! Zalogowano jako: {bot.user.name}')

# --- SYSTEM POWITAŃ I POŻEGNAŃ ---

@bot.command()
async def welcome(ctx):
    ustawienia["kanal_powitan"] = ctx.channel.id
    await ctx.send(f"⚓ **Kanał powitań ustawiony tutaj!** Będę witał nowych piratów na <#{ctx.channel.id}>.")

@bot.event
async def on_member_join(member):
    if ustawienia["kanal_powitan"]:
        channel = bot.get_channel(ustawienia["kanal_powitan"])
        if channel:
            embed = discord.Embed(title="Witaj / Welcome!", color=0x00ffcc)
            embed.description = f"Ahoj <@{member.id}>!\nPL: Przeczytaj **!regulamin**\nEN: Read **!regulamin AN**"
            embed.set_thumbnail(url=member.display_avatar.url)
            await channel.send(embed=embed)

@bot.event
async def on_member_remove(member):
    if ustawienia["kanal_powitan"]:
        channel = bot.get_channel(ustawienia["kanal_powitan"])
        if channel:
            await channel.send(f"🚢 **{member.name}** opuścił port... Żegnaj piracie!")

# --- KOMENDY ZABAWY I OGÓLNE ---

@bot.command()
async def pomoc(ctx):
    embed = discord.Embed(title="⚓ Panel Sterowania Zabawnej Łodzi", color=0xbc13fe)
    embed.add_field(name="🎲 Zabawa", value="`!moneta`, `!pirat`, `!ping` ", inline=False)
    embed.add_field(name="💰 Ekonomia", value="`!bal`, `!daily`, `!praca` ", inline=False)
    embed.add_field(name="⚙️ Ustawienia", value="`!welcome`, `!logs`, `!regulamin` ", inline=False)
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
async def regulamin(ctx):
    await ctx.send("📜 **Regulamin Serwera:**\n1. Nie spamuj.\n2. Bądź miły dla innych.\n3. Baw się dobrze!")

# --- SYSTEM EKONOMII ---

@bot.command()
async def bal(ctx):
    user_id = str(ctx.author.id)
    money = db.get(user_id, 0)
    await ctx.send(f"💰 {ctx.author.name}, stan konta: {money} monet.")

@bot.command()
async def praca(ctx):
    user_id = str(ctx.author.id)
    zarobek = random.randint(10, 50)
    db[user_id] = db.get(user_id, 0) + zarobek
    await ctx.send(f"⚓ Wykonałeś pracę i zarobiłeś `{zarobek}` monet!")

@bot.command()
@commands.cooldown(1, 86400, commands.BucketType.user) # Raz na 24h
async def daily(ctx):
    user_id = str(ctx.author.id)
    db[user_id] = db.get(user_id, 0) + 200
    await ctx.send("🎁 Odebrałeś 200 dziennych monet!")

# --- START BOTA ---
token = os.environ.get('DISCORD_TOKEN')
bot.run(token)
