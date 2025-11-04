import discord
from discord.ext import commands
import os
import asyncio
from dotenv import load_dotenv
from pathlib import Path

# --- CONFIGURACIÓN E INICIALIZACIÓN ---

env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

TOKEN = os.getenv('DISCORD_TOKEN')
ALLOWED_CHANNEL_ID = os.getenv('ALLOWED_CHANNEL_ID')
SERVER_IP = os.getenv('SERVER_IP')

# Verifica que las variables existan
if not all([TOKEN, ALLOWED_CHANNEL_ID, SERVER_IP]):
    print("--- ERRORES CRÍTICOS EN .env ---")
    if not TOKEN: print("DISCORD_TOKEN no encontrado.")
    if not ALLOWED_CHANNEL_ID: print("ALLOWED_CHANNEL_ID no encontrado.")
    if not SERVER_IP: print("SERVER_IP no encontrado.")
    print("---------------------------------")
    exit() # No arranca si faltan variables

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# --- EVENTOS ---
@bot.event
async def on_ready():
    print(f'Bot (v2.0) conectado como {bot.user}')
    await bot.change_presence(activity=discord.Game(name="Servidor: Offline"))

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        pass
    else:
        print(f"Error: {error}")
        await ctx.send(f'Ha ocurrido un error inesperado: {error}')

# --- COMANDOS ---

@bot.command(name='startserver')
async def start_server(ctx):
    if ctx.channel.id != int(ALLOWED_CHANNEL_ID): return

    await ctx.send("✅ Recibido. Iniciando servicio `minecraft.service`...")
    
    # Llama a systemctl para iniciar el servidor
    process = await asyncio.create_subprocess_exec(
        '/usr/bin/sudo', '/usr/bin/systemctl', 'start', 'minecraft.service',
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()

    if process.returncode == 0:
        await asyncio.sleep(45) # Espera a que Java cargue
        await ctx.send(f'🚀 Servidor iniciado! Ya pueden conectarse a: {SERVER_IP}')
        await bot.change_presence(activity=discord.Game(name=f"Servidor: ONLINE ({SERVER_IP})"))
    else:
        await ctx.send(f'❌ Error al iniciar el servicio: {stderr.decode()}')

@bot.command(name='stopserver')
async def stop_server(ctx):
    if ctx.channel.id != int(ALLOWED_CHANNEL_ID): return

    await ctx.send('🛑 Recibido. Deteniendo servicio `minecraft.service` (guardando)...')
    
    # Llama a systemctl para detener (systemd ejecutará el RCON)
    process = await asyncio.create_subprocess_exec(
        '/usr/bin/sudo', '/usr/bin/systemctl', 'stop', 'minecraft.service',
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    
    if process.returncode == 0:
        await ctx.send(f'✅ Servidor detenido y guardado.')
        await bot.change_presence(activity=discord.Game(name="Servidor: Offline"))
    else:
        await ctx.send(f'❌ Error al detener el servicio: {stderr.decode()}')

# --- EJECUCIÓN ---
bot.run(TOKEN)