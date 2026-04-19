import discord
from discord.ext import commands
from discord.ui import Button, View
import os

# --- KONFIGURACJA ---
intents = discord.Intents.default()
intents.message_content = True
intents.members = True 

bot = commands.Bot(command_prefix="!", intents=intents)

# Baza danych w pamięci (Resetuje się przy restarcie bota, chyba że użyjesz bazy danych)
# Struktura: {guild_id: {"pl": "treść", "en": "treść"}}
regulaminy_serwerow = {}

# --- WIDOK Z PRZYCISKAMI ---

class RegulaminView(View):
    def __init__(self, guild_id):
        super().__init__(timeout=60)
        self.guild_id = guild_id

    @discord.ui.button(label="Polski PL 🇵🇱", style=discord.ButtonStyle.primary)
    async def pl_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        data = regulaminy_serwerow.get(self.guild_id, {})
        tresc = data.get("pl")
        
        if not tresc:
            await interaction.response.send_message("❌ Błąd: Regulamin PL nie został jeszcze ustawiony na tym serwerze przez administratora.", ephemeral=True)
        else:
            embed = discord.Embed(title="📜 Regulamin Serwera", description=tresc, color=0xff0000)
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="English EN 🇬🇧", style=discord.ButtonStyle.secondary)
    async def en_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        data = regulaminy_serwerow.get(self.guild_id, {})
        tresc = data.get("en")
        
        if not tresc:
            await interaction.response.send_message("❌ Error: English Regulations have not been set on this server yet.", ephemeral=True)
        else:
            embed = discord.Embed(title="📜 Server Rules", description=tresc, color=0x0000ff)
            await interaction.response.send_message(embed=embed, ephemeral=True)

# --- KOMENDY ---

@bot.command()
async def regulamin(ctx):
    # Usuwamy wiadomość użytkownika (!regulamin)
    try:
        await ctx.message.delete()
    except:
        pass # Jeśli bot nie ma uprawnień do usuwania wiadomości

    view = RegulaminView(ctx.guild.id)
    embed = discord.Embed(
        title="⚓ Wybierz język regulaminu / Choose language",
        description="Kliknij odpowiedni przycisk poniżej:\nClick the button below:",
        color=0xbc13fe
    )
    # Bot wysyła wiadomość od siebie
    await ctx.send(embed=embed, view=view)

@bot.command(name="set-reg-pl")
@commands.has_permissions(administrator=True)
async def set_reg_pl(ctx, *, tresc):
    gid = ctx.guild.id
    if gid not in regulaminy_serwerow:
        regulaminy_serwerow[gid] = {"pl": None, "en": None}
    
    regulaminy_serwerow[gid]["pl"] = tresc
    await ctx.message.delete()
    await ctx.send(f"✅ Polski regulamin został zapisany dla serwera **{ctx.guild.name}**!", delete_after=5)

@bot.command(name="set-reg-en")
@commands.has_permissions(administrator=True)
async def set_reg_en(ctx, *, tresc):
    gid = ctx.guild.id
    if gid not in regulaminy_serwerow:
        regulaminy_serwerow[gid] = {"pl": None, "en": None}
    
    regulaminy_serwerow[gid]["en"] = tresc
    await ctx.message.delete()
    await ctx.send(f"✅ English regulations saved for **{ctx.guild.name}**!", delete_after=5)

# --- RESZTA SYSTEMU (TICKET I POMOC) ---

@bot.command()
async def pomoc(ctx):
    embed = discord.Embed(title="⚓ Panel Pomocy", color=0xbc13fe)
    embed.add_field(name="📜 Regulamin", value="`!regulamin` - Pokazuje przyciski\n`!set-reg-pl [treść]` - Ustawia polski\n`!set-reg-en [treść]` - Ustawia angielski", inline=False)
    await ctx.send(embed=embed)

# --- START ---
token = os.environ.get('DISCORD_TOKEN')
bot.run(token)
