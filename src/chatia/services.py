"""Adapters: no credentials, audio or history are persisted."""
import json
import mimetypes
import re
import uuid
from pathlib import Path
from urllib import error, request


class ServiceError(Exception):
    """Safe user-facing error; never includes remote bodies or tokens."""


def post(url, token, body, content_type):
    if not token.strip():
        raise ServiceError("Falta la clave o el token del servicio.")
    req = request.Request(url, data=body, method="POST", headers={
        "Authorization": "Bearer " + token.strip(), "Content-Type": content_type})
    try:
        with request.urlopen(req, timeout=120) as response:
            result = json.load(response)
    except error.HTTPError as exc:
        status = exc.code
        exc.close()
        raise ServiceError(f"El servicio rechazó la solicitud (HTTP {status}). Revisá credenciales, modelo y permisos. No se reintentó.") from None
    except (error.URLError, TimeoutError, OSError):
        raise ServiceError("Falló la conexión. Si enviabas un mensaje, verificá su estado antes de volver a enviarlo.") from None
    except (ValueError, UnicodeError):
        raise ServiceError("Respuesta no válida. Verificá el estado antes de repetir un envío.") from None
    if not isinstance(result, dict):
        raise ServiceError("La respuesta del servicio no es válida.")
    return result


def post_json(url, token, payload):
    return post(url, token, json.dumps(payload).encode("utf-8"), "application/json")


def draft(text, key, model):
    if not text.strip() or not model.strip():
        raise ServiceError("Ingresá un mensaje y un modelo de OpenAI.")
    result = post_json("https://api.openai.com/v1/responses", key, {
        "model": model.strip(),
        "instructions": "Redactá una respuesta breve y clara en el idioma del mensaje. No inventes datos ni compromisos. Devolvé solo el borrador; una persona lo revisará antes de enviarlo.",
        "input": text.strip()})
    parts = [part["text"] for item in result.get("output", [])
             if item.get("type") == "message"
             for part in item.get("content", [])
             if part.get("type") == "output_text" and isinstance(part.get("text"), str)]
    answer = "\n".join(parts).strip()
    if not answer:
        raise ServiceError("El modelo no devolvió texto.")
    return answer


def transcribe_cloud(path, key, model):
    audio = Path(path)
    if audio.suffix.lower() not in {".mp3", ".mp4", ".mpeg", ".mpga", ".m4a", ".wav", ".webm"}:
        raise ServiceError("Convertí el audio a MP3, M4A, WAV o WEBM.")
    if not key.strip() or not model.strip():
        raise ServiceError("Ingresá la clave y el modelo de transcripción.")
    try:
        if audio.stat().st_size > 24 * 1024 * 1024:
            raise ServiceError("El audio debe ocupar como máximo 24 MiB.")
        data = audio.read_bytes()
    except OSError:
        raise ServiceError("No se pudo leer el audio.") from None
    if not data:
        raise ServiceError("El audio está vacío.")
    boundary = "chatia" + uuid.uuid4().hex
    mime = mimetypes.guess_type(audio.name)[0] or "application/octet-stream"
    fields = []
    for name, value in (("model", model.strip()), ("response_format", "json")):
        fields.append(f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"\r\n\r\n{value}\r\n'.encode())
    fields.append(f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="audio{audio.suffix.lower()}"\r\nContent-Type: {mime}\r\n\r\n'.encode())
    fields.extend((data, f"\r\n--{boundary}--\r\n".encode()))
    result = post("https://api.openai.com/v1/audio/transcriptions", key,
                  b"".join(fields), f"multipart/form-data; boundary={boundary}")
    text = result.get("text")
    if not isinstance(text, str) or not text.strip():
        raise ServiceError("No se detectó texto en el audio.")
    return text.strip()


def transcribe_local(path, model="base"):
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        raise ServiceError("Instalá la opción local: pip install '.[local]'.") from None
    try:
        engine = WhisperModel(model, device="cpu", compute_type="int8")
        segments, _ = engine.transcribe(path, vad_filter=True)
        text = " ".join(segment.text.strip() for segment in segments).strip()
    except Exception:
        raise ServiceError("No se pudo transcribir localmente. Revisá el archivo y la instalación de faster-whisper.") from None
    if not text:
        raise ServiceError("No se detectó voz.")
    return text


def send_whatsapp(text, recipient, token, phone_id, version):
    recipient = recipient.strip().removeprefix("+")
    phone_id, version = phone_id.strip(), version.strip()
    if not re.fullmatch(r"[1-9][0-9]{6,14}", recipient):
        raise ServiceError("El destinatario debe incluir código de país y solo dígitos, sin espacios.")
    if not re.fullmatch(r"[0-9]+", phone_id) or not re.fullmatch(r"v[0-9]+\.0", version):
        raise ServiceError("Revisá Phone Number ID y versión de Graph API (ejemplo: v23.0).")
    if not text.strip() or len(text) > 4096:
        raise ServiceError("El mensaje debe contener entre 1 y 4096 caracteres.")
    result = post_json(f"https://graph.facebook.com/{version}/{phone_id}/messages", token, {
        "messaging_product": "whatsapp", "to": recipient,
        "type": "text", "text": {"preview_url": False, "body": text}})
    messages = result.get("messages", [])
    if not messages or not isinstance(messages[0].get("id"), str):
        raise ServiceError("No se recibió un ID. Verificá en Meta antes de reintentar.")
    return messages[0]["id"]
