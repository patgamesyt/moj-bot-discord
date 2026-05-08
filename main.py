import discord
from discord.ext import commands
from discord.ui import Button, View
import os
import random
import asyncio
import aiohttp
import time
import datetime
import re
from flask import Flask
from threading import Thread

# --- DODATEK DLA RENDER.COM (SERWER WWW) ---
app = Flask('')

@app.route('/')
def home():
    return "Funny Boat is Online!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# Uruchomienie udawacza strony www
keep_alive()

# --- TWOJA KONFIGURACJA ---
intents = discord.Intents.default()
intents.message_content = True
intents.members = True 

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# Baza danych w pamięci
serwery = {}
# Przechowuje aktywne zadania konkursów
giveaway_tasks = {}

def get_data(guild_id):
    if guild_id not in serwery:
        serwery[guild_id] = {
            "welcome": None, 
            "goodbye": None, 
            "logs": None, 
            "sugestie_channel": None,
            "money": {}, 
            "ignored_users": [],
            "active_giveaways": {} 
        }
    return serwery[guild_id]

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name="!pomoc | funnyboat.carrd.co"))
    print(f'🚢 Funny Boat jest gotowy! Zalogowano jako: {bot.user.name}')

# --- 1. SYSTEM REGULAMINU ---
class RegulaminView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Polski PL 🇵🇱", style=discord.ButtonStyle.primary)
    async def pl_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("❌ Tylko admin może to zrobić!", ephemeral=True)
        await interaction.response.send_message("📝 Napisz teraz treść polskiego regulaminu na czacie...", ephemeral=True)
        def check(m): return m.author == interaction.user and m.channel == interaction.channel
        try:
            msg = await bot.wait_for('message', check=check, timeout=300)
            tresc = msg.content
            await msg.delete()
            embed = discord.Embed(title="📜 REGULAMIN SERWERA", description=tresc, color=0xff0000)
            await interaction.channel.send(embed=embed)
        except asyncio.TimeoutError:
            await interaction.followup.send("⏰ Czas minął.", ephemeral=True)

    @discord.ui.button(label="English EN 🇬🇧", style=discord.ButtonStyle.secondary)
    async def en_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("❌ Only for Admin!", ephemeral=True)
        await interaction.response.send_message("📝 Type the English regulations now...", ephemeral=True)
        def check(m): return m.author == interaction.user and m.channel == interaction.channel
        try:
            msg = await bot.wait_for('message', check=check, timeout=300)
            tresc = msg.content
            await msg.delete()
            embed = discord.Embed(title="📜 SERVER REGULATIONS", description=tresc, color=0x0000ff)
            await interaction.channel.send(embed=embed)
        except asyncio.TimeoutError:
            await interaction.followup.send("⏰ Timeout.", ephemeral=True)

# --- 2. SYSTEM TICKETÓW ---
class ConfirmCloseView(View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="🗑️ Usuń Ticket", style=discord.ButtonStyle.danger)
    async def close(self, interaction, button):
        await interaction.channel.delete()

class TicketView(View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="📩 Otwórz Ticket", style=discord.ButtonStyle.success)
    async def open(self, interaction, button):
        ch = await interaction.guild.create_text_channel(f"ticket-{interaction.user.name}")
        await ch.set_permissions(interaction.guild.default_role, read_messages=False)
        await ch.set_permissions(interaction.user, read_messages=True, send_messages=True)
        await interaction.response.send_message(f"✅ Stworzono kanał: {ch.mention}", ephemeral=True)
        embed = discord.Embed(title="⚓ Nowy Ticket", description="Opisz swój problem. Moderator zaraz się Tobą zajmie.", color=0x00ffcc)
        await ch.send(embed=embed, view=ConfirmCloseView())

