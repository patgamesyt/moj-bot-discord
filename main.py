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

# Baza danych w pamięci
db = {}
ustawienia = {"kanal_powitan": None, "kanal_pozegnan": None, "kanal_logow": None}

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
            await msg.delete() # Usuwa Twoją wiadomość
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

# --- 3. KOMENDY I SYSTEMY ---

@bot.command()
async def regulamin(ctx):
    await ctx.message.delete()
    await ctx.send(embed=discord.Embed(title="⚓ Ustawianie Regulaminu", description="Wybierz język:", color=0xbc13fe), view=RegulaminView())

@bot.command()
async def setup_tickets(ctx):
    await ctx.send(embed=discord.Embed(title="📩 Wsparcie", description="Kliknij, aby otworzyć ticket:"), view=TicketView())

@bot.command()
async def pomoc(ctx):
    embed = discord.Embed(title="⚓ Panel Zabawnej Łodzi", color=0xbc13fe)
    embed.add_field(name="⚙️ Admin", value="`!regulamin`, `!setup_tickets`, `!welcome`, `!goodbye`, `!logs`", inline=False)
    embed.add_field(name="💰 Ekonomia", value="`!bal`, `!praca`, `!daily`", inline=False)
    embed.add_field(name="🎲 Zabawa", value="`!moneta`, `!pirat`, `!ping`, `!ruletka`", inline=False)
    embed.add_field(name="🌐 Inne", value="`!strona`", inline=False)
    await ctx.send(embed=embed)

# --- EKONOMIA ---
@bot.command()
async def praca(ctx):
    z = random.randint(20, 100)
    db[str(ctx.author.id)] = db.get(str(ctx.author.id), 0) + z
    await ctx.send(f"⚓ Zarobiłeś `{z}` monet!")

@bot.command()
async def bal(ctx):
    await ctx.send(f"💰 Stan konta: `{db.get(str(ctx.author.id), 0)}` monet.")

@bot.command()
@commands.cooldown(1, 86400, commands.BucketType.user)
async def daily(ctx):
    db[str(ctx.author.id)] = db.get(str(ctx.author.id), 0) + 200
    await ctx.send("🎁 Bonus 200 monet odebrany!")

# --- ZABAWA ---
@bot.command()
async def moneta(ctx): await ctx.send(f"🪙 Wypadło: **{random.choice(['Orzeł', 'Reszka'])}**")

@bot.command()
async def pirat(ctx): await ctx.send(random.choice(["Ahoj!", "Arrr!", "Bierz rum!"]))

@bot.command()
async def ruletka(ctx): await ctx.send(random.choice(["💥 BUM!", "🍀 Przeżyłeś!"]))

@bot.command()
async def ping(ctx): await ctx.send(f"🏓 Pong! `{round(bot.latency * 1000)}ms`")

@bot.command()
async def strona(ctx): await ctx.send("🌐 **funy-boat.carrd.co**")

# --- SYSTEMY SERWEROWE ---
@bot.command()
async def welcome(ctx): 
    ustawienia["kanal_powitan"] = ctx.channel.id
    await ctx.send("✅ Kanał powitań ustawiony!")

@bot.command()
async def goodbye(ctx): 
    ustawienia["kanal_pozegnan"] = ctx.channel.id
    await ctx.send("✅ Kanał pożegnań ustawiony!")

@bot.command()
async def logs(ctx): 
    ustawienia["kanal_logow"] = ctx.channel.id
    await ctx.send("📡 Kanał logów ustawiony!")

@bot.event
async def on_member_join(member):
    if ustawienia["kanal_powitan"]:
        ch = bot.get_channel(ustawienia["kanal_powitan"])
        if ch: await ch.send(f"⚓ Witaj na pokładzie {member.mention}!")

@bot.event
async def on_message_delete(message):
    if ustawienia["kanal_logow"] and not message.author.bot:
        ch = bot.get_channel(ustawienia["kanal_logow"])
        if ch: await ch.send(f"🗑️ Usunięto wiadomość od {message.author.name}: {message.content}")

# --- START ---
token = os.environ.get('DISCORD_TOKEN')
bot.run(token)
