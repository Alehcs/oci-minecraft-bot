#!/bin/bash

# Configuración RCON
RCON_IP="127.0.0.1"
RCON_PORT="25575"
RCON_PASS="micontrasenaunica"

echo "Deteniendo servidor de Minecraft de forma segura..."

# Aviso inicial
rcon-cli --host "$RCON_IP" --port "$RCON_PORT" --password "$RCON_PASS" say "El servidor se apagará en 15 segundos..."
sleep 10

# Segundo aviso
rcon-cli --host "$RCON_IP" --port "$RCON_PORT" --password "$RCON_PASS" say "Apagando en 5..."
sleep 5

# Comando de apagado
rcon-cli --host "$RCON_IP" --port "$RCON_PORT" --password "$RCON_PASS" stop

# Esperar a que el proceso termine
sleep 10
echo "✅ Servidor detenido correctamente."