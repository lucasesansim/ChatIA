# ChatIÁ — v0.1.0

Asistente de escritorio de código abierto para preparar respuestas, transcribir
audios y enviar mensajes revisados mediante **WhatsApp Cloud API oficial**.

> Esta versión fue reconstruida desde cero. No es una recuperación del ZIP de la
> conversación anterior. Es un MVP manual; no recibe mensajes automáticamente.

## Qué incluye

- Interfaz en español para Windows y Ubuntu (Python + Tk).
- Generación de borradores mediante la API de OpenAI, con respuesta editable.
- Transcripción de un archivo mediante OpenAI o localmente con faster-whisper.
- Copiar respuestas sin conectar WhatsApp.
- Envío de texto por WhatsApp Cloud API, con revisión completa y confirmación.
- Credenciales en memoria o variables de entorno; sin historial persistente.
- Recetas para un instalador Windows .exe y un paquete Ubuntu .deb.

## Estado real

El programa requiere tus credenciales para utilizar OpenAI y Meta. No incluye
claves, sesiones de WhatsApp, historial de conversaciones ni cuentas preconectadas.
La aceptación de un mensaje por Meta no garantiza su entrega.
Las pruebas usan servicios simulados: todavía hay que validar el flujo completo
con una cuenta real, y compilar/verificar los instaladores en cada plataforma.

No incluye recepción por webhook, WhatsApp Web por QR, acceso al WhatsApp personal,
Notta, integración con skills de ChatGPT, respuestas automáticas ni instaladores
firmados. Una suscripción a ChatGPT no configura la API de OpenAI en esta app.

## Ejecutar desde código

Requiere Python 3.11 o superior. En Ubuntu instalá también Tk y venv:

```bash
sudo apt install python3 python3-tk python3-venv
python3 -m venv .venv
source .venv/bin/activate
python -m pip install .
python -m chatia
```

En Windows, instalá Python con Tcl/Tk y abrí PowerShell en la carpeta del proyecto:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install .
.\.venv\Scripts\python.exe -m chatia
```

En la pestaña **Configuración**, ingresá la clave de OpenAI y, para enviar por
WhatsApp, el token de Meta, Phone Number ID y versión de Graph API de tu aplicación.
Los modelos sugeridos se pueden cambiar si tu cuenta no tiene acceso.

Variables de entorno opcionales:

| Variable | Uso |
| --- | --- |
| OPENAI_API_KEY | Clave de OpenAI |
| OPENAI_MODEL | Modelo de borrador; por defecto gpt-4.1-mini |
| OPENAI_TRANSCRIBE_MODEL | Por defecto gpt-4o-mini-transcribe |
| WHATSAPP_TOKEN | Token de acceso de Meta |
| WHATSAPP_PHONE_NUMBER_ID | ID del número de la aplicación de Meta |
| WHATSAPP_GRAPH_VERSION | Versión vigente admitida por tu app, con formato vNN.0 |

No se carga un archivo .env automáticamente ni se guarda la configuración.
Para evitar que una clave quede en el historial de la terminal, ingresala en la
interfaz. No compartas capturas de la configuración ni publiques tus tokens.

## Usar ChatIÁ

1. Pegá el mensaje recibido o elegí un archivo de audio.
2. Elegí transcripción local u OpenAI. El uso de OpenAI requiere confirmar la carga.
3. Generá un borrador o escribí directamente la respuesta.
4. Editá y revisá el resultado.
5. Copialo o ingresá un destinatario con código de país, sin espacios.
6. Revisá el destinatario y el mensaje completo en el cuadro de confirmación.
7. Confirmá el envío. No hay reintentos automáticos.

Para WhatsApp necesitás configurar una app de Meta con Cloud API y sus permisos.
Los números de prueba pueden exigir destinatarios habilitados. El envío de texto
libre está sujeto a la ventana de atención y políticas de Meta; iniciar un contacto
fuera de esa ventana puede requerir plantillas, que esta versión no implementa.
Consultá la documentación oficial antes de enviar mensajes.

## Transcripción local

Desde el entorno virtual, en la carpeta del proyecto:

```bash
python -m pip install ".[local]"
```

La primera ejecución descarga el modelo público base de faster-whisper.
El audio se procesa en CPU, en tu equipo. Esta opción no necesita una clave de
OpenAI, pero generar un borrador sí usa OpenAI. El modelo queda en la caché del
sistema. El ejecutable básico no incluye faster-whisper: usá esta función desde
código con la opción local instalada.

Para OpenAI se admiten MP3, MP4, MPEG, MPGA, M4A, WAV y WEBM, hasta 24 MiB.
Un audio OGG/OPUS descargado de WhatsApp debe convertirse para esta ruta.
La ruta local admite los formatos que soporte el decodificador de faster-whisper.

## Compilar instaladores

Las recetas están en [docs/BUILD.md](docs/BUILD.md). Los ejecutables se generan en
dist/ y no se incluyen en Git. Cada plataforma debe compilarse en su propio SO.
Todavía no hay binarios de release ni firma de código.

## Desarrollo y verificación

```bash
python -m pip install -e .
python -m unittest discover -s tests -v
```

Las pruebas verifican payloads, destinatarios, límites, multipart, errores sin
filtrar tokens y ausencia de reintentos. No llaman APIs reales.
Ver [CONTRIBUTING.md](CONTRIBUTING.md) y [SECURITY.md](SECURITY.md).

Próximos pasos: pruebas con cuentas reales, instaladores firmados, recepción por
webhook con validación de firma y deduplicación, y evaluación de Notta.

## Documentación de los servicios

- [OpenAI Responses](https://platform.openai.com/docs/api-reference/responses)
- [OpenAI speech-to-text](https://developers.openai.com/api/docs/guides/speech-to-text)
- [WhatsApp Cloud API, colección oficial de Meta](https://www.postman.com/meta/whatsapp-business-platform/documentation/wlk6lh4/whatsapp-cloud-api)
- [faster-whisper](https://github.com/SYSTRAN/faster-whisper)

Licencia [MIT](LICENSE). Los servicios externos pueden tener cargos y sus propios términos.
