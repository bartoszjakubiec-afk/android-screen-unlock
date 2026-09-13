from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List


@dataclass
class Device:
    serial: str
    state: str


def adb_path() -> str | None:
    return shutil.which("adb")


def _run(args: List[str], timeout: int = 20) -> subprocess.CompletedProcess[str]:
    if not adb_path():
        raise RuntimeError("Nie znaleziono programu adb. Zainstaluj Android Platform Tools.")
    return subprocess.run(
        ["adb", *args],
        text=True,
        capture_output=True,
        timeout=timeout,
        check=False,
    )


def list_devices() -> list[Device]:
    result = _run(["devices"])
    devices: list[Device] = []
    for line in result.stdout.splitlines()[1:]:
        line = line.strip()
        if not line or "\t" not in line:
            continue
        serial, state = line.split("\t", 1)
        devices.append(Device(serial=serial.strip(), state=state.strip()))
    return devices


def require_authorized_device(serial: str | None = None) -> Device:
    devices = list_devices()
    authorized = [d for d in devices if d.state == "device"]
    if serial:
        for dev in authorized:
            if dev.serial == serial:
                return dev
        raise RuntimeError("Wybrane urządzenie nie jest autoryzowane w ADB.")
    if len(authorized) == 1:
        return authorized[0]
    if not authorized:
        raise RuntimeError("Brak autoryzowanego urządzenia ADB.")
    raise RuntimeError("Podłączono więcej niż jedno urządzenie. Wybierz numer seryjny.")


def shell_prop(prop: str, serial: str | None = None) -> str:
    dev = require_authorized_device(serial)
    result = _run(["-s", dev.serial, "shell", "getprop", prop])
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "Nie udało się odczytać danych urządzenia.")
    return result.stdout.strip()


def device_info(serial: str | None = None) -> dict[str, str]:
    dev = require_authorized_device(serial)
    return {
        "serial": dev.serial,
        "manufacturer": shell_prop("ro.product.manufacturer", dev.serial),
        "model": shell_prop("ro.product.model", dev.serial),
        "android": shell_prop("ro.build.version.release", dev.serial),
        "sdk": shell_prop("ro.build.version.sdk", dev.serial),
    }


def reboot(mode: str = "system", serial: str | None = None) -> None:
    dev = require_authorized_device(serial)
    args = ["-s", dev.serial, "reboot"]
    if mode in {"recovery", "bootloader"}:
        args.append(mode)
    elif mode != "system":
        raise ValueError("Dozwolone tryby: system, recovery, bootloader")
    result = _run(args)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "Restart nie powiódł się.")


def pull_path(remote_path: str, destination: Path, serial: str | None = None) -> None:
    dev = require_authorized_device(serial)
    destination = destination.expanduser().resolve()
    destination.mkdir(parents=True, exist_ok=True)
    result = _run(
        ["-s", dev.serial, "pull", remote_path, str(destination)],
        timeout=1800,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or f"Nie udało się skopiować {remote_path}.")


def backup_paths(
    destination: Path,
    remote_paths: Iterable[str] | None = None,
    serial: str | None = None,
) -> Path:
    destination = destination.expanduser().resolve()
    destination.mkdir(parents=True, exist_ok=True)
    paths = list(remote_paths or [
        "/sdcard/DCIM",
        "/sdcard/Pictures",
        "/sdcard/Movies",
        "/sdcard/Download",
        "/sdcard/Documents",
    ])
    errors: list[str] = []
    for remote in paths:
        try:
            pull_path(remote, destination, serial)
        except RuntimeError as exc:
            errors.append(f"{remote}: {exc}")
    if len(errors) == len(paths):
        raise RuntimeError("Nie udało się skopiować żadnego katalogu.\n" + "\n".join(errors))
    return destination


def backup_dcim(destination: Path, serial: str | None = None) -> Path:
    destination = destination.expanduser().resolve()
    pull_path("/sdcard/DCIM", destination, serial)
    return destination
