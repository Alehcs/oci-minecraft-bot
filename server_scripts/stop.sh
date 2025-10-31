#!/bin/bash
# Primero, verifica si el servidor está corriendo
if ! screen -list | grep -q "minecraft"; then
    echo "El servidor no está en ejecución."
    exit 1
fi

# Envía los comandos de apagado seguro
screen -S minecraft -p 0 -X stuff "say El servidor se apagará en 15 segundos...^M"
sleep 10
screen -S minecraft -p 0 -X stuff "say Apagando en 5...^M"
sleep 5
screen -S minecraft -p 0 -X stuff "stop^M"

# Espera a que el proceso termine
sleep 10
echo "Servidor detenido."