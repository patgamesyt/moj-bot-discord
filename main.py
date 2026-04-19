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
        serwery[guild_id] = {"welcome": None, "goodbye": None, "logs": None, "money": {}, "ignored_users": []}
    return serwery[guild_id]

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name="!pomoc | funnyboat.carrd.co"))
    print(f'🚢 Funny Boat jest gotowy!')

# --- 1. SYSTEM LOGÓW (WIELE OSÓB DO IGNOROWANIA) ---

class LogsView(View):
    def __init__(self, channel_id):
        super().__init__(timeout=60)
        self.channel_id = channel_id

    @discord.ui.button(label="Ignoruj osoby 👤+", style=discord.ButtonStyle.primary)
    async def ignore_users(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("❌ Tylko dla admina!", ephemeral=True)
            
        await interaction.response.send_message("👤 Oznacz teraz jedną lub wiele osób (@użytkownik1 @użytkownik2...), które mam ignorować w logach...", ephemeral=True)
        
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
                imiona = ", ".join(dodani) if dodani else "użytkownicy już byli na liście"
                await interaction.followup.send(f"✅ Teraz ignoruję: **{imiona}**. Logi będą wysyłane na tym kanale.", ephemeral=True)
            else:
                await interaction.followup.send("❌ Nie oznaczyłeś nikogo! Spróbuj ponownie wpisać `!logs`.", ephemeral=True)
        except asyncio.TimeoutError:
            await interaction.followup.send("⏰ Czas minął na oznaczenie osób.", ephemeral=True)

    @discord.ui.button(label="Pomiń / Loguj wszystkich 📄", style=discord.ButtonStyle.secondary)
    async def log_all(self, interaction: discord.Interaction, button: discord.ui.Button):
        data = get_data(interaction.guild.id)
        data["logs"] = self.channel_id
        data["ignored_users"] = [] # Czyścimy całą listę
        await interaction.response.edit_message(content=f"📡 Kanał logów ustawiony na <#{self.channel_id}>. Loguję wszystkich bez wyjątków!", embed=None, view=None)

# --- 2. RESZTA SYSTEMÓW (BEZ ZMIAN) ---

class RegulaminView(View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="Polski PL 🇵🇱", style=discord.ButtonStyle.primary)
    async def pl(self, it, bt):
        await it.response.send_message("📝 Napisz treść regulaminu...", ephemeral=True)
        msg = await bot.wait_for('message', check=lambda m: m.author == it.user, timeout=300)
        await it.channel.send(embed=discord.Embed(title="📜 REGULAMIN", description=msg.content, color=0xff0000))

class TicketView(View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="📩 Otwórz Ticket", style=discord.ButtonStyle.success)
    async def open(self, it, bt):
        ch = await it.guild.create_text_channel(f"ticket-{it.user.name}")
        await ch.set_permissions(it.user, read_messages=True, send_messages=True)
        await it.response.send_message(f"✅ Kanał: {ch.mention}", ephemeral=True)

class WebsiteView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(discord.ui.Button(label="Otwórz Stronę WWW", url="https://funnyboat.carrd.co"))

# --- 3. KOMENDY ---

@bot.command()
async def logs(ctx):
    embed = discord.Embed(title="📡 Konfiguracja Logów", description="Wybierz, czy chcesz zignorować grupę osób, czy logować każdego.", color=0xbc13fe)
    await ctx.send(embed=embed, view=LogsView(ctx.channel.id))

@bot.command()
async def pomoc(ctx):
    embed = discord.Embed(title="⚓ Komendy Funny Boat", color=0xbc13fe)
    embed.add_field(name="⚙️ Admin", value="`!welcome`, `!goodbye`, `!logs`, `!regulamin`, `!setup_tickets`", inline=False)
    embed.add_field(name="💰 Ekonomia", value="`!bal`, `!praca`, `!daily` ", inline=False)
    embed.add_field(name="🎲 Zabawa", value="`!moneta`, `!pirat`, `!ping`, `!strona` ", inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def strona(ctx):
    await ctx.send(embed=discord.Embed(title="🌐 Strona Funny Boat"), view=WebsiteView())

@bot.command()
async def regulamin(ctx): await ctx.send(view=RegulaminView())
@bot.command()
async def setup_tickets(ctx): await ctx.send(view=TicketView())

@bot.command()
async def praca(ctx):
    z = random.randint(20, 100)
    data = get_data(ctx.guild.id)
    data["money"][str(ctx.author.id)] = data["money"].get(str(ctx.author.id), 0) + z
    await ctx.send(f"⚓ Zarobiłeś `{z}` monet!")

@bot.command()
async def bal(ctx):
    m = get_data(ctx.guild.id)["money"].get(str(ctx.author.id), 0)
    await ctx.send(f"💰 Stan konta: `{m}` monet.")

@bot.command()
async def daily(ctx):
    get_data(ctx.guild.id)["money"][str(ctx.author.id)] = get_data(ctx.guild.id)["money"].get(str(ctx.author.id), 0) + 200
    await ctx.send("🎁 Odebrałeś 200 monet!")

@bot.command()
async def moneta(ctx): await ctx.send(f"🪙 **{random.choice(['Orzeł', 'Reszka'])}**")
@bot.command()
async def pirat(ctx): await ctx.send("Arrr! 🏴‍☠️")
@bot.command()
async def ping(ctx): await ctx.send(f"🏓 `{round(bot.latency * 1000)}ms`")

# --- 4. EVENTY ---

@bot.event
async def on_message_delete(message):
    if message.author == bot.user: return
    data = get_data(message.guild.id)
    
    if data.get("logs"):
        # Sprawdzamy, czy autor usuniętej wiadomości jest na liście ignorowanych (ID)
        if message.author.id in data.get("ignored_users", []):
            return
            
        ch = bot.get_channel(data["logs"])
        if ch:
            emb = discord.Embed(title="🗑️ Usunięto wiadomość", color=0xff4747)
            emb.add_field(name="Autor:", value=message.author.mention)
            emb.add_field(name="Kanał:", value=message.channel.mention)
            emb.add_field(name="Treść:", value=message.content or "Brak tekstu/Plik")
            await ch.send(embed=emb)

# --- URUCHOMIENIE ---
token = os.environ.get('DISCORD_TOKEN')
bot.run(token)
