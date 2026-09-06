import discord
from discord.ext import commands
import os
import asyncio
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Configuración
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

# --- CARGADOR DE COGS ---
async def load_extensions():
    # Recorre la carpeta 'cogs'
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            # Carga el archivo (ej: cogs.bienvenida)
            await bot.load_extension(f'cogs.{filename[:-3]}')
            print(f'⚙️  Engranaje cargado: {filename}')

@bot.event
async def on_ready():
    print('-----------------------------------------------------')
    print(f'⚡ SISTEMA ONLINE: {bot.user.name}')
    print('-----------------------------------------------------')
    await bot.change_presence(activity=discord.Game(name="Vigilando Sector Omega"))

# --- EJECUCIÓN ---
async def main():
    if not TOKEN:
        print("❌ ERROR CRÍTICO: No se encontró DISCORD_TOKEN en .env")
        print("   Crea un archivo .env con: DISCORD_TOKEN=tu_token_aqui")
        return
    async with bot:
        await load_extensions()
        await bot.start(TOKEN)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        # Esto evita errores feos al cancelar con Ctrl+C
        pass