# Instaladores

Recetas preparadas, pendientes de compilación y prueba en Windows y Ubuntu.
No equivalen a binarios firmados ni a releases verificadas.

## Windows: instalador .exe

Necesitás Python 3.11+ con Tk, un entorno virtual e
[Inno Setup 6](https://jrsoftware.org/isinfo.php).

En PowerShell, desde la raíz del proyecto:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install ".[build]"
.\.venv\Scripts\python.exe -m PyInstaller --noconfirm --clean --windowed --onedir --name ChatIA --paths src launcher.py
& "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" packaging\windows\ChatIA.iss
```

Resultado esperado: dist/ChatIA-0.1.0-Setup.exe. Instala para el usuario actual,
sin privilegios de administrador. No empaquetes claves ni archivos .env.
El paquete básico incluye Tk y los adaptadores de nube; no faster-whisper.
Windows puede mostrar advertencias por falta de firma digital.

## Ubuntu: paquete .deb

En Ubuntu con Python 3.11+, Tk y dpkg-deb:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install ".[build]"
bash packaging/ubuntu/build-deb.sh
sudo apt install ./dist/chatia_0.1.0_*.deb
```

Compilá en la versión más antigua de Ubuntu que pretendas soportar y verificá la
compatibilidad de glibc. El paquete se construye para la arquitectura del equipo.
La instalación se hace en /opt/chatia y agrega una entrada al menú de aplicaciones.
No incluye el motor local de transcripción.

## Lista de verificación de release

- Ejecutar tests y abrir la app en ambos sistemas.
- Probar generación y transcripción con cuentas propias y datos de prueba.
- Verificar cancelación, revisión y aceptación de un envío a un número de prueba.
- Probar instalación, inicio y desinstalación en equipos limpios.
- Revisar que no haya claves, archivos de audio ni conversaciones en el paquete.
- Publicar hashes SHA-256 y documentar arquitectura y versión de SO.
