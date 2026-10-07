"""Desktop UI; all widget access stays on the main thread."""
import os
import queue
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter.scrolledtext import ScrolledText
from . import __version__, services


class App:
    def __init__(self, root):
        self.root, self.events, self.buttons = root, queue.Queue(), []
        root.title(f"ChatIÁ {__version__}")
        root.geometry("840x820")
        root.minsize(700, 700)
        frame = ttk.Frame(root, padding=16)
        frame.pack(fill="both", expand=True)
        ttk.Label(frame, text="ChatIÁ · respuestas que vos revisás", font=("Segoe UI", 18, "bold")).pack(anchor="w")
        ttk.Label(frame, text="Texto y audio → borrador → revisión → envío por WhatsApp Cloud API").pack(anchor="w", pady=(4, 12))
        notebook = ttk.Notebook(frame)
        notebook.pack(fill="both", expand=True)
        compose, settings = ttk.Frame(notebook, padding=12), ttk.Frame(notebook, padding=12)
        notebook.add(compose, text="Mensaje")
        notebook.add(settings, text="Configuración")
        self.values = {}
        fields = [
            ("OPENAI_API_KEY", "Clave de OpenAI", "", True),
            ("OPENAI_MODEL", "Modelo de respuesta", "gpt-4.1-mini", False),
            ("OPENAI_TRANSCRIBE_MODEL", "Modelo de transcripción en OpenAI", "gpt-4o-mini-transcribe", False),
            ("WHATSAPP_TOKEN", "Token de WhatsApp Cloud API", "", True),
            ("WHATSAPP_PHONE_NUMBER_ID", "Phone Number ID de Meta", "", False),
            ("WHATSAPP_GRAPH_VERSION", "Versión de Graph API (según tu app de Meta)", "", False)]
        for env, label, default, secret in fields:
            ttk.Label(settings, text=label).pack(anchor="w", pady=(8, 2))
            value = tk.StringVar(value=os.environ.get(env, default))
            self.values[env] = value
            ttk.Entry(settings, textvariable=value, show="•" if secret else "").pack(fill="x")
        ttk.Label(settings, text="Las credenciales quedan en memoria y no se guardan en archivos.\nTambién podés proporcionarlas mediante variables de entorno.\n\nOpenAI recibe el texto o audio cuando elegís sus funciones.\nLa opción local procesa el audio en tu equipo y descarga el modelo la primera vez.\nNotta y recepción automática: pendientes para otra versión.", wraplength=650).pack(anchor="w", pady=18)
        ttk.Label(compose, text="Mensaje recibido o transcripción").pack(anchor="w")
        self.source = ScrolledText(compose, height=8, wrap="word")
        self.source.pack(fill="both", expand=True, pady=5)
        row = ttk.Frame(compose)
        row.pack(fill="x", pady=5)
        self.button(row, "Transcribir con OpenAI", lambda: self.audio(False))
        self.button(row, "Transcribir localmente", lambda: self.audio(True))
        self.button(row, "Generar borrador", self.generate)
        ttk.Label(compose, text="Respuesta editable (revisala antes de enviarla)").pack(anchor="w", pady=(12, 0))
        self.answer = ScrolledText(compose, height=8, wrap="word")
        self.answer.pack(fill="both", expand=True, pady=5)
        ttk.Label(compose, text="Destinatario: código de país y número, sin espacios").pack(anchor="w", pady=(10, 3))
        self.recipient = tk.StringVar()
        ttk.Entry(compose, textvariable=self.recipient).pack(fill="x")
        row = ttk.Frame(compose)
        row.pack(fill="x", pady=10)
        self.button(row, "Copiar respuesta", self.copy)
        self.button(row, "Revisar y enviar por WhatsApp", self.send)
        self.status = tk.StringVar(value="Listo. No se envían mensajes automáticamente.")
        ttk.Label(frame, textvariable=self.status, wraplength=760).pack(anchor="w", pady=(12, 0))
        root.after(100, self.poll)

    def button(self, parent, text, command):
        button = ttk.Button(parent, text=text, command=command)
        button.pack(side="left", padx=(0, 8))
        self.buttons.append(button)

    def start(self, action, done, status):
        for button in self.buttons:
            button.state(["disabled"])
        self.status.set(status)
        def worker():
            try:
                self.events.put((done, action(), None))
            except services.ServiceError as exc:
                self.events.put((done, None, str(exc)))
            except Exception:
                self.events.put((done, None, "Ocurrió un error inesperado. Verificá el estado antes de repetir un envío."))
        threading.Thread(target=worker, daemon=True).start()

    def poll(self):
        try:
            done, result, problem = self.events.get_nowait()
        except queue.Empty:
            pass
        else:
            for button in self.buttons:
                button.state(["!disabled"])
            if problem:
                self.status.set(problem)
                messagebox.showerror("ChatIÁ", problem, parent=self.root)
            else:
                done(result)
        self.root.after(100, self.poll)

    def replace(self, widget, text):
        widget.delete("1.0", "end")
        widget.insert("1.0", text)
        self.status.set("Listo. Revisá el texto.")

    def generate(self):
        text = self.source.get("1.0", "end-1c")
        key, model = self.values["OPENAI_API_KEY"].get(), self.values["OPENAI_MODEL"].get()
        if not messagebox.askyesno("Enviar texto a OpenAI", "Se enviará el texto ingresado a OpenAI para generar un borrador. ¿Continuar?", parent=self.root):
            return
        self.start(lambda: services.draft(text, key, model), lambda result: self.replace(self.answer, result), "Generando borrador…")

    def audio(self, local):
        path = filedialog.askopenfilename(title="Elegí un audio", parent=self.root)
        if not path:
            return
        if local:
            action = lambda: services.transcribe_local(path)
        else:
            if not messagebox.askyesno("Enviar audio a OpenAI", "Se enviará el archivo de audio a OpenAI para transcribirlo. ¿Continuar?", parent=self.root):
                return
            key, model = self.values["OPENAI_API_KEY"].get(), self.values["OPENAI_TRANSCRIBE_MODEL"].get()
            action = lambda: services.transcribe_cloud(path, key, model)
        self.start(action, lambda result: self.replace(self.source, result), "Transcribiendo… La primera carga local puede tardar.")

    def copy(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.answer.get("1.0", "end-1c"))
        self.status.set("Respuesta copiada al portapapeles.")

    def send(self):
        text, recipient = self.answer.get("1.0", "end-1c"), self.recipient.get()
        token = self.values["WHATSAPP_TOKEN"].get()
        phone_id = self.values["WHATSAPP_PHONE_NUMBER_ID"].get()
        version = self.values["WHATSAPP_GRAPH_VERSION"].get()
        if not text.strip():
            messagebox.showerror("ChatIÁ", "La respuesta está vacía.", parent=self.root)
            return
        dialog = tk.Toplevel(self.root)
        dialog.title("Confirmar envío")
        dialog.geometry("620x500")
        dialog.transient(self.root)
        dialog.grab_set()
        ttk.Label(dialog, text=f"Destinatario: {recipient}", padding=10).pack(anchor="w")
        review = ScrolledText(dialog, wrap="word")
        review.pack(fill="both", expand=True, padx=10)
        review.insert("1.0", text)
        review.configure(state="disabled")
        def confirm():
            dialog.destroy()
            self.start(lambda: services.send_whatsapp(text, recipient, token, phone_id, version),
                       lambda ident: self.status.set("Aceptado por Meta (no confirma entrega). ID: " + ident), "Enviando una vez…")
        ttk.Button(dialog, text="Enviar este mensaje", command=confirm).pack(side="right", padx=10, pady=10)
        ttk.Button(dialog, text="Cancelar", command=dialog.destroy).pack(side="right", pady=10)


def main():
    root = tk.Tk()
    App(root)
    root.mainloop()
