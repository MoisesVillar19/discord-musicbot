"""Panel local del bot (Sprint 5, D-05). tkinter + ttk, cero dependencias.

Arranca/detiene el bot como subproceso, edita alters (máx 5 por comando,
canónicos protegidos) y .env, y muestra el log. v1: un solo bot local
(perfiles múltiples queda como mejora futura).
"""
import os
import subprocess
import sys
import tkinter as tk
from tkinter import messagebox, ttk

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from core.aliases import (  # noqa: E402
    ALIASES_EXAMPLE,
    ALIASES_FILE,
    CANONICAL_COMMANDS,
    MAX_ALIASES,
    AliasError,
    load_aliases,
    save_aliases,
)

LOG_FILE = os.path.join(ROOT, "logs", "bot.log")
VENV_PYTHON = os.path.join(ROOT, "venv", "Scripts", "python.exe")
ENV_KEYS = ("DISCORD_TOKEN", "BOT_NAME", "GUILD_ID")

BG, BG2, FG, ACCENT = "#1e1e1e", "#2d2d2d", "#e0e0e0", "#4caf50"


class Panel(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("MusicBot — Panel local")
        self.geometry("720x560")
        self.proc = None
        self._style()
        self._build()
        self._tick()

    def _style(self):
        self.configure(bg=BG)
        s = ttk.Style(self)
        try:
            s.theme_use("clam")
        except tk.TclError:
            pass
        s.configure(".", background=BG, foreground=FG, fieldbackground=BG2,
                    font=("Segoe UI", 10))
        s.configure("TNotebook", background=BG, borderwidth=0)
        s.configure("TNotebook.Tab", background=BG2, foreground=FG, padding=(12, 6))
        s.configure("TFrame", background=BG)
        s.configure("TLabel", background=BG, foreground=FG)
        s.configure("TButton", background=BG2, foreground=FG, padding=6)
        s.configure("TEntry", fieldbackground=BG2, foreground=FG)

    def _build(self):
        top = ttk.Frame(self, padding=10)
        top.pack(fill="x")
        self.status = ttk.Label(top, text="● Offline", foreground="#f44336",
                                font=("Segoe UI", 12, "bold"))
        self.status.pack(side="left")
        for label, cmd in (("▶ Iniciar", self.start_bot),
                           ("⏹ Detener", self.stop_bot),
                           ("↻ Reiniciar", self.restart_bot)):
            ttk.Button(top, text=label, command=cmd).pack(side="right", padx=4)

        tabs = ttk.Notebook(self)
        tabs.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.log_box = tk.Text(tabs, bg="#111", fg="#cfc", font=("Consolas", 9),
                               state="disabled")
        tabs.add(self.log_box, text="📋 Logs")

        alias_frame = ttk.Frame(tabs, padding=10)
        tabs.add(alias_frame, text="🎭 Alters")
        ttk.Label(alias_frame,
                  text=f"Máx {MAX_ALIASES} por comando. Los nombres base no se tocan. "
                       "Guardar + reiniciar para aplicar.").pack(anchor="w", pady=(0, 8))
        self.alias_vars = {}
        for cmd in CANONICAL_COMMANDS:
            row = ttk.Frame(alias_frame)
            row.pack(fill="x", pady=2)
            ttk.Label(row, text=f"/{cmd}", width=14).pack(side="left")
            self.alias_vars[cmd] = tk.StringVar()
            ttk.Entry(row, textvariable=self.alias_vars[cmd]).pack(
                side="left", fill="x", expand=True, padx=6)
        btns = ttk.Frame(alias_frame)
        btns.pack(fill="x", pady=8)
        ttk.Button(btns, text="💾 Guardar alters", command=self.save_aliases_ui).pack(side="left")
        ttk.Button(btns, text="↺ Recargar", command=self.load_aliases_ui).pack(side="left", padx=6)
        ttk.Label(alias_frame, text="Separa con comas. Vacío = sin alters.",
                  font=("Segoe UI", 9)).pack(anchor="w")

        cfg_frame = ttk.Frame(tabs, padding=10)
        tabs.add(cfg_frame, text="⚙️ Config")
        self.cfg_vars = {}
        for key in ENV_KEYS:
            row = ttk.Frame(cfg_frame)
            row.pack(fill="x", pady=4)
            ttk.Label(row, text=key, width=16).pack(side="left")
            show = "" if key != "DISCORD_TOKEN" else "*"
            self.cfg_vars[key] = tk.StringVar()
            ttk.Entry(row, textvariable=self.cfg_vars[key], show=show).pack(
                side="left", fill="x", expand=True)
        ttk.Button(cfg_frame, text="💾 Guardar config",
                   command=self.save_config_ui).pack(anchor="w", pady=8)
        ttk.Label(cfg_frame, text="Cambios de config y alters requieren reiniciar el bot.",
                  font=("Segoe UI", 9)).pack(anchor="w")

        self.load_aliases_ui()
        self.load_config_ui()

    # ---- bot ----
    def start_bot(self):
        if self.proc and self.proc.poll() is None:
            return
        py = VENV_PYTHON if os.path.isfile(VENV_PYTHON) else sys.executable
        try:
            self.proc = subprocess.Popen(
                [py, os.path.join(ROOT, "bot.py")], cwd=ROOT,
                stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        except OSError as e:
            messagebox.showerror("Error", f"No se pudo arrancar:\n{e}")

    def stop_bot(self):
        if self.proc and self.proc.poll() is None:
            self.proc.terminate()

    def restart_bot(self):
        self.stop_bot()
        self.after(800, self.start_bot)

    def _tick(self):
        running = self.proc is not None and self.proc.poll() is None
        self.status.config(text="● Online" if running else "● Offline",
                           foreground=ACCENT if running else "#f44336")
        self._refresh_log()
        self.after(2000, self._tick)

    def _refresh_log(self):
        try:
            with open(LOG_FILE, encoding="utf-8") as f:
                lines = f.readlines()[-80:]
        except OSError:
            lines = ["(sin logs todavía: inicia el bot)\n"]
        self.log_box.config(state="normal")
        self.log_box.delete("1.0", "end")
        self.log_box.insert("end", "".join(lines))
        self.log_box.see("end")
        self.log_box.config(state="disabled")

    # ---- alters ----
    def load_aliases_ui(self):
        try:
            data = load_aliases(os.path.join(ROOT, ALIASES_FILE))
        except AliasError as e:
            messagebox.showerror("aliases.json inválido", str(e))
            return
        for cmd, var in self.alias_vars.items():
            var.set(", ".join(data.get(cmd, [])))

    def save_aliases_ui(self):
        data = {cmd: [a for a in (var.get().split(",")) if a.strip()]
                for cmd, var in self.alias_vars.items()}
        try:
            save_aliases(data, os.path.join(ROOT, ALIASES_FILE))
        except AliasError as e:
            messagebox.showerror("Error", str(e))
            return
        messagebox.showinfo("OK", "Alters guardados. Reinicia el bot para aplicar.")

    # ---- config ----
    def _env_path(self):
        return os.path.join(ROOT, ".env")

    def load_config_ui(self):
        values = {}
        try:
            with open(self._env_path(), encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        values[k.strip()] = v.strip()
        except OSError:
            pass
        for key, var in self.cfg_vars.items():
            var.set(values.get(key, ""))

    def save_config_ui(self):
        path = self._env_path()
        lines, seen = [], set()
        try:
            with open(path, encoding="utf-8") as f:
                old = f.readlines()
        except OSError:
            old = []
        with open(path, "w", encoding="utf-8") as f:
            for line in old:
                s = line.strip()
                if s and not s.startswith("#") and "=" in s:
                    k = s.split("=", 1)[0].strip()
                    if k in self.cfg_vars:
                        f.write(f"{k}={self.cfg_vars[k].get().strip()}\n")
                        seen.add(k)
                        continue
                f.write(line)
            for key, var in self.cfg_vars.items():
                if key not in seen:
                    f.write(f"{key}={var.get().strip()}\n")
        messagebox.showinfo("OK", ".env guardado. Reinicia el bot para aplicar.")


if __name__ == "__main__":
    if not os.path.isfile(os.path.join(ROOT, ALIASES_EXAMPLE)):
        print("aviso: falta aliases.example.json")
    Panel().mainloop()
