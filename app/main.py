from __future__ import annotations

from pathlib import Path

from .adb import adb_path, backup_dcim, device_info, list_devices, reboot


def print_header() -> None:
    print("\n=== Android Recovery Assistant ===")
    print("Narzędzie do diagnostyki własnego urządzenia przez autoryzowane ADB.\n")


def show_devices() -> None:
    devices = list_devices()
    if not devices:
        print("Brak urządzeń ADB.")
        return
    for dev in devices:
        print(f"- {dev.serial}: {dev.state}")


def show_info() -> None:
    info = device_info()
    print(f"Producent: {info['manufacturer']}")
    print(f"Model: {info['model']}")
    print(f"Android: {info['android']} (SDK {info['sdk']})")
    print(f"Numer seryjny ADB: {info['serial']}")


def main() -> None:
    print_header()
    if not adb_path():
        print("Nie znaleziono ADB. Zainstaluj Android Platform Tools i uruchom ponownie.")
        return

    while True:
        print("\n1. Pokaż urządzenia")
        print("2. Pokaż informacje o autoryzowanym urządzeniu")
        print("3. Skopiuj zdjęcia DCIM")
        print("4. Restart do recovery")
        print("5. Restart do bootloadera")
        print("6. Zwykły restart")
        print("0. Wyjście")
        choice = input("Wybierz opcję: ").strip()

        try:
            if choice == "1":
                show_devices()
            elif choice == "2":
                show_info()
            elif choice == "3":
                target = input("Folder docelowy [~/Android-Backup]: ").strip() or "~/Android-Backup"
                path = backup_dcim(Path(target))
                print(f"Kopia zakończona: {path}")
            elif choice == "4":
                reboot("recovery")
                print("Wysłano polecenie restartu do recovery.")
            elif choice == "5":
                reboot("bootloader")
                print("Wysłano polecenie restartu do bootloadera.")
            elif choice == "6":
                reboot("system")
                print("Wysłano polecenie restartu.")
            elif choice == "0":
                break
            else:
                print("Nieznana opcja.")
        except Exception as exc:
            print(f"Błąd: {exc}")


if __name__ == "__main__":
    main()
