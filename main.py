import discord
from discord.ext import commands
from discord.ui import Button, View
import os
import random
import asyncio

# --- CONFIGURATION ---
intents = discord.Intents.default()
intents.message_content = True
intents.members = True 

bot = commands.Bot(command_prefix="!", intents=intents)

# Database in memory
serwery = {}

def get_data(guild_id):
    if guild_id not in serwery:
        serwery[guild_id] = {"welcome": None, "goodbye": None, "logs": None, "money": {}}
    return serwery[guild_id]

@bot.event
async def on_ready():
    print(f'🚢 Funny Boat is ready! Logged in as: {bot.user.name}')

# --- 1. RULES SYSTEM (MULTI-LANG) ---

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

# --- 2. TICKET SYSTEM ---

class ConfirmCloseView(View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="🗑️ Delete Ticket", style=discord.ButtonStyle.danger)
    async def close(self, interaction, button):
        await interaction.channel.delete()

class TicketView(View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="📩 Open Ticket", style=discord.ButtonStyle.success)
    async def open(self, interaction, button):
        ch = await interaction.guild.create_text_channel(f"ticket-{interaction.user.name}")
        await ch.set_permissions(interaction.guild.default_role, read_messages=False)
        await ch.set_permissions(interaction.user, read_messages=True, send_messages=True)
        await interaction.response.send_message(f"✅ Created: {ch.mention}", ephemeral=True)
        embed = discord.Embed(title="⚓ New Ticket", description="Describe your issue. Click the button below to close this ticket.", color=0x00ffcc)
        await ch.send(embed=embed, view=ConfirmCloseView())

# --- 3. ADMIN COMMANDS ---

@bot.command()
async def welcome(ctx):
    data = get_data(ctx.guild.id)
    data["welcome"] = ctx.channel.id
    await ctx.send(f"✅ Welcome channel set to {ctx.channel.mention}!")

@bot.command()
async def goodbye(ctx):
    data = get_data(ctx.guild.id)
    data["goodbye"] = ctx.channel.id
    await ctx.send(f"✅ Goodbye channel set to {ctx.channel.mention}!")

@bot.command()
async def logs(ctx):
    data = get_data(ctx.guild.id)
    data["logs"] = ctx.channel.id
    await ctx.send(f"📡 Logs channel set successfully!")

@bot.command(name="rules")
async def rules_cmd(ctx):
    await ctx.message.delete()
    await ctx.send(embed=discord.Embed(title="⚓ Regulation Panel", description="Select language / Wybierz język:", color=0xbc13fe), view=RegulaminView())

@bot.command(name="setup_tickets")
async def setup_tickets_cmd(ctx):
    await ctx.send(embed=discord.Embed(title="📩 Support", description="Click the button below to open a ticket."), view=TicketView())

# --- 4. ECONOMY & FUN ---

@bot.command(name="help")
async def help_cmd(ctx):
    embed = discord.Embed(title="⚓ Funny Boat Command Panel", color=0xbc13fe)
    embed.add_field(name="⚙️ Settings", value="`!welcome`, `!goodbye`, `!logs`, `!rules`, `!setup_tickets`", inline=False)
    embed.add_field(name="💰 Economy", value="`!bal`, `!work`, `!daily` ", inline=False)
    embed.add_field(name="🎲 Games", value="`!coin`, `!pirate`, `!ping`, `!roulette` ", inline=False)
    embed.add_field(name="🌐 Others", value="`!website` ", inline=False)
    await ctx.send(embed=embed)

@bot.command(name="work")
async def work_cmd(ctx):
    z = random.randint(20, 100)
    data = get_data(ctx.guild.id)
    uid = str(ctx.author.id)
    data["money"][uid] = data["money"].get(uid, 0) + z
    await ctx.send(f"⚓ You worked hard and earned `{z}` coins!")

@bot.command()
async def bal(ctx):
    data = get_data(ctx.guild.id)
    m = data["money"].get(str(ctx.author.id), 0)
    await ctx.send(f"💰 Balance: `{m}` coins.")

@bot.command()
async def daily(ctx):
    data = get_data(ctx.guild.id)
    uid = str(ctx.author.id)
    data["money"][uid] = data["money"].get(uid, 0) + 200
    await ctx.send("🎁 You claimed your 200 daily coins!")

@bot.command(name="coin")
async def coin_cmd(ctx): await ctx.send(f"🪙 Result: **{random.choice(['Heads', 'Tails'])}**")

@bot.command()
async def pirate(ctx): await ctx.send(random.choice(["Ahoj!", "Arrr!", "Fetch the rum!"]))

@bot.command(name="roulette")
async def roulette_cmd(ctx): await ctx.send(random.choice(["💥 BOOM!", "🍀 You survived!"]))

@bot.command()
async def ping(ctx): await ctx.send(f"🏓 Pong! `{round(bot.latency * 1000)}ms`")

@bot.command(name="website")
async def website_cmd(ctx): await ctx.send("🌐 **funy-boat.carrd.co**")

# --- 5. EVENTS ---

@bot.event
async def on_member_join(member):
    data = get_data(member.guild.id)
    if data["welcome"]:
        ch = bot.get_channel(data["welcome"])
        if ch:
            embed = discord.Embed(title="Welcome on board!", description=f"⚓ Ahoj {member.mention}! Glad you joined us!", color=0x00ffcc)
            embed.set_thumbnail(url=member.display_avatar.url)
            await ch.send(embed=embed)

@bot.event
async def on_member_remove(member):
    data = get_data(member.guild.id)
    if data["goodbye"]:
        ch = bot.get_channel(data["goodbye"])
        if ch:
            embed = discord.Embed(title="Farewell!", description=f"🚢 **{member.name}** left the port. Good luck, pirate!", color=0xff4747)
            embed.set_thumbnail(url=member.display_avatar.url)
            await ch.send(embed=embed)

@bot.event
async def on_message_delete(message):
    data = get_data(message.guild.id)
    if data["logs"] and not message.author.bot:
        ch = bot.get_channel(data["logs"])
        if ch: await ch.send(f"🗑️ **Deleted Message:** {message.author.name}: {message.content}")

# --- START ---
token = os.environ.get('DISCORD_TOKEN')
bot.run(token)
