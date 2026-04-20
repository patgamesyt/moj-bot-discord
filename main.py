import discord
from discord.ext import commands
from discord.ui import Button, View
import os
import random
import asyncio

# --- KONFIGURACJA ---
intents = discord.Intents.default()
intents.message_content = True
intents.members = True 

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# ⚠️ WPISZ TUTAJ SWOJE ID (Prawy klik na Twój profil -> Kopiuj ID)
OWNER_ID = 123456789012345678 

serwery = {}

def get_data(guild_id):
    if guild_id not in serwery:
        serwery[guild_id] = {
            "welcome": None, "goodbye": None, "logs": None, 
            "sugestie_channel": None, "updates_channel": None,
            "money": {}, "ignored_users": []
        }
    return serwery[guild_id]

# --- EVENTY ---

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name="!pomoc | funnyboat.carrd.co"))
    print(f'🚢 Funny Boat gotowy! Zalogowano jako: {bot.user.name}')

@bot.event
async def on_guild_join(guild):
    """Wysyła DM do właściciela po dodaniu bota"""
    owner = guild.owner
    if owner:
        embed = discord.Embed(
            title="⚓ Witaj na pokładzie Funny Boat!",
            description=f"Dzięki za dodanie bota na **{guild.name}**!\n\n"
                        "⚠️ **WAŻNE:** Aby odblokować komendy, musisz ustawić kanał aktualizacji bota.\n"
                        "Wejdź na wybrany kanał i wpisz: `!ustaw`",
            color=0xbc13fe
        )
        try: await owner.send(embed=embed)
        except: pass

# --- SYSTEM BLOKADY I AUTO-SUGESTII ---

@bot.check
async def global_check(ctx):
    # Te komendy działają zawsze
    if ctx.command.name in ["ustaw", "pomoc", "wiadomość"]: return True
    
    data = get_data(ctx.guild.id)
    # Jeśli kanał updatów nie jest ustawiony, blokuj resztę
    if not data["updates_channel"]:
        await ctx.send("❌ **BŁĄD:** Musisz najpierw ustawić kanał aktualizacji bota używając `!ustaw`!")
        return False
    return True

@bot.event
async def on_message(message):
    if message.author.bot or not message.guild: return
    
    data = get_data(message.guild.id)
    
    # Automatyczny system sugestii (bez komendy)
    if data["sugestie_channel"] == message.channel.id and not message.content.startswith('!'):
        content = message.content
        await message.delete()
        emb = discord.Embed(title="💡 Nowa Sugestia", description=content, color=0xffd700)
        emb.set_author(name=message.author.name, icon_url=message.author.display_avatar.url)
        m = await message.channel.send(embed=emb)
        await m.add_reaction("✅"); await m.add_reaction("❌")
        return

    await bot.process_commands(message)

# --- KOMENDY SETUPU (ADMIN) ---

@bot.command()
@commands.has_permissions(administrator=True)
async def ustaw(ctx):
    """Ustawia kanał dla globalnych aktualizacji"""
    get_data(ctx.guild.id)["updates_channel"] = ctx.channel.id
    await ctx.send(f"✅ Kanał {ctx.channel.mention} został wybrany do odbierania aktualizacji bota. Wszystkie komendy zostały odblokowane!")

@bot.command()
@commands.has_permissions(administrator=True)
async def sugestie(ctx):
    """Ustawia kanał dla automatycznych sugestii"""
    get_data(ctx.guild.id)["sugestie_channel"] = ctx.channel.id
    await ctx.send(f"✅ Kanał sugestii ustawiony! Każda wiadomość tutaj zostanie zamieniona w kartę do głosowania.")

# --- TWOJA GLOBALNA KOMENDA (UKRYTA) ---

@bot.command(name="wiadomość")
async def wiadomosc_all(ctx, target: str = None):
    """Komenda tylko dla Ciebie do wysyłania ogłoszeń na wszystkie serwery"""
    if ctx.author.id != OWNER_ID or target != "all": 
        return # Nic nie robi, jeśli ktoś inny użyje

    await ctx.send("📝 Podaj treść globalnej aktualizacji (masz 10 minut):")
    def check(m): return m.author == ctx.author and m.channel == ctx.channel
    try:
        msg = await bot.wait_for('message', check=check, timeout=600)
        emb = discord.Embed(title="🚀 NOWA AKTUALIZACJA FUNNY BOAT", description=msg.content, color=0x00aaff)
        emb.set_thumbnail(url=bot.user.display_avatar.url)
        emb.set_footer(text="Funny Boat Global Update System 🤖")
        
        count = 0
        for guild in bot.guilds:
            data = get_data(guild.id)
            ch_id = data.get("updates_channel")
            if ch_id:
                channel = bot.get_channel(ch_id)
                if channel: 
                    try: 
                        await channel.send(embed=emb)
                        count += 1
                    except: pass
        
        await ctx.send(f"✅ Pomyślnie rozesłano ogłoszenie do `{count}` serwerów!")
        await msg.delete()
    except asyncio.TimeoutError:
        await ctx.send("⏰ Czas na napisanie treści minął.")

# --- KOMENDY POMOCY I MODERACJI ---

@bot.command()
async def pomoc(ctx):
    emb = discord.Embed(title="⚓ Funny Boat - Panel Sterowania", color=0xbc13fe)
    emb.add_field(name="⚙️ Konfiguracja (Admin)", value="`!ustaw`, `!sugestie`, `!welcome`, `!goodbye`, `!logs`, `!setup_tickets`, `!regulamin` ", inline=False)
    emb.add_field(name="🛡️ Moderacja", value="`!clear` ", inline=False)
    emb.add_field(name="💰 Ekonomia", value="`!praca`, `!bal`, `!daily` ", inline=False)
    emb.add_field(name="🎲 Zabawa & Inne", value="`!moneta`, `!ping`, `!strona`, `!ruletka`, `!pirat` ", inline=False)
    emb.set_footer(text="Skonfiguruj kanał aktualizacji (!ustaw), aby używać bota!")
    await ctx.send(embed=emb)

@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int):
    await ctx.channel.purge(limit=amount + 1)
    msg = await ctx.send(f"🧹 Sprzątnięto `{amount}` wiadomości!")
    await asyncio.sleep(3)
    await msg.delete()

# --- EKONOMIA I ZABAWA ---

@bot.command()
async def praca(ctx):
    z = random.randint(20, 100); uid = str(ctx.author.id)
    data = get_data(ctx.guild.id)
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
async def ruletka(ctx): await ctx.send(random.choice(["💥 BOOM!", "🍀 Przeżyłeś!"]))
@bot.command()
async def pirat(ctx): await ctx.send(random.choice(["Ahoj!", "Arrr!", "Gdzie mój rum?", "Szczur lądowy!"]))
@bot.command()
async def ping(ctx): await ctx.send(f"🏓 `{round(bot.latency * 1000)}ms`")

@bot.command()
async def strona(ctx):
    v = View(); v.add_item(discord.ui.Button(label="WWW", url="https://funnyboat.carrd.co"))
    await ctx.send(embed=discord.Embed(title="🌐 Nasza Strona", color=0x00aaff), view=v)

# --- SYSTEMY KONFIGUROWALNE (WIDOKI) ---

class RegulaminView(View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="Ustaw Regulamin 📜", style=discord.ButtonStyle.primary)
    async def set_reg(self, it, bt):
        if not it.user.guild_permissions.administrator: return
        await it.response.send_message("Napisz treść regulaminu:", ephemeral=True)
        def check(m): return m.author == it.user
        msg = await bot.wait_for('message', check=check)
        await it.channel.send(embed=discord.Embed(title="📜 REGULAMIN", description=msg.content, color=0xff0000))

@bot.command()
@commands.has_permissions(administrator=True)
async def regulamin(ctx):
    await ctx.send(view=RegulaminView())

@bot.command()
@commands.has_permissions(administrator=True)
async def welcome(ctx): 
    get_data(ctx.guild.id)["welcome"] = ctx.channel.id
    await ctx.send("✅ Powitania ustawione!")

@bot.command()
@commands.has_permissions(administrator=True)
async def goodbye(ctx): 
    get_data(ctx.guild.id)["goodbye"] = ctx.channel.id
    await ctx.send("✅ Pożegnania ustawione!")

@bot.command()
@commands.has_permissions(administrator=True)
async def logs(ctx):
    get_data(ctx.guild.id)["logs"] = ctx.channel.id
    await ctx.send("✅ Logi będą wysyłane tutaj!")

# --- LOGI (EVENTY) ---

@bot.event
async def on_message_delete(message):
    if message.author.bot: return
    data = get_data(message.guild.id)
    if data.get("logs"):
        if message.author.id in data.get("ignored_users", []): return
        ch = bot.get_channel(data["logs"])
        if ch: await ch.send(f"🗑️ Usunięto: **{message.author.name}**: {message.content}")

token = os.environ.get('DISCORD_TOKEN')
bot.run(token)
