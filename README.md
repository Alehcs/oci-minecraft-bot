# ☁️ Servidor de Minecraft OCI Free Tier con Bot de Discord v2.0 (systemd)

Este proyecto documenta la configuración de un servidor de Minecraft (PaperMC 1.21.10) optimizado para el nivel gratuito "Always Free" de Oracle Cloud Infrastructure (OCI).

La arquitectura final utiliza **systemd** para una gestión robusta del servidor y un bot de Discord para la automatización remota (`!startserver`, `!stopserver`), eliminando la fragilidad de los scripts de `screen`. También incluye backups diarios a OCI Object Storage y seguridad para modo no-premium.

## ✨ Características del Proyecto

* **Infraestructura de Costo Cero:** Servidor corriendo en la VM "Always Free" **VM.Standard.A1.Flex (Ampere)** al máximo de su capacidad (**4 OCPU** y **24 GB de RAM**).
* **Servidor No-Premium Seguro:** Configurado con `online-mode=false` y protegido contra suplantación de identidad usando el plugin **AuthMe Reloaded**.
* **Gestión Robusta con `systemd`:** El servidor de Minecraft se ejecuta como un servicio (`minecraft.service`), garantizando un arranque y parada estables.
* **Gestión Remota por Discord:** Un bot de Python (`discord.py`) controla el servicio `systemd` para iniciar (`!startserver`), detener (`!stopserver`) y reiniciar (`!restartserver`) el servidor.
* **Guardado Seguro (RCON):** El servicio `systemd` utiliza **RCON** para ejecutar un `save-all` y `stop` antes de apagar el servidor, asegurando que no se pierda progreso.
* **Backups Automáticos en la Nube:** Un script `cron` diario comprime el mundo, plugins y configuraciones, y los sube al **OCI Object Storage** (gratuito) usando el OCI CLI.

## 🛠️ Stack Tecnológico

| Componente | Tecnología/Servicio | Uso Principal |
| :--- | :--- | :--- |
| **Cloud Computing** | Oracle Cloud Infrastructure (OCI) | VM Ampere A1 (4 OCPU, 24 GB RAM). |
| **Sistema Operativo** | Ubuntu 22.04 LTS (ARM64) | Base del servidor. |
| **Servidor Minecraft**| **PaperMC 1.21.10** | Servidor optimizado (Requiere **Java 21**). |
| **Gestión de Servicio**| **systemd** | `minecraft.service` para un control robusto (reemplaza a `screen`). |
| **Bot de Discord** | Python + `discord.py` | Automatización de comandos `systemctl` vía `sudo`. |
| **Seguridad Login** | AuthMe Reloaded (Plugin) | Forza el login (`/login`) en modo no-premium. |
| **Conexión Servidor** | `rcon-cli` | Usado por `systemd` y `backup.sh` para `stop` y `save-all`. |
| **Almacenamiento** | OCI Object Storage | Backups diarios redundantes. |
| **Automatización** | Cron | Programación del script de backup. |

## 🚀 Guía de Configuración Rápida

### 1. Configuración del Entorno OCI

1.  **Creación de la VCN:** Crear una Virtual Cloud Network (VCN) con una subred pública.
2.  **Reglas de Seguridad (Ingress):** Abrir los puertos TCP en la Security List de la VCN:
    * **Puerto 22 (SSH):** Para acceso a la terminal.
    * **Puerto 25565 (Juego):** Para que los jugadores se conecten.
    * **Puerto 25575 (RCON):** Para el control del bot y `systemd`.
3.  **Creación de la Instancia:** Crear la instancia `VM.Standard.A1.Flex` (Ubuntu 22.04) con **4 OCPU** y **24 GB de RAM**.

### 2. Configuración del Servidor y `systemd`

1.  **Instalación de Java 21:**
    * `sudo apt install openjdk-21-jre-headless -y`
    * `sudo update-alternatives --set java /usr/lib/jvm/java-21-openjdk-arm64/bin/java`
2.  **Instalación de Dependencias:** Instalar `rcon-cli` (vía `npm`) y `oci-cli` (vía `pip3`).
3.  **Configuración de Minecraft:**
    * Instalar PaperMC 1.21.10 (`paper.jar`) en `/home/minecraft/server`.
    * Instalar `AuthMe.jar` en la carpeta `plugins`.
    * Editar `server.properties` y configurar:
        ```properties
        online-mode=false
        enable-rcon=true
        rcon.port=25575
        rcon.password=TU_CONTRASEÑA_SEGURA
        ```
4.  **Crear el Servicio `minecraft.service`:**
    * Crear el archivo: `sudo nano /etc/systemd/system/minecraft.service`
    * Añadir el comando `ExecStart=` (con el comando `java` largo) y el `ExecStop=` (con el comando `rcon-cli` para `stop`).

### 3. Configuración del Bot de Discord

1.  **Crear Usuarios:** Crear usuarios `minecraft` y `discordbot`.
2.  **Configurar `visudo`:** Dar permisos al `discordbot` para controlar `systemd`:
    ```
    discordbot ALL=(ALL) NOPASSWD: /usr/bin/systemctl start minecraft.service, /usr/bin/systemctl stop minecraft.service
    ```
3.  **Configurar Bot (`bot.py`):**
    * El bot usa `asyncio.create_subprocess_exec` para llamar a `sudo systemctl start/stop minecraft.service`.
    * El bot **no** usa `start.sh` ni `screen`.
4.  **Configurar `.env`:** Añadir `DISCORD_TOKEN`, `ALLOWED_CHANNEL_ID`, `SERVER_IP` y `RCON_PASS`.
5.  **Servicio `discord-bot.service`:** Crear el servicio `systemd` para que el bot corra 24/7.

### 4. Configuración del Backup Automático

1.  **Crear el Bucket OCI** (ej. `minecraft-backups-ale`).
2.  **Configurar OCI CLI** (`oci setup config`).
3.  **Script de Backup (`backup.sh`):**
    * El script usa `rcon-cli` para `save-off` y `save-all`.
    * **Nota:** Asegurarse de usar los flags largos: `--host`, `--port`, y `--password`.
    * Comprime (`tar`) y sube (`oci os object put`) al bucket.
4.  **Programación (Cron):**
    * `sudo -iu minecraft crontab -e`
    * `0 4 * * * /home/minecraft/backups/backup.sh > /home/minecraft/backups/backup.log 2>&1`

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Consulta el archivo `LICENSE` para más detalles.
