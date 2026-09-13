from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox
from tkinter.scrolledtext import ScrolledText

from .adb import adb_path, backup_paths, device_info, list_devices, reboot


class RecoveryApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Android Recovery Assistant")
        self.geometry("760x560")
        self.minsize(680, 500)

        title = tk.Label(self, text="Android Recovery Assistant", font=("Helvetica", 20, "bold"))
        title.pack(pady=(18, 4))
        subtitle = tk.Label(
            self,
            text="Diagnostyka i bezpieczne odzyskiwanie danych z własnego telefonu",
        )
        subtitle.pack(pady=(0, 14))

        buttons = tk.Frame(self)
        buttons.pack(fill="x", padx=18)

        tk.Button(buttons, text="Sprawdź telefon", width=18, command=self.check_phone).grid(row=0, column=0, padx=5, pady=5)
        tk.Button(buttons, text="Informacje", width=18, command=self.show_info).grid(row=0, column=1, padx=5, pady=5)
        tk.Button(buttons, text="Backup danych", width=18, command=self.backup_data).grid(row=0, column=2, padx=5, pady=5)

        tk.Button(buttons, text="Restart systemu", width=18, command=lambda: self.do_reboot("system")).grid(row=1, column=0, padx=5, pady=5)
        tk.Button(buttons, text="Recovery", width=18, command=lambda: self.do_reboot("recovery")).grid(row=1, column=1, padx=5, pady=5)
        tk.Button(buttons, text="Bootloader", width=18, command=lambda: self.do_reboot("bootloader")).grid(row=1, column=2, padx=5, pady=5)

        self.output = ScrolledText(self, height=20, wrap=tk.WORD)
        self.output.pack(fill="both", expand=True, padx=18, pady=16)

        warning = (
            "Ta aplikacja nie obchodzi PIN-u, hasła, wzoru ani FRP. "
            "Dane można kopiować tylko wtedy, gdy Android zezwala na dostęp i ADB jest autoryzowane."
        )
        tk.Label(self, text=warning, wraplength=700, justify="left").pack(padx=18, pady=(0, 14))
        self.log("Podłącz telefon kablem USB i kliknij „Sprawdź telefon”.")

    def log(self, text: str) -> None:
        self.output.insert(tk.END, text + "\n")
        self.output.see(tk.END)

    def check_phone(self) -> None:
        self.output.delete("1.0", tk.END)
        if not adb_path():
            self.log("ADB nie jest zainstalowane lub nie znajduje się w PATH.")
            self.log("Zainstaluj Android Platform Tools, a następnie uruchom aplikację ponownie.")
            return

        devices = list_devices()
        if not devices:
            self.log("Nie wykryto telefonu przez ADB.")
            self.log("Sprawdź kabel USB i tryb połączenia.")
            return

        for dev in devices:
            self.log(f"Urządzenie: {dev.serial} — status: {dev.state}")
            if dev.state == "device":
                self.log("✓ ADB jest autoryzowane. Możliwy jest bezpieczny backup dostępnych danych.")
            elif dev.state == "unauthorized":
                self.log("⚠ Telefon widzi komputer, ale ADB nie jest autoryzowane.")
                self.log("Bez odblokowania telefonu i zaakceptowania klucza ADB nie można skopiować danych przez ADB.")
            elif dev.state == "offline":
                self.log("⚠ Urządzenie jest offline. Odłącz i podłącz przewód ponownie.")

    def show_info(self) -> None:
        try:
            info = device_info()
            self.log(f"Producent: {info['manufacturer']}")
            self.log(f"Model: {info['model']}")
            self.log(f"Android: {info['android']} (SDK {info['sdk']})")
            self.log(f"Numer seryjny ADB: {info['serial']}")
        except Exception as exc:
            messagebox.showerror("Błąd", str(exc))

    def backup_data(self) -> None:
        destination = filedialog.askdirectory(title="Wybierz folder na kopię danych")
        if not destination:
            return
        try:
            self.log("Rozpoczynam kopiowanie dostępnych danych...")
            path = backup_paths(Path(destination))
            self.log(f"✓ Backup zakończony: {path}")
            messagebox.showinfo("Gotowe", f"Kopia danych została zapisana w:\n{path}")
        except Exception as exc:
            messagebox.showerror("Backup nie powiódł się", str(exc))

    def do_reboot(self, mode: str) -> None:
        try:
            reboot(mode)
            self.log(f"Wysłano polecenie restartu: {mode}")
        except Exception as exc:
            messagebox.showerror("Błąd", str(exc))


def main() -> None:
    app = RecoveryApp()
    app.mainloop()


if __name__ == "__main__":
    main()
