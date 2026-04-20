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
        serwery[guild_id] = {
            "welcome": None, 
            "goodbye": None, 
            "logs": None, 
            "sugestie_channel": None, # Tutaj bot zapisze ID kanału dla sugestii
            "money": {}, 
            "ignored_users": []
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
            return await interaction.response.send_message("❌ Tylko admin!", ephemeral=True)
        await interaction.response.send_message("📝 Napisz treść polskiego regulaminu...", ephemeral=True)
        def check(m): return m.author == interaction.user and m.channel == interaction.channel
        try:
            msg = await bot.wait_for('message', check=check, timeout=300)
            tresc = msg.content
            await msg.delete()
            await interaction.channel.send(embed=discord.Embed(title="📜 REGULAMIN SERWERA", description=tresc, color=0xff0000))
        except asyncio.TimeoutError:
            await interaction.followup.send("⏰ Czas minął.", ephemeral=True)

    @discord.ui.button(label="English EN 🇬🇧", style=discord.ButtonStyle.secondary)
    async def en_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("❌ Only for Admin!", ephemeral=True)
        await interaction.response.send_message("📝 Type the English regulations...", ephemeral=True)
        def check(m): return m.author == interaction.user and m.channel == interaction.channel
        try:
            msg = await bot.wait_for('message', check=check, timeout=300)
            tresc = msg.content
            await msg.delete()
            await interaction.channel.send(embed=discord.Embed(title="📜 SERVER REGULATIONS", description=tresc, color=0x0000ff))
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
        embed = discord.Embed(title="⚓ Nowy Ticket", description="Opisz swój problem. Moderator zaraz pomoże.", color=0x00ffcc)
        await ch.send(embed=embed, view=ConfirmCloseView())

# --- 3. SYSTEM LOGÓW (WIELE OSÓB) ---

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
                await interaction.followup.send(f"✅ Zignorowano: {', '.join(dodani)}", ephemeral=True)
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

# --- 4. KOMENDY ADMINISTRACYJNE (NOWE !SUGESTIE I RESZTA) ---

@bot.command()
@commands.has_permissions(administrator=True)
async def sugestie(ctx):
    """Ustawia kanał, na którym wpisano komendę, jako kanał dla sugestii"""
    data = get_data(ctx.guild.id)
    data["sugestie_channel"] = ctx.channel.id
    await ctx.send(f"✅ Kanał sugestii został pomyślnie ustawiony na {ctx.channel.mention}!")

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
    await ctx.send("📝 Napisz treść ogłoszenia:")
    def check(m): return m.author == ctx.author and m.channel == ctx.channel
    try:
        msg = await bot.wait_for('message', check=check, timeout=300)
        embed = discord.Embed(title="📢 OGŁOSZENIE", description=msg.content, color=0x00aaff)
        embed.set_footer(text=f"Przez: {ctx.author.name}")
        await msg.delete()
        await ctx.channel.send(embed=embed)
    except asyncio.TimeoutError:
        await ctx.send("⏰ Czas minął.")

@bot.command()
async def welcome(ctx):
    get_data(ctx.guild.id)["welcome"] = ctx.channel.id
    await ctx.send(f"✅ Kanał powitań ustawiony!")

@bot.command()
async def goodbye(ctx):
    get_data(ctx.guild.id)["goodbye"] = ctx.channel.id
    await ctx.send(f"✅ Kanał pożegnań ustawiony!")

@bot.command()
async def logs(ctx):
    await ctx.send(embed=discord.Embed(title="📡 Konfiguracja Logów", description="Wybierz opcję poniżej:", color=0xbc13fe), view=LogsView(ctx.channel.id))

@bot.command()
async def regulamin(ctx):
    try: await ctx.message.delete()
    except: pass
    await ctx.send(embed=discord.Embed(title="⚓ Panel Regulaminu", color=0xbc13fe), view=RegulaminView())

@bot.command()
async def setup_tickets(ctx):
    await ctx.send(embed=discord.Embed(title="📩 Wsparcie", description="Kliknij przycisk poniżej."), view=TicketView())

# --- 5. KOMENDY DLA UŻYTKOWNIKÓW (SUGESTIA I EKONOMIA) ---

@bot.command()
async def sugestia(ctx, *, tekst):
    """Wysyła sugestię na ustawiony wcześniej kanał"""
    data = get_data(ctx.guild.id)
    if not data["sugestie_channel"]:
        return await ctx.send("❌ Administrator nie ustawili kanału sugestii! (Użyj `!sugestie`) ")
    
    channel = bot.get_channel(data["sugestie_channel"])
    if channel:
        embed = discord.Embed(title="💡 Nowa Sugestia", description=tekst, color=0xffd700)
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
        msg = await channel.send(embed=embed)
        await msg.add_reaction("✅")
        await msg.add_reaction("❌")
        await ctx.send("✅ Twoja sugestia została wysłana!", delete_after=5)

@bot.command()
async def pomoc(ctx):
    embed = discord.Embed(title="⚓ Panel Funny Boat", color=0xbc13fe)
    embed.add_field(name="⚙️ Ustawienia", value="`!welcome`, `!goodbye`, `!logs`, `!regulamin`, `!sugestie`, `!setup_tickets` ", inline=False)
    embed.add_field(name="🛡️ Admin", value="`!clear`, `!ogloszenie` ", inline=False)
    embed.add_field(name="💰 Ekonomia", value="`!bal`, `!praca`, `!daily` ", inline=False)
    embed.add_field(name="🎲 Reszta", value="`!moneta`, `!ping`, `!strona`, `!sugestia` ", inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def strona(ctx):
    view = View()
    view.add_item(discord.ui.Button(label="Otwórz Stronę WWW", url="https://funnyboat.carrd.co"))
    await ctx.send(embed=discord.Embed(title="🌐 Oficjalna Strona Funny Boat", color=0x00aaff), view=view)

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
async def ping(ctx): await ctx.send(f"🏓 Pong! `{round(bot.latency * 1000)}ms`")
@bot.command()
async def moneta(ctx): await ctx.send(f"🪙 Wynik: **{random.choice(['Orzeł', 'Reszka'])}**")

# --- 6. EVENTY ---

@bot.event
async def on_member_join(member):
    data = get_data(member.guild.id)
    if data["welcome"]:
        ch = bot.get_channel(data["welcome"])
        if ch: await ch.send(embed=discord.Embed(title="Witaj!", description=f"⚓ Ahoj {member.mention}!", color=0x00ffcc))

@bot.event
async def on_member_remove(member):
    data = get_data(member.guild.id)
    if data["goodbye"]:
        ch = bot.get_channel(data["goodbye"])
        if ch: await ch.send(f"🚢 **{member.name}** opuścił załogę.")

@bot.event
async def on_message_delete(message):
    if message.author.bot: return
    data = get_data(message.guild.id)
    if data.get("logs") and message.author.id not in data.get("ignored_users", []):
        ch = bot.get_channel(data["logs"])
        if ch: await ch.send(f"🗑️ **Usunięta wiadomość:** {message.author.name}: {message.content}")

# --- URUCHOMIENIE ---
token = os.environ.get('DISCORD_TOKEN')
bot.run(token)
