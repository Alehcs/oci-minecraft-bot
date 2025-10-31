#!/bin/bash
echo "Reiniciando el servidor..."
# Llama al script de parada (usando la ruta absoluta por seguridad)
/home/minecraft/server/stop.sh
# Espera un poco para que se apague bien
sleep 5
# Llama al script de inicio (usando la ruta absoluta)
/home/minecraft/server/start.sh
echo "Reinicio completado."