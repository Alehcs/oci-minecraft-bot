# ☁️ Minecraft Server - OCI Free Tier con Automatización en Discord

Este proyecto documenta la configuración de un servidor de Minecraft (PaperMC) optimizado para el nivel gratuito "Always Free" de Oracle Cloud Infrastructure (OCI). Incluye un bot de Discord para la gestión remota del servidor y un sistema de backup diario y automático a almacenamiento en la nube.

La arquitectura combina infraestructura gratuita de alto rendimiento con scripts de automatización para maximizar la disponibilidad y minimizar los costos de operación.

## ✨ Características del Proyecto

* **Infraestructura de Costo Cero:** Servidor corriendo en una máquina virtual **VM.Standard.A1.Flex (Ampere)** con 1 OCPU y 6 GB de RAM, elegible para la capa "Always Free" de OCI.
* **Gestión Remota por Discord:** Un bot en Python (utilizando la biblioteca `discord.py`) permite a los usuarios autorizados iniciar (`!startserver`), detener (`!stopserver`) y verificar el estado del servidor sin necesidad de acceder a la consola SSH.
* **Backups Automáticos y Gratuitos:**
    * Copia de seguridad diaria programada mediante **Cron**.
    * Utiliza la API de OCI para comprimir el mundo (`.tar.gz`) y subirlo a un **Bucket de Almacenamiento de Objetos** (gratuito) para una redundancia total.
* **Control de Acceso (RCON):** Se utiliza RCON (Remote Console) para una comunicación segura y eficiente entre el bot de Discord, los scripts de automatización y la consola del servidor de Minecraft.

## 🛠️ Stack Tecnológico

| Componente | Tecnología/Servicio | Uso Principal |
| :--- | :--- | :--- |
| **Cloud Computing** | Oracle Cloud Infrastructure (OCI) | Alojamiento de la VM (VM.Standard.A1.Flex). |
| **Sistema Operativo** | Ubuntu 22.04 LTS (ARM64) | Base del servidor. |
| **Servidor Minecraft**| PaperMC (Java 17+) | Servidor optimizado para mejor rendimiento. |
| **Gestión de Sesiones**| `screen` | Permite que el servidor se ejecute en segundo plano. |
| **Bot de Discord** | Python + `discord.py` | Automatización de comandos. |
| **Conexión Servidor** | `rcon-cli` | Comunicación segura entre los scripts y el servidor de Minecraft. |
| **Almacenamiento** | OCI Object Storage | Almacenamiento redundante de los Backups diarios. |
| **Automatización** | Cron | Programación del script de backup diario. |

## 🚀 Guía de Configuración Rápida

Esta sección es un resumen de los pasos cruciales para la configuración.

### 1. Configuración del Entorno OCI

1.  **Creación de la VCN:** Crear una Virtual Cloud Network (VCN) con subredes pública y privada.
2.  **Reglas de Seguridad (Ingress):** Asegurar que los siguientes puertos estén abiertos en la Lista de Seguridad de la VCN:
    * **Puerto 22 (SSH):** Para acceso a la terminal.
    * **Puerto 25565 (TCP):** Para que los jugadores se conecten al servidor de Minecraft.
    * **Puerto 25575 (RCON/TCP):** Para la comunicación interna de los scripts y el bot.
3.  **Creación de la Instancia:** Crear la instancia VM.Standard.A1.Flex con la imagen **Canonical Ubuntu 22.04** y las especificaciones **1 OCPU y 6 GB de RAM**.
4.  **Generación de Claves SSH:** Descargar el par de claves SSH (`.pub` y `.key`) para la conexión.
5.  **OCI API Key:** Generar una clave API en la consola de OCI y descargar el archivo de clave privada (`.pem`) para el acceso programático a Object Storage.

### 2. Configuración del Servidor y Scripts

1.  **Conexión SSH:** Conectarse a la VM usando la clave SSH.
2.  **Creación de Usuario:** Crear el usuario dedicado `minecraft`.
3.  **Instalación de Java y Dependencias:** Instalar Java 17, `rcon-cli`, y las herramientas de OCI CLI.
4.  **Configuración de Minecraft:** Instalar PaperMC, aceptar la EULA y configurar `server.properties`:
    ```properties
    enable-rcon=true
    rcon.port=25575
    rcon.password=TU_CONTRASEÑA_SEGURA
    ```
5.  **Scripts de Control (start.sh, stop.sh):** Asegurar que estos scripts utilicen el comando `screen` para gestionar la sesión del servidor en segundo plano.

### 3. Configuración del Backup Automático

1.  **Creación del Bucket OCI:** Crear un Bucket de Object Storage (ej: `minecraft-backups-ale`) para alojar los archivos de mundo.
2.  **Script de Backup (`backup.sh`):** Implementar la lógica para:
    a.  Enviar comando RCON `save-off` y `save-all`.
    b.  Comprimir la carpeta del mundo (`world`).
    c.  Subir el archivo `.tar.gz` al Bucket OCI usando el OCI CLI.
    d.  Enviar comando RCON `save-on`.
    **Nota:** Es crucial forzar el uso del puerto RCON correcto (`-P 25575`) en el script para evitar el error de puerto por defecto.
3.  **Programación (Cron):**
    ```bash
    sudo -iu minecraft crontab -e
    ```
    Añadir la línea de programación (ejemplo para 4:00 AM diario):
    ```cron
    0 4 * * * /home/minecraft/backups/backup.sh > /home/minecraft/backups/backup.log 2>&1
    ```

### 4. Configuración del Bot de Discord

1.  **Creación del Bot:** Registrar la aplicación en el Portal de Desarrolladores de Discord.
2.  **Permisos:** Configurar los permisos necesarios (especialmente **Send Messages**).
3.  **Archivo de Configuración (`.env`):** Almacenar el `DISCORD_TOKEN`, el ID del Canal y el Rol de Administrador.
4.  **Lógica del Bot (`bot.py`):** Implementar los comandos (`!startserver`, `!stopserver`) para ejecutar los scripts de control (`start.sh`, `stop.sh`) en la VM usando `subprocess` con el usuario `minecraft`.
5.  **Servicio Systemd:** Configurar el bot para ejecutarse como un servicio persistente.

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Consulta el archivo `LICENSE` para más detalles.

---
