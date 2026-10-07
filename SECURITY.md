# Seguridad y privacidad

La v0.1.0 es experimental. Las claves ingresadas permanecen en memoria; ChatIÁ no
escribe credenciales ni conversaciones en disco. Los modelos locales sí usan
la caché de faster-whisper. El portapapeles y los proveedores externos están fuera
del control de la aplicación. Cerrá ChatIÁ al terminar en un equipo compartido.

El texto y el audio se envían a OpenAI solo tras confirmar la acción correspondiente.
Meta recibe destinatario y respuesta cuando confirmás el envío. No se registran
cuerpos de error del proveedor, para evitar exponer tokens o contenido privado.
Un timeout de envío deja un estado incierto: verificá en Meta antes de repetirlo.

No publiques secretos en issues. Si encontrás una vulnerabilidad, usá el reporte
privado de GitHub si está habilitado o contactá al responsable por un canal privado.
Si una clave se expuso, revocala en el proveedor y reemplazala.
