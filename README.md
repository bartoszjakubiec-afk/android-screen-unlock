# Android Recovery Assistant

Bezpieczne narzędzie dla macOS do diagnostyki i obsługi **własnego** urządzenia Android przez oficjalne mechanizmy ADB.

## Co potrafi

- wykrywa telefon podłączony przez USB,
- pokazuje status ADB (`device`, `unauthorized`, `offline`),
- odczytuje producenta, model i wersję Androida,
- pozwala zrestartować **autoryzowane** urządzenie do systemu, recovery lub bootloadera,
- pozwala skopiować zdjęcia z katalogu `DCIM` z urządzenia, jeśli ADB ma legalny dostęp,
- prowadzi użytkownika krok po kroku przez diagnostykę połączenia.

## Czego nie robi

Projekt **nie obchodzi** PIN-u, hasła, wzoru, FRP ani innych zabezpieczeń Androida. Jeżeli ADB nie było wcześniej autoryzowane, aplikacja nie próbuje omijać tej ochrony.

## Wymagania

- macOS (także starsze wersje, o ile działa Python 3 i Android Platform Tools),
- Python 3.9+,
- `adb` z pakietu Android Platform Tools.

## Uruchomienie

W Terminalu:

```bash
python3 -m app.main
```

Możesz też uruchomić:

```bash
bash run.command
```

## Instalacja ADB na Macu

Jeżeli masz Homebrew:

```bash
brew install android-platform-tools
```

Następnie sprawdź:

```bash
adb version
adb devices
```

## Automatyzacja

Repozytorium zawiera GitHub Actions. Po każdym `push` GitHub automatycznie:

1. sprawdza składnię Pythona,
2. uruchamia testy,
3. tworzy paczkę ZIP projektu jako artefakt workflow.

## Bezpieczeństwo

Funkcje wymagające komunikacji z telefonem wykonują się wyłącznie wtedy, gdy `adb devices` pokazuje urządzenie jako `device`.
