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

bot = commands.Bot(command_prefix="!", intents=intents)

# Baza danych w pamięci (Guild ID jako klucz, żeby każdy serwer miał osobno)
serwery = {}

def get_data(guild_id):
    if guild_id not in serwery:
        serwery[guild_id] = {"welcome": None, "goodbye": None, "logs": None, "money": {}}
    return serwery[guild_id]

@bot.event
async def on_ready():
    print(f'🚢 Zabawna Łódź gotowa! Zalogowano jako: {bot.user.name}')

# --- 1. SYSTEM REGULAMINU (TWOJA SPECJALNA KOMENDA) ---

class RegulaminView(View):
    def __init__(self):
        super().__init__(timeout=60)

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
        await interaction.response.send_message("⚓ Usuwanie kanału...")
        await interaction.channel.delete()

class TicketView(View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="📩 Otwórz Ticket", style=discord.ButtonStyle.success)
    async def open(self, interaction, button):
        ch = await interaction.guild.create_text_channel(f"ticket-{interaction.user.name}")
        await ch.set_permissions(interaction.guild.default_role, read_messages=False)
        await ch.set_permissions(interaction.user, read_messages=True, send_messages=True)
        await interaction.response.send_message(f"✅ Otwarto: {ch.mention}", ephemeral=True)
        embed = discord.Embed(title="⚓ Nowy Ticket", description="Opisz swój problem. Kliknij przycisk, aby usunąć kanał.", color=0x00ffcc)
        await ch.send(embed=embed, view=ConfirmCloseView())

# --- 3. KOMENDY ADMINISTRACYJNE (POWITANIA, POŻEGNANIA, LOGI) ---

@bot.command()
async def welcome(ctx):
    data = get_data(ctx.guild.id)
    data["welcome"] = ctx.channel.id
    await ctx.send(f"✅ Kanał powitań został ustawiony na {ctx.channel.mention}!")

@bot.command()
async def goodbye(ctx):
    data = get_data(ctx.guild.id)
    data["goodbye"] = ctx.channel.id
    await ctx.send(f"✅ Kanał pożegnań został ustawiony na {ctx.channel.mention}!")

@bot.command()
async def logs(ctx):
    data = get_data(ctx.guild.id)
    data["logs"] = ctx.channel.id
    await ctx.send(f"📡 Kanał logów ustawiony na {ctx.channel.mention}!")

@bot.command()
async def regulamin(ctx):
    await ctx.message.delete()
    await ctx.send(embed=discord.Embed(title="⚓ Ustawianie Regulaminu", description="Wybierz język:", color=0xbc13fe), view=RegulaminView())

@bot.command()
async def setup_tickets(ctx):
    await ctx.send(embed=discord.Embed(title="📩 Wsparcie", description="Kliknij, aby otworzyć ticket:"), view=TicketView())

# --- 4. EKONOMIA I ZABAWA ---

@bot.command()
async def pomoc(ctx):
    embed = discord.Embed(title="⚓ Panel Zabawnej Łodzi", color=0xbc13fe)
    embed.add_field(name="⚙️ Admin", value="`!regulamin`, `!setup_tickets`, `!welcome`, `!goodbye`, `!logs`", inline=False)
    embed.add_field(name="💰 Ekonomia", value="`!bal`, `!praca`, `!daily` ", inline=False)
    embed.add_field(name="🎲 Zabawa", value="`!moneta`, `!pirat`, `!ping`, `!ruletka` ", inline=False)
    await ctx.send(embed=embed)

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
async def moneta(ctx): await ctx.send(f"🪙 Wypadło: **{random.choice(['Orzeł', 'Reszka'])}**")
@bot.command()
async def pirat(ctx): await ctx.send(random.choice(["Ahoj!", "Arrr!", "Bierz rum!"]))
@bot.command()
async def ping(ctx): await ctx.send(f"🏓 Pong! `{round(bot.latency * 1000)}ms`")

# --- 5. EVENTY (POWITANIA, POŻEGNANIA, LOGI) ---

@bot.event
async def on_member_join(member):
    data = get_data(member.guild.id)
    if data["welcome"]:
        ch = bot.get_channel(data["welcome"])
        if ch:
            embed = discord.Embed(title="Witaj na pokładzie!", description=f"⚓ Ahoj {member.mention}! Cieszymy się, że jesteś z nami!", color=0x00ffcc)
            await ch.send(embed=embed)

@bot.event
async def on_member_remove(member):
    data = get_data(member.guild.id)
    if data["goodbye"]:
        ch = bot.get_channel(data["goodbye"])
        if ch:
            await ch.send(f"🚢 **{member.name}** opuścił port... Żegnaj piracie!")

@bot.event
async def on_message_delete(message):
    data = get_data(message.guild.id)
    if data["logs"] and not message.author.bot:
        ch = bot.get_channel(data["logs"])
        if ch: await ch.send(f"🗑️ **Usunięto:** {message.author.name}: {message.content}")

# --- START ---
token = os.environ.get('DISCORD_TOKEN')
bot.run(token)