# --- 3. SYSTEM LOGÓW ---
class LogsView(View):
    def __init__(self, channel_id):
        super().__init__(timeout=60)
        self.channel_id = channel_id

    @discord.ui.button(label="Ignoruj osoby 👤+", style=discord.ButtonStyle.primary)
    async def ignore_users(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("❌ Tylko dla admina!", ephemeral=True)
        await interaction.response.send_message("👤 Oznacz teraz osoby (@osoba1 @osoba2...), które mam ignorować...", ephemeral=True)
        def check(m): return m.author == interaction.user and m.channel == interaction.channel
        try:
            msg = await bot.wait_for('message', check=check, timeout=60)
            if msg.mentions:
                data = get_data(interaction.guild.id)
                data["logs"] = self.channel_id
                dodani = []
                for user in msg.mentions:
                    if user.id not in data["ignored_users"]:
                        data["ignored_users"].append(user.id)
                        dodani.append(user.name)
                await msg.delete()
                await interaction.followup.send(f"✅ Ustawiono logi i zignorowano: {', '.join(dodani)}", ephemeral=True)
            else:
                await interaction.followup.send("❌ Nie oznaczyłeś nikogo!", ephemeral=True)
        except asyncio.TimeoutError:
            await interaction.followup.send("⏰ Czas minął.", ephemeral=True)

    @discord.ui.button(label="Pomiń / Loguj wszystkich 📄", style=discord.ButtonStyle.secondary)
    async def log_all(self, interaction: discord.Interaction, button: discord.ui.Button):
        data = get_data(interaction.guild.id)
        data["logs"] = self.channel_id
        data["ignored_users"] = [] 
        await interaction.response.edit_message(content=f"📡 Kanał logów ustawiony! Loguję wszystkich.", embed=None, view=None)

# --- 4. KOMENDY ADMINISTRACYJNE ---
@bot.command()
@commands.has_permissions(administrator=True)
async def sugestie(ctx):
    data = get_data(ctx.guild.id)
    data["sugestie_channel"] = ctx.channel.id
    await ctx.send(f"✅ Ten kanał jest teraz **kanałem sugestii**.")

@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int):
    await ctx.channel.purge(limit=amount + 1)
    msg = await ctx.send(f"🧹 Usunięto `{amount}` wiadomości!")
    await asyncio.sleep(3)
    await msg.delete()

@bot.command()
@commands.has_permissions(administrator=True)
async def ogloszenie(ctx):
    await ctx.send("📝 Napisz treść ogłoszenia (masz 5 minut):")
    def check(m): return m.author == ctx.author and m.channel == ctx.channel
    try:
        msg = await bot.wait_for('message', check=check, timeout=300)
        embed = discord.Embed(title="📢 OGŁOSZENIE", description=msg.content, color=0x00aaff)
        embed.set_footer(text=f"Przez: {ctx.author.name}")
        embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)
        await msg.delete()
        await ctx.channel.send(embed=embed)
    except asyncio.TimeoutError:
        await ctx.send("⏰ Czas na ogłoszenie minął.")

@bot.command()
@commands.has_permissions(administrator=True)
async def welcome(ctx):
    data = get_data(ctx.guild.id)
    data["welcome"] = ctx.channel.id
    await ctx.send(f"✅ Kanał powitań: {ctx.channel.mention}")

@bot.command()
@commands.has_permissions(administrator=True)
async def goodbye(ctx):
    data = get_data(ctx.guild.id)
    data["goodbye"] = ctx.channel.id
    await ctx.send(f"✅ Kanał pożegnań: {ctx.channel.mention}")

@bot.command()
@commands.has_permissions(administrator=True)
async def logs(ctx):
    embed = discord.Embed(title="📡 Konfiguracja Logów", description="Wybierz opcję poniżej:", color=0xbc13fe)
    await ctx.send(embed=embed, view=LogsView(ctx.channel.id))

@bot.command()
@commands.has_permissions(administrator=True)
async def regulamin(ctx):
    try: await ctx.message.delete()
    except: pass
    await ctx.send(embed=discord.Embed(title="⚓ Panel Regulaminu", description="Wybierz język poniżej:", color=0xbc13fe), view=RegulaminView())

@bot.command()
@commands.has_permissions(administrator=True)
async def setup_tickets(ctx):
    await ctx.send(embed=discord.Embed(title="📩 Wsparcie", description="Kliknij przycisk, aby otworzyć ticket."), view=TicketView())

# --- 5. SYSTEM LFG (SZUKANIE EKIPY) ---
@bot.command()
async def lfg(ctx, *, gra_i_opis):
    embed = discord.Embed(title="🎮 POSZUKIWANI GRACZE!", description=f"**Gra/Opis:** {gra_i_opis}", color=0x00ff00)
    embed.add_field(name="Lider załogi", value=ctx.author.mention)
    embed.set_thumbnail(url=ctx.author.display_avatar.url)
    embed.set_footer(text="Kliknij ⚔️ pod tą wiadomością, aby dołączyć!")
    msg = await ctx.send(content="@here", embed=embed)
    await msg.add_reaction("⚔️")

