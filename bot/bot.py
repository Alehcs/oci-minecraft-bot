import discord
from discord.ext import commands
import os
import asyncio
from dotenv import load_dotenv
from pathlib import Path

# --- Configuración ---
# Cargar .env desde la misma carpeta que bot.py
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)
TOKEN = os.getenv('DISCORD_TOKEN')
if not TOKEN:
    raise ValueError("❌ CRÍTICO: DISCORD_TOKEN no está definido en bot/.env")

# (Haz clic derecho en tu canal en Discord -> "Copiar ID")
ALLOWED_CHANNEL_ID = 1433902638461878354  # ID del canal donde escuchará el bot

SERVER_IP = "159.112.131.174" # La IP de tu servidor

intents = discord.Intents.default()
intents.message_content = True # Necesario para leer "!startserver"

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Bot conectado como {bot.user}')
    await bot.change_presence(activity=discord.Game(name="Servidor: Offline"))

# --- Comando Start ----
@bot.command(name='startserver')
async def start_server(ctx):
    if ctx.channel.id != ALLOWED_CHANNEL_ID: # Solo en el canal permitido
        return

    await ctx.send('✅ Recibido. Iniciando el servidor de Minecraft... Esto puede tardar un minuto.')
    await bot.change_presence(activity=discord.Game(name="Servidor: Iniciando..."))
    
    try:
        # Ejecuta el script start.sh COMO el usuario 'minecraft' de forma asíncrona con desacoplamiento
        # Usa DEVNULL para no bloquear el bot, asumiendo que el arranque será exitoso
        command = ['sudo', '-u', 'minecraft', '/home/minecraft/server/start.sh']
        process = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL
        )
        
        
        # El servidor se queda corriendo en background
        await asyncio.sleep(45)  # Dar tiempo suficiente al servidor para que arranque
        
        await ctx.send(f'🚀 ¡Servidor iniciado! Ya pueden conectarse a: `{SERVER_IP}`')
        await bot.change_presence(activity=discord.Game(name=f"Servidor: ONLINE ({SERVER_IP})"))

    except Exception as e:
        await ctx.send(f'❌ **Error inesperado:**\n`{e}`')
        await bot.change_presence(activity=discord.Game(name="Servidor: Error"))

# --- Comando Stop ----
@bot.command(name='stopserver')
async def stop_server(ctx):
    if ctx.channel.id != ALLOWED_CHANNEL_ID:
        return

    await ctx.send('🛑 Recibido. Guardando el mundo y deteniendo el servidor...')
    await bot.change_presence(activity=discord.Game(name="Servidor: Apagando..."))
    
    try:
        # Ejecuta el script stop.sh COMO el usuario 'minecraft' de forma asíncrona
        command = ['sudo', '-u', 'minecraft', '/home/minecraft/server/stop.sh']
        process = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            error_msg = stderr.decode() if stderr else "Error desconocido"
            await ctx.send(f'❌ **Error al detener el servidor:**\n`{error_msg}`')
            await bot.change_presence(activity=discord.Game(name="Servidor: Error"))
            return
        
        output = stdout.decode() if stdout else "Servidor detenido correctamente"
        await ctx.send(f'✅ Servidor detenido de forma segura.\n`{output}`')
        await bot.change_presence(activity=discord.Game(name="Servidor: Offline"))

    except Exception as e:
        await ctx.send(f'❌ **Error inesperado:**\n`{e}`')
        await bot.change_presence(activity=discord.Game(name="Servidor: Error"))

# --- Comando Restart ----
@bot.command(name='restartserver')
async def restart_server(ctx):
    if ctx.channel.id != ALLOWED_CHANNEL_ID:
        return

    await ctx.send('🔄 Recibido. Reiniciando el servidor de Minecraft...')
    await bot.change_presence(activity=discord.Game(name="Servidor: Reiniciando..."))
    
    try:
        # Ejecuta el script restart.sh COMO el usuario 'minecraft' de forma asíncrona
        command = ['sudo', '-u', 'minecraft', '/home/minecraft/server/restart.sh']
        process = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            error_msg = stderr.decode() if stderr else "Error desconocido"
            await ctx.send(f'❌ **Error al reiniciar el servidor:**\n`{error_msg}`')
            await bot.change_presence(activity=discord.Game(name="Servidor: Error"))
            return
        
        await asyncio.sleep(50)  # Dar tiempo para que el servidor reinicie
        await ctx.send(f'🔄 ¡Servidor reiniciado! Ya pueden conectarse a: `{SERVER_IP}`')
        await bot.change_presence(activity=discord.Game(name=f"Servidor: ONLINE ({SERVER_IP})"))

    except Exception as e:
        await ctx.send(f'❌ **Error inesperado:**\n`{e}`')
        await bot.change_presence(activity=discord.Game(name="Servidor: Error"))

# Manejo de errores
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        pass # Ignorar comandos no encontrados
    else:
        print(f"Error: {error}")
        await ctx.send(f'Ha ocurrido un error inesperado: {error}')

bot.run(TOKEN)