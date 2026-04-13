import os
import asyncio
from datetime import datetime

import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

# ─────────────────────────────────────────────
#  CONFIG
# ─────────────────────────────────────────────
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN není nastavený!")

INTENTS = discord.Intents.default()
INTENTS.message_content = True

bot = commands.Bot(command_prefix="!", intents=INTENTS)
tree = bot.tree

# ─────────────────────────────────────────────
#  DATA
# ─────────────────────────────────────────────
PREDMETY = [
    "Morphine 30mg",
    "Morphine 60mg",
    "Epinephrine",
    "Naloxone",
    "Bandage",
    "Blood Bag",
    "Defibrillator",
    "Oxygen Mask",
    "Splint",
    "Stretcher",
    "Tazer",
    "Tazer Cartridge",
    "Handcuffs",
    "Radio",
    "Vest",
]

HODNOSTI = [
    "Trainee EMS",
    "Junior EMS",
    "EMS",
    "Senior EMS",
    "Supervisor EMS",
    "Lieutenant EMS",
    "Captain EMS",
    "Deputy Chief of EMS",
    "Chief of EMS",
]

DUVODY = [
    "Terénní výjezd",
    "Výcvik",
    "Záloha stanice",
    "Mimořádná situace",
    "Přidělení vozidlu",
    "Jiné",
]

# ─────────────────────────────────────────────
#  AUTOCOMPLETE
# ─────────────────────────────────────────────
async def ac_predmet(interaction: discord.Interaction, current: str):
    return [
        app_commands.Choice(name=p, value=p)
        for p in PREDMETY
        if current.lower() in p.lower()
    ][:25]

async def ac_hodnost(interaction: discord.Interaction, current: str):
    return [
        app_commands.Choice(name=h, value=h)
        for h in HODNOSTI
        if current.lower() in h.lower()
    ][:25]

async def ac_duvod(interaction: discord.Interaction, current: str):
    return [
        app_commands.Choice(name=d, value=d)
        for d in DUVODY
        if current.lower() in d.lower()
    ][:25]

# ─────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────
def parse_datum(raw: str) -> str:
    for fmt in ("%d.%m.%Y", "%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(raw.strip(), fmt).strftime("%d.%m.%Y")
        except ValueError:
            continue
    return raw.strip()

# ─────────────────────────────────────────────
#  COMMAND: /vydejka
# ─────────────────────────────────────────────
@tree.command(name="vydejka", description="Vytvoří výdejku materiálu.")
@app_commands.describe(
    prijemce="Discord @mention",
    jmeno="Celé jméno",
    datum="DD.MM.YYYY",
    predmet="Předmět",
    mnozstvi="Množství",
    duvod="Důvod",
    seriove_cislo="Sériové číslo",
    vydal="Vydal",
    hodnost="Hodnost",
)
@app_commands.autocomplete(predmet=ac_predmet, vydal=ac_hodnost, duvod=ac_duvod)
async def vydejka(
    interaction: discord.Interaction,
    prijemce: str,
    jmeno: str,
    datum: str,
    predmet: str,
    mnozstvi: str,
    duvod: str,
    vydal: str,
    hodnost: str,
    seriove_cislo: str = "—",
):
    datum_fmt = parse_datum(datum)
    now = datetime.now().strftime("%d.%m.%Y %H:%M")

    embed = discord.Embed(
        title="📋 VÝDEJKA MATERIÁLU",
        color=0x1B6CA8,
        timestamp=datetime.utcnow(),
    )

    embed.set_footer(text=f"Vygenerováno: {now}")

    embed.add_field(name="👤 Příjemce", value=prijemce, inline=True)
    embed.add_field(name="📛 Jméno", value=jmeno, inline=True)
    embed.add_field(name="📅 Datum", value=datum_fmt, inline=True)

    embed.add_field(name="📦 Předmět", value=predmet, inline=True)
    embed.add_field(name="🔢 Množství", value=mnozstvi, inline=True)
    embed.add_field(name="🔖 Sériové číslo", value=seriove_cislo, inline=True)

    embed.add_field(name="📝 Důvod", value=duvod, inline=False)

    embed.add_field(name="✍️ Vydal", value=vydal, inline=True)
    embed.add_field(name="🏅 Hodnost", value=hodnost, inline=True)

    await interaction.response.send_message(embed=embed)

# ─────────────────────────────────────────────
#  EVENTS
# ─────────────────────────────────────────────
@bot.event
async def on_ready():
    await tree.sync()
    print(f"✅ Bot běží jako {bot.user}")

@bot.event
async def on_disconnect():
    print("⚠️ Bot odpojen")

@bot.event
async def on_resumed():
    print("🔄 Bot znovu připojen")

# ─────────────────────────────────────────────
#  START
# ─────────────────────────────────────────────
if __name__ == "__main__":
    bot.run(BOT_TOKEN)
