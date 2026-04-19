import discord
from discord.ext import commands
import os
import random

# --- KONFIGURACJA ---
intents = discord.Intents.default()
intents.message_content = True
intents.members = True 

bot = commands.Bot(command_prefix="!", intents=intents)

# Baza danych w pamięci (UWAGA: po restarcie bota dane znikają)
db = {}
ustawienia = {
    "kanal_powitan": None,
    "kanal_pozegnan": None,
    "kanal_logow": None
}

@bot.event
async def on_ready():
    print(f'🚢 Zabawna Łódź gotowa! Zalogowano jako: {bot.user.name}')

# --- 1. SYSTEM POWITAŃ I POŻEGNAŃ ---
@bot.command()
async def welcome(ctx):
    ustawienia["kanal_powitan"] = ctx.channel.id
    await ctx.send(f"✅ Kanał powitań ustawiony na <#{ctx.channel.id}>")

@bot.command()
async def goodbye(ctx):
    ustawienia["kanal_pozegnan"] = ctx.channel.id
    await ctx.send(f"✅ Kanał pożegnań ustawiony na <#{ctx.channel.id}>")

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
    target = ustawienia["kanal_pozegnan"] or ustawienia["kanal_powitan"]
    if target:
        channel = bot.get_channel(target)
        if channel:
            await channel.send(f"🚢 **{member.name}** opuścił port... Żegnaj!")

# --- 2. KOMENDY ZABAWY ---
@bot.command()
async def moneta(ctx):
    await ctx.send(f"Wypadło: **{random.choice(['Orzeł! 🦅', 'Reszka! 🪙'])}**")

@bot.command()
async def pirat(ctx):
    await ctx.send(random.choice(["Ahoj, kamracie!", "Arrr!", "Szczur lądowy na horyzoncie!"]))

@bot.command()
async def ping(ctx):
    await ctx.send(f"🏓 Pong! Opóźnienie: **{round(bot.latency * 1000)}ms**")

@bot.command()
async def ruletka(ctx, stawka: int = 0):
    if random.choice([True, False]):
        await ctx.send(f"💥 BUM! Przegrałeś (stawka: {stawka}).")
    else:
        await ctx.send("🍀 Klik... Miałeś szczęście!")

# --- 3. SYSTEM EKONOMII ---
@bot.command()
async def bal(ctx):
    money = db.get(str(ctx.author.id), 0)
    await ctx.send(f"💰 {ctx.author.name}, masz: **{money}** monet.")

@bot.command()
async def praca(ctx):
    zarobek = random.randint(10, 60)
    uid = str(ctx.author.id)
    db[uid] = db.get(uid, 0) + zarobek
    await ctx.send(f"⚓ {random.choice(['Wyczyściłeś pokład', 'Złowiłeś rybę'])}: Zarobiłeś **{zarobek}** monet!")

@bot.command()
@commands.cooldown(1, 86400, commands.BucketType.user)
async def daily(ctx):
    uid = str(ctx.author.id)
    db[uid] = db.get(uid, 0) + 200
    await ctx.send("🎁 Odebrałeś dzienne 200 monet!")

# --- 4. OGÓLNE I LOGI ---
@bot.command()
async def logs(ctx):
    ustawienia["kanal_logow"] = ctx.channel.id
    await ctx.send(f"📡 Kanał logów ustawiony na <#{ctx.channel.id}>")

@bot.event
async def on_message_delete(message):
    if ustawienia["kanal_logow"]:
        channel = bot.get_channel(ustawienia["kanal_logow"])
        if channel:
            await channel.send(f"🗑️ Usunięto wiadomość od {message.author}: {message.content}")

@bot.command()
async def regulamin(ctx):
    await ctx.send("📜 **Regulamin:** 1. Nie spamuj. 2. Bądź miły. 3. Baw się dobrze!")

@bot.command()
async def strona(ctx):
    await ctx.send("🌐 Nasza strona: **funy-boat.carrd.co**")

@bot.command()
async def pomoc(ctx):
    embed = discord.Embed(title="⚓ Wszystkie Komendy", color=0xbc13fe)
    embed.add_field(name="⚙️ Ustawienia", value="`!welcome`, `!goodbye`, `!logs`, `!regulamin` ", inline=False)
    embed.add_field(name="🎲 Zabawa", value="`!moneta`, `!pirat`, `!ping`, `!ruletka` ", inline=False)
    embed.add_field(name="💰 Ekonomia", value="`!bal`, `!daily`, `!praca` ", inline=False)
    await ctx.send(embed=embed)

# --- START ---
token = os.environ.get('DISCORD_TOKEN')
bot.run(token)