# --- 6. EKONOMIA I ZABAWA ---
class WebsiteView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(discord.ui.Button(label="Otwórz Stronę WWW", url="https://funnyboat.carrd.co"))

@bot.command()
async def pomoc(ctx):
    embed = discord.Embed(title="⚓ Panel Komend Funny Boat", color=0xbc13fe)
    embed.add_field(name="⚙️ Administracja", value="`!welcome`, `!goodbye`, `!logs`, `!regulamin`, `!setup_tickets`, `!clear`, `!ogloszenie`, `!sugestie`, `!gstart`, `!gend` ", inline=False)
    embed.add_field(name="🎮 Gaming", value="`!lfg`, `!kalkulator`", inline=False)
    embed.add_field(name="💰 Ekonomia", value="`!bal`, `!praca`, `!daily` ", inline=False)
    embed.add_field(name="🎲 Zabawa & Inne", value="`!moneta`, `!pirat`, `!ping`, `!ruletka`, `!strona`, `!avatar`, `!memy` ", inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def strona(ctx):
    embed = discord.Embed(title="🌐 Oficjalna Strona Funny Boat", description="Kliknij przycisk poniżej!", color=0x00aaff)
    await ctx.send(embed=embed, view=WebsiteView())

@bot.command()
async def praca(ctx):
    z = random.randint(20, 100)
    data = get_data(ctx.guild.id)
    uid = str(ctx.author.id)
    data["money"][uid] = data["money"].get(uid, 0) + z
    await ctx.send(f"⚓ Zarobiłeś `{z}` monet!")

@bot.command()
async def bal(ctx):
    m = get_data(ctx.guild.id)["money"].get(str(ctx.author.id), 0)
    await ctx.send(f"💰 Stan konta: `{m}` monet.")

@bot.command()
async def daily(ctx):
    uid = str(ctx.author.id)
    get_data(ctx.guild.id)["money"][uid] = get_data(ctx.guild.id)["money"].get(uid, 0) + 200
    await ctx.send("🎁 Odebrałeś codzienne 200 monet!")

@bot.command()
async def moneta(ctx): await ctx.send(f"🪙 Wynik: **{random.choice(['Orzeł', 'Reszka'])}**")
@bot.command()
async def pirat(ctx): await ctx.send(random.choice(["Ahoj!", "Arrr!", "Podajcie rum!"]))
@bot.command()
async def ruletka(ctx): await ctx.send(random.choice(["💥 BOOM!", "🍀 Przeżyłeś!"]))
@bot.command()
async def ping(ctx): await ctx.send(f"🏓 Pong! `{round(bot.latency * 1000)}ms`")

@bot.command()
async def kalkulator(ctx, *, rownanie):
    try:
        wynik = eval(rownanie, {"__builtins__": None}, {})
        await ctx.send(f"🧮 Wynik: **{wynik}**")
    except:
        await ctx.send("❌ Błędne działanie!")

@bot.command()
async def avatar(ctx, member: discord.Member = None):
    member = member or ctx.author
    embed = discord.Embed(title=f"🖼️ Avatar {member.name}", color=0xbc13fe)
    embed.set_image(url=member.display_avatar.url)
    await ctx.send(embed=embed)

@bot.command()
async def memy(ctx):
    async with aiohttp.ClientSession() as session:
        async with session.get("https://meme-api.com/gimme") as response:
            data = await response.json()
            embed = discord.Embed(title=data['title'], color=0x00ffcc)
            embed.set_image(url=data['url'])
            await ctx.send(embed=embed)

# --- 7. EVENTY ---
@bot.event
async def on_message(message):
    if message.author.bot: return
    if message.guild:
        data = get_data(message.guild.id)
        if data["sugestie_channel"] == message.channel.id:
            if not message.content.startswith('!'):
                content = message.content
                await message.delete()
                embed = discord.Embed(title="💡 Nowa Sugestia", description=content, color=0xffd700)
                embed.set_author(name=message.author.name, icon_url=message.author.display_avatar.url)
                sug_msg = await message.channel.send(embed=embed)
                await sug_msg.add_reaction("✅")
                await sug_msg.add_reaction("❌")
                return
    await bot.process_commands(message)

@bot.event
async def on_member_join(member):
    data = get_data(member.guild.id)
    if data["welcome"]:
        ch = bot.get_channel(data["welcome"])
        if ch:
            embed = discord.Embed(title="Witaj na pokładzie! ⚓", description=f"Ahoj {member.mention}!", color=0x00ffcc)
            await ch.send(embed=embed)

@bot.event
async def on_member_remove(member):
    data = get_data(member.guild.id)
    if data["goodbye"]:
        ch = bot.get_channel(data["goodbye"])
        if ch:
            embed = discord.Embed(title="Pirat odpłynął... 🚢", description=f"**{member.name}** opuścił nas.", color=0xff4500)
            await ch.send(embed=embed)

@bot.event
async def on_message_delete(message):
    if not message.guild: return
    data = get_data(message.guild.id)
    if data.get("logs"):
        if message.author.id in data.get("ignored_users", []): return
        if message.author.bot: return
        ch = bot.get_channel(data["logs"])
        if ch: await ch.send(f"🗑️ **Usunięta wiadomość:** {message.author.name}: {message.content}")

# --- SYSTEM GIVEAWAY ---
def parse_duration(duration_str):
    time_units = {"s": 1, "m": 60, "g": 3600, "d": 86400, "t": 604800}
    match = re.match(r"(\d+)([smgdt])", duration_str.lower())
    if not match: return None
    val, unit = match.groups()
    return int(val) * time_units[unit]

@bot.command()
@commands.has_permissions(administrator=True)
async def gstart(ctx):
    def check(m): return m.author == ctx.author and m.channel == ctx.channel
    
    await ctx.send("🕒 **Czas trwania?** (np. 10s, 5m, 1g):")
    try:
        msg = await bot.wait_for('message', check=check, timeout=60)
        seconds = parse_duration(msg.content)
        if seconds is None: return await ctx.send("❌ Błędny format!")
    except asyncio.TimeoutError: return await ctx.send("⏰ Czas minął.")

    await ctx.send("🎁 **Nagroda?**:")
    msg = await bot.wait_for('message', check=check, timeout=60)
    prize = msg.content

    await ctx.send("👥 **Ilu zwycięzców?**:")
    msg = await bot.wait_for('message', check=check, timeout=60)
    try: winners_count = int(msg.content)
    except: winners_count = 1

    end_time = int(time.time() + seconds)
    embed = discord.Embed(title="🎉 NOWY GIVEAWAY!", description=f"Nagroda: **{prize}**\n\nKoniec: <t:{end_time}:R>", color=0x00ff00)
    embed.set_footer(text=f"Zwycięzcy: {winners_count}")
    g_msg = await ctx.send(embed=embed)
    await g_msg.add_reaction("🎉")

    task = asyncio.create_task(run_giveaway(ctx, g_msg, seconds, prize, winners_count))
    giveaway_tasks[ctx.guild.id] = {"task": task, "msg": g_msg}

async def run_giveaway(ctx, g_msg, seconds, prize, winners_count):
    try:
        await asyncio.sleep(seconds)
        msg = await ctx.channel.fetch_message(g_msg.id)
        reaction = discord.utils.get(msg.reactions, emoji="🎉")
        
        users = []
        async for user in reaction.users():
            if not user.bot:
                users.append(user)
        
        if len(users) == 0:
            await ctx.send(f"❌ Nikt nie wygrał **{prize}** (brak uczestników).")
        else:
            winners = random.sample(users, min(len(users), winners_count))
            win_mentions = ", ".join([w.mention for w in winners])
            await ctx.send(f"🎊 Gratulacje {win_mentions}! Wygraliście: **{prize}**!")
        
        try: await msg.delete()
        except: pass
            
    except asyncio.CancelledError:
        try: await g_msg.delete()
        except: pass
    finally:
        giveaway_tasks.pop(ctx.guild.id, None)

@bot.command()
@commands.has_permissions(administrator=True)
async def gend(ctx):
    if ctx.guild.id in giveaway_tasks:
        info = giveaway_tasks[ctx.guild.id]
        info["task"].cancel() 
        await ctx.send("✅ Giveaway został usunięty!", delete_after=5)
    else:
        await ctx.send("❌ Nie ma aktywnego konkursu.")

# --- URUCHOMIENIE (ZMIENIONO NA POBIERANIE TOKENU Z ENV) ---
token = os.environ.get('DISCORD_TOKEN')
if token:
    bot.run(token)
