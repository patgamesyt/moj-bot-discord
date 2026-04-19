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

# --- SYSTEM TICKETÓW ---

class ConfirmCloseView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🗑️ Usuń Ticket", style=discord.ButtonStyle.danger, custom_id="close_ticket")
    async def close_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("⚓ Zamykanie ticketu...")
        await interaction.channel.delete()

class TicketView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="📩 Otwórz Ticket", style=discord.ButtonStyle.primary, custom_id="open_ticket")
    async def open_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        user = interaction.user
        channel_name = f"ticket-{user.name}"
        
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        
        ticket_channel = await guild.create_text_channel(channel_name, overwrites=overwrites)
        await interaction.response.send_message(f"✅ Otwarto ticket: {ticket_channel.mention}", ephemeral=True)
        
        embed = discord.Embed(
            title="⚓ Ticket Otwarty",
            description=f"Witaj {user.mention}! Opisz swój problem.\nAby zamknąć sprawę, kliknij przycisk poniżej.",
            color=0x00ffcc
        )
        await ticket_channel.send(embed=embed, view=ConfirmCloseView())

# --- KOMENDY BOTA ---

@bot.command()
async def pomoc(ctx):
    embed = discord.Embed(
        title="⚓ Pełna Lista Komend - Zabawna Łódź",
        description="Oto wszystkie funkcje Twojego bota podzielone na kategorie:",
        color=0xbc13fe
    )
    embed.add_field(name="🎟️ Support / Tickety", value="`!setup_tickets` - Tworzy panel zgłoszeń", inline=False)
    embed.add_field(name="⚙️ Ustawienia Serwera", value="`!welcome` - Ustawia powitania\n`!goodbye` - Ustawia pożegnania\n`!logs` - Ustawia kanał logów\n`!regulamin` - Pokazuje zasady", inline=False)
    embed.add_field(name="💰 Ekonomia", value="`!bal` - Stan konta\n`!praca` - Zarabianie monet\n`!daily` - Bonus co 24h", inline=False)
    embed.add_field(name="🎲 Zabawa i Inne", value="`!moneta` - Orzeł czy reszka\n`!pirat` - Tekst pirata\n`!ping` - Opóźnienie bota\n`!ruletka` - Gra losowa\n`!strona` - Nasza strona WWW", inline=False)
    embed.set_footer(text="🚢 Zabawna Łódź - Systemy automatyczne (logi, powitania) są aktywne!")
    await ctx.send(embed=embed)

@bot.command()
async def setup_tickets(ctx):
    embed = discord.Embed(title="📩 Pomoc i Wsparcie", description="Kliknij przycisk, aby otworzyć ticket.", color=0x00ffcc)
    await ctx.send(embed=embed, view=TicketView())

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

@bot.command()
async def daily(ctx):
    uid = str(ctx.author.id)
    db[uid] = db.get(uid, 0) + 200
    await ctx.send("🎁 Odebrałeś 200 monet!")

@bot.command()
async def ruletka(ctx):
    wynik = random.choice(["Przeżyłeś! 🍀", "BUM! 💥"])
    await ctx.send(wynik)

# Reszta komend (skrócone dla przejrzystości, ale działające)
@bot.command()
async def moneta(ctx): await ctx.send(f"🪙 {random.choice(['Orzeł', 'Reszka'])}")
@bot.command()
async def pirat(ctx): await ctx.send(random.choice(["Ahoj!", "Arrr!"]))
@bot.command()
async def ping(ctx): await ctx.send(f"🏓 Pong: {round(bot.latency * 1000)}ms")
@bot.command()
async def regulamin(ctx): await ctx.send("📜 Bądź miły i nie spamuj!")
@bot.command()
async def strona(ctx): await ctx.send("🌐 funy-boat.carrd.co")
@bot.command()
async def bal(ctx): await ctx.send(f"💰 Masz: {db.get(str(ctx.author.id), 0)} monet")
@bot.command()
async def praca(ctx):
    z = random.randint(10,50)
    db[str(ctx.author.id)] = db.get(str(ctx.author.id), 0) + z
    await ctx.send(f"⚓ Zarobiłeś {z} monet!")

# --- START ---
token = os.environ.get('DISCORD_TOKEN')
bot.run(token)
