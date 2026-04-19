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

# Baza danych w pamięci
serwery = {}

def get_data(guild_id):
    if guild_id not in serwery:
        serwery[guild_id] = {"welcome": None, "goodbye": None, "logs": None, "money": {}, "ignore_bots": False}
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

# --- 3. SYSTEM LOGÓW (Z IGNOROWANIEM) ---

class LogsView(View):
    def __init__(self, channel_id):
        super().__init__(timeout=60)
        self.channel_id = channel_id

    @discord.ui.button(label="Ignoruj Boty 🤖", style=discord.ButtonStyle.primary)
    async def ignore_bots(self, interaction: discord.Interaction, button: discord.ui.Button):
        data = get_data(interaction.guild.id)
        data["logs"] = self.channel_id
        data["ignore_bots"] = True
        await interaction.response.edit_message(content=f"📡 Kanał logów ustawiony na <#{self.channel_id}>. Będę ignorować inne boty!", embed=None, view=None)

    @discord.ui.button(label="Pomiń / Loguj wszystko 📄", style=discord.ButtonStyle.secondary)
    async def log_all(self, interaction: discord.Interaction, button: discord.ui.Button):
        data = get_data(interaction.guild.id)
        data["logs"] = self.channel_id
        data["ignore_bots"] = False
        await interaction.response.edit_message(content=f"📡 Kanał logów ustawiony na <#{self.channel_id}>. Będę logować wszystko.", embed=None, view=None)

# --- 4. PRZYCISK WWW ---

class WebsiteView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(discord.ui.Button(label="Otwórz Stronę WWW", url="https://funnyboat.carrd.co"))

# --- 5. KOMENDY ADMINISTRACYJNE ---

@bot.command()
async def welcome(ctx):
    data = get_data(ctx.guild.id)
    data["welcome"] = ctx.channel.id
    await ctx.send(f"✅ Kanał powitań ustawiony na {ctx.channel.mention}!")

@bot.command()
async def goodbye(ctx):
    data = get_data(ctx.guild.id)
    data["goodbye"] = ctx.channel.id
    await ctx.send(f"✅ Kanał pożegnań ustawiony na {ctx.channel.mention}!")

@bot.command()
async def logs(ctx):
    embed = discord.Embed(title="📡 Konfiguracja Logów", description="Czy mam ignorować wiadomości od innych botów?", color=0xbc13fe)
    await ctx.send(embed=embed, view=LogsView(ctx.channel.id))

@bot.command()
async def regulamin(ctx):
    try: await ctx.message.delete()
    except: pass
    await ctx.send(embed=discord.Embed(title="⚓ Panel Regulaminu", description="Wybierz język regulaminu poniżej:", color=0xbc13fe), view=RegulaminView())

@bot.command()
async def setup_tickets(ctx):
    await ctx.send(embed=discord.Embed(title="📩 Wsparcie", description="Kliknij przycisk poniżej, aby otworzyć ticket."), view=TicketView())

# --- 6. EKONOMIA I ZABAWA ---

@bot.command()
async def pomoc(ctx):
    embed = discord.Embed(title="⚓ Panel Komend Funny Boat", color=0xbc13fe)
    embed.add_field(name="⚙️ Ustawienia", value="`!welcome`, `!goodbye`, `!logs`, `!regulamin`, `!setup_tickets`", inline=False)
    embed.add_field(name="💰 Ekonomia", value="`!bal`, `!praca`, `!daily` ", inline=False)
    embed.add_field(name="🎲 Zabawa", value="`!moneta`, `!pirat`, `!ping`, `!ruletka` ", inline=False)
    embed.add_field(name="🌐 Inne", value="`!strona` ", inline=False)
    embed.set_footer(text="funnyboat.carrd.co")
    await ctx.send(embed=embed)

@bot.command()
async def strona(ctx):
    embed = discord.Embed(title="🌐 Oficjalna Strona Funny Boat", description="Kliknij przycisk poniżej, aby nas odwiedzić!", color=0x00aaff)
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
    data = get_data(ctx.guild.id)
    m = data["money"].get(str(ctx.author.id), 0)
    await ctx.send(f"💰 Stan konta: `{m}` monet.")

@bot.command()
async def daily(ctx):
    data = get_data(ctx.guild.id)
    uid = str(ctx.author.id)
    data["money"][uid] = data["money"].get(uid, 0) + 200
    await ctx.send("🎁 Odebrałeś 200 monet!")

@bot.command()
async def moneta(ctx): await ctx.send(f"🪙 Wynik: **{random.choice(['Orzeł', 'Reszka'])}**")
@bot.command()
async def pirat(ctx): await ctx.send(random.choice(["Ahoj!", "Arrr!", "Rum dla wszystkich!"]))
@bot.command()
async def ruletka(ctx): await ctx.send(random.choice(["💥 BOOM!", "🍀 Przeżyłeś!"]))
@bot.command()
async def ping(ctx): await ctx.send(f"🏓 Pong! `{round(bot.latency * 1000)}ms`")

# --- 7. EVENTY ---

@bot.event
async def on_member_join(member):
    data = get_data(member.guild.id)
    if data["welcome"]:
        ch = bot.get_channel(data["welcome"])
        if ch:
            embed = discord.Embed(title="Witaj!", description=f"⚓ Ahoj {member.mention}!", color=0x00ffcc)
            embed.set_thumbnail(url=member.display_avatar.url)
            await ch.send(embed=embed)

@bot.event
async def on_member_remove(member):
    data = get_data(member.guild.id)
    if data["goodbye"]:
        ch = bot.get_channel(data["goodbye"])
        if ch:
            await ch.send(f"🚢 **{member.name}** opuścił pokład.")

@bot.event
async def on_message_delete(message):
    if message.author.bot: return
    data = get_data(message.guild.id)
    if data.get("logs"):
        if data.get("ignore_bots") and message.author.bot: return
        ch = bot.get_channel(data["logs"])
        if ch:
            emb = discord.Embed(title="🗑️ Usunięto wiadomość", color=0xff4747)
            emb.add_field(name="Autor:", value=message.author.mention)
            emb.add_field(name="Treść:", value=message.content or "Plik/Brak tekstu")
            await ch.send(embed=emb)

# --- URUCHOMIENIE ---
token = os.environ.get('DISCORD_TOKEN')
bot.run(token)
