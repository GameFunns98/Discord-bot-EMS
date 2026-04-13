import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime
import re

# ─────────────────────────────────────────────
#  Konfigurace
# ─────────────────────────────────────────────
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

INTENTS = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=INTENTS)
tree = bot.tree
from keep import keep_alive
import os
from dotenv import load_dotenv
keep_alive()
# ─────────────────────────────────────────────
#  Statické seznamy pro autocomplete
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
#  Autocomplete handlery
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
#  Pomocná funkce – formátování data
# ─────────────────────────────────────────────
def parse_datum(raw: str) -> str:
    """Přijme datum ve formátu DD.MM.YYYY nebo YYYY-MM-DD, vrátí DD.MM.YYYY."""
    for fmt in ("%d.%m.%Y", "%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(raw.strip(), fmt).strftime("%d.%m.%Y")
        except ValueError:
            continue
    return raw.strip()  # vrátí tak jak je, pokud nerozpozná formát

# ─────────────────────────────────────────────
#  /vydejka  – hlavní příkaz
# ─────────────────────────────────────────────
@tree.command(
    name="vydejka",
    description="Vytvoří formální výdejku materiálu / vybavení EMS."
)
@app_commands.describe(
    prijemce_tag="Discord @mention příjemce (např. @Angel)",
    prijemce_jmeno="Celé jméno příjemce (např. M.S. Stanislav Hoppe)",
    datum="Datum výdeje ve formátu DD.MM.YYYY",
    predmet="Vydávaný předmět (vyber ze seznamu nebo dopiš)",
    mnozstvi="Množství a specifikace (např. 20x 30mg)",
    duvod="Důvod výdeje",
    seriove_cislo="Sériové číslo (vyplň pouze pokud relevantní, jinak nech prázdné)",
    vydal_jmeno="Jméno vydávajícího (např. Hoppe)",
    vydal_hodnost="Hodnost vydávajícího",
)
@app_commands.autocomplete(predmet=ac_predmet, vydal_hodnost=ac_hodnost, duvod=ac_duvod)
async def vydejka(
    interaction: discord.Interaction,
    prijemce_tag: str,
    prijemce_jmeno: str,
    datum: str,
    predmet: str,
    mnozstvi: str,
    duvod: str,
    vydal_jmeno: str,
    vydal_hodnost: str,
    seriove_cislo: str = "—",
):
    datum_fmt = parse_datum(datum)
    now = datetime.now().strftime("%d.%m.%Y %H:%M")

    # ── Embed ──────────────────────────────────
    embed = discord.Embed(
        title="📋  VÝDEJKA MATERIÁLU / VYBAVENÍ",
        color=0x1B6CA8,
        timestamp=datetime.utcnow(),
    )
    embed.set_footer(text=f"Vygenerováno: {now}  •  EMS Dispatch System")

    # Sekce: Příjemce
    embed.add_field(name="👤  Příjemce", value=f"{prijemce_tag}", inline=True)
    embed.add_field(name="📛  Jméno a hodnost", value=prijemce_jmeno, inline=True)
    embed.add_field(name="📅  Datum výdeje", value=datum_fmt, inline=True)

    embed.add_field(name="\u200b", value="──────────────────────", inline=False)

    # Sekce: Vydávaný předmět
    embed.add_field(name="📦  Předmět", value=predmet, inline=True)
    embed.add_field(name="🔢  Množství / Specifikace", value=mnozstvi, inline=True)
    embed.add_field(name="🔖  Sériové číslo", value=seriove_cislo, inline=True)

    embed.add_field(name="\u200b", value="──────────────────────", inline=False)

    # Sekce: Důvod
    embed.add_field(name="📝  Důvod výdeje", value=duvod, inline=False)

    embed.add_field(name="\u200b", value="──────────────────────", inline=False)

    # Sekce: Podpis vydávajícího
    embed.add_field(name="✍️  Podpis", value=vydal_jmeno, inline=True)
    embed.add_field(name="🏅  Hodnost", value=vydal_hodnost, inline=True)

    await interaction.response.send_message(embed=embed)


# ─────────────────────────────────────────────
#  /vydejka_tazer  – zkrácená varianta pro Tazer
# ─────────────────────────────────────────────
@tree.command(
    name="vydejka_tazer",
    description="Rychlá výdejka pro Tazer (předvyplněný předmět)."
)
@app_commands.describe(
    prijemce_tag="Discord @mention příjemce",
    prijemce_jmeno="Celé jméno příjemce",
    datum="Datum výdeje DD.MM.YYYY",
    seriove_cislo="Sériové číslo tazeru",
    vydal_jmeno="Jméno vydávajícího",
    vydal_hodnost="Hodnost vydávajícího",
)
@app_commands.autocomplete(vydal_hodnost=ac_hodnost)
async def vydejka_tazer(
    interaction: discord.Interaction,
    prijemce_tag: str,
    prijemce_jmeno: str,
    datum: str,
    seriove_cislo: str,
    vydal_jmeno: str,
    vydal_hodnost: str,
):
    datum_fmt = parse_datum(datum)
    now = datetime.now().strftime("%d.%m.%Y %H:%M")

    embed = discord.Embed(
        title="⚡  VÝDEJKA — TAZER",
        color=0xF0A500,
        timestamp=datetime.utcnow(),
    )
    embed.set_footer(text=f"Vygenerováno: {now}  •  EMS Dispatch System")

    embed.add_field(name="👤  Příjemce", value=prijemce_tag, inline=True)
    embed.add_field(name="📛  Jméno a hodnost", value=prijemce_jmeno, inline=True)
    embed.add_field(name="📅  Datum výdeje", value=datum_fmt, inline=True)

    embed.add_field(name="\u200b", value="──────────────────────", inline=False)

    embed.add_field(name="📦  Předmět", value="Tazer", inline=True)
    embed.add_field(name="🔖  Sériové číslo", value=seriove_cislo, inline=True)
    embed.add_field(name="\u200b", value="\u200b", inline=True)

    embed.add_field(name="\u200b", value="──────────────────────", inline=False)

    embed.add_field(name="✍️  Podpis", value=vydal_jmeno, inline=True)
    embed.add_field(name="🏅  Hodnost", value=vydal_hodnost, inline=True)

    await interaction.response.send_message(embed=embed)


# ─────────────────────────────────────────────
#  On ready + sync
# ─────────────────────────────────────────────
@bot.event
async def on_ready():
    await tree.sync()
    print(f"✅  Bot přihlášen jako {bot.user} | Slash příkazy synchronizovány.")


bot.run(BOT_TOKEN)
