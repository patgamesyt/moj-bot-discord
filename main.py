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
ustawienia = {"kanal_powitan": None, "kanal_pozegnan": None, "kanal_logow": None}

@bot.event
async def on_ready():
    print(f'🚢 Zabawna Łódź gotowa! Zalogowano jako: {bot.user.name}')

# --- SYSTEM TICKETÓW ---

# Widok z przyciskiem do usuwania kanału (pojawia się wewnątrz ticketu)
class ConfirmCloseView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🗑️ Usuń Ticket", style=discord.ButtonStyle.danger, custom_id="close_ticket")
    async def close_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("⚓ Zamykanie ticketu za 3 sekundy...")
        await interaction.channel.delete()

# Widok z przyciskiem do otwierania (pojawia się po !setup_tickets)
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
        
        # Wiadomość wewnątrz ticketu z przyciskiem DO USUNIĘCIA
        embed = discord.Embed(
            title="⚓ Ticket Otwarty",
            description=f"Witaj {user.mention}! Opisz swój problem. Administracja zaraz się Tobą zajmie.\n\nPo zakończeniu sprawy kliknij przycisk poniżej, aby usunąć ten kanał.",
            color=0x00ffcc
        )
        await ticket_channel.send(embed=embed, view=ConfirmCloseView())

@bot.command()
async def setup_tickets(ctx):
    embed = discord.Embed(
        title="📩 Pomoc i Wsparcie",
        description="Jeśli potrzebujesz pomocy, kliknij przycisk poniżej, aby otworzyć ticket.",
        color=0xbc13fe
    )
    await ctx.send(embed=embed, view=TicketView())

# --- RESZTA KOMEND (POWITANIA, EKONOMIA, ZABAWA) ---

@bot.command()
async def welcome(ctx):
    ustawienia["kanal_powitan"] = ctx.channel.id
    await ctx.send(f"✅ Ustawiono kanał powitań.")

@bot.command()
async def goodbye(ctx):
    ustawienia["kanal_pozegnan"] = ctx.channel.id
    await ctx.send(f"✅ Ustawiono kanał pożegnań.")

@bot.event
async def on_member_join(member):
    if ustawienia["kanal_powitan"]:
        channel = bot.get_channel(ustawienia["kanal_powitan"])
        if channel:
            await channel.send(f"Ahoj {member.mention}! Witaj na pokładzie!")

@bot.command()
async def moneta(ctx):
    await ctx.send(f"🪙 Wypadło: **{random.choice(['Orzeł', 'Reszka'])}**")

@bot.command()
async def praca(ctx):
    zarobek = random.randint(20, 100)
    db[str(ctx.author.id)] = db.get(str(ctx.author.id), 0) + zarobek
    await ctx.send(f"⚓ Zarobiłeś **{zarobek}** monet!")

@bot.command()
async def bal(ctx):
    money = db.get(str(ctx.author.id), 0)
    await ctx.send(f"💰 Masz: **{money}** monet.")

@bot.command()
async def pomoc(ctx):
    embed = discord.Embed(title="⚓ Lista Komend", color=0xbc13fe)
    embed.add_field(name="🎫 Support", value="`!setup_tickets`", inline=False)
    embed.add_field(name="💰 Ekonomia", value="`!bal`, `!praca` ", inline=False)
    embed.add_field(name="🎲 Zabawa", value="`!moneta` ", inline=False)
    await ctx.send(embed=embed)

# --- START ---
token = os.environ.get('DISCORD_TOKEN')
bot.run(token)
