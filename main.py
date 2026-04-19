import discord
from discord.ext import commands
from discord.ui import Button, View
import os
import random

# --- KONFIGURACJA ---
intents = discord.Intents.default()
intents.message_content = True
intents.members = True 

bot = commands.Bot(command_prefix="!", intents=intents)

# Baza danych w pamięci
db = {}
ustawienia = {
    "kanal_powitan": None,
    "kanal_pozegnan": None,
    "kanal_logow": None
}

@bot.event
async def on_ready():
    print(f'🚢 Zabawna Łódź gotowa! Zalogowano jako: {bot.user.name}')

# --- 1. SYSTEM TICKETÓW (!setup-tickets) ---

class TicketView(View):
    def __init__(self):
        super().__init__(timeout=None) # Przyciski działają na zawsze

    @discord.ui.button(label="📩 Otwórz Ticket", style=discord.ButtonStyle.primary, custom_id="open_ticket")
    async def button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        user = interaction.user
        
        # Tworzenie nazwy kanału
        channel_name = f"ticket-{user.name}"
        
        # Ustawienia uprawnień: tylko user i admin widzą kanał
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        
        ticket_channel = await guild.create_text_channel(channel_name, overwrites=overwrites)
        await interaction.response.send_message(f"✅ Twój ticket został otwarty: {ticket_channel.mention}", ephemeral=True)
        
        await ticket_channel.send(f"Witaj {user.mention}! Opisz swój problem, a administracja zaraz Ci pomoże. Aby zamknąć ten kanał, administrator musi go usunąć.")

@bot.command()
async def setup_tickets(ctx):
    embed = discord.Embed(
        title="📩 Pomoc i Wsparcie",
        description="Jeśli masz problem lub pytanie do administracji, kliknij przycisk poniżej, aby otworzyć prywatny kanał (ticket).",
        color=0x00ffcc
    )
    await ctx.send(embed=embed, view=TicketView())

# --- 2. POWITANIA I LOGI ---

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
            embed.description = f"Ahoj <@{member.id}>!\nPrzeczytaj **!regulamin**"
            await channel.send(embed=embed)

@bot.command()
async def logs(ctx):
    ustawienia["kanal_logow"] = ctx.channel.id
    await ctx.send(f"📡 Kanał logów ustawiony na <#{ctx.channel.id}>")

@bot.event
async def on_message_delete(message):
    if ustawienia["kanal_logow"] and not message.author.bot:
        channel = bot.get_channel(ustawienia["kanal_logow"])
        if channel:
            await channel.send(f"🗑️ **Usunięto:** {message.author.tag} w <#{message.channel.id}>: {message.content}")

# --- 3. EKONOMIA I ZABAWA ---

@bot.command()
async def bal(ctx):
    money = db.get(str(ctx.author.id), 0)
    await ctx.send(f"💰 {ctx.author.name}, Twój portfel: **{money}** monet.")

@bot.command()
async def praca(ctx):
    zarobek = random.randint(20, 100)
    uid = str(ctx.author.id)
    db[uid] = db.get(uid, 0) + zarobek
    await ctx.send(f"⚓ Zarobiłeś **{zarobek}** monet!")

@bot.command()
async def moneta(ctx):
    await ctx.send(f"🪙 Wypadło: **{random.choice(['Orzeł', 'Reszka'])}**")

@bot.command()
async def pirat(ctx):
    await ctx.send(random.choice(["Ahoj!", "Arrr!", "Gdzie mój skarb?"]))

@bot.command()
async def regulamin(ctx):
    await ctx.send("📜 **Regulamin:** 1. Nie spamuj. 2. Bądź miły. 3. Baw się dobrze!")

@bot.command()
async def pomoc(ctx):
    embed = discord.Embed(title="⚓ Panel Komend Zabawnej Łodzi", color=0xbc13fe)
    embed.add_field(name="🎟️ Support", value="`!setup_tickets`", inline=False)
    embed.add_field(name="⚙️ Ustawienia", value="`!welcome`, `!goodbye`, `!logs`, `!regulamin` ", inline=False)
    embed.add_field(name="💰 Ekonomia", value="`!bal`, `!praca` ", inline=False)
    embed.add_field(name="🎲 Zabawa", value="`!moneta`, `!pirat` ", inline=False)
    await ctx.send(embed=embed)

# --- START ---
token = os.environ.get('DISCORD_TOKEN')
bot.run(token)
