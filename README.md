# SoundPad— Virtual Microphone Soundboard

SoundPad с горячими клавишами: подмешивает звуки к вашему микрофону в реальном времени.
Собеседник в Discord/Zoom/TeamSpeak слышит и вас, и звуки одновременно.

---

## Установка (один раз)

### 1. VB-Cable (виртуальный аудио кабель)
Скачайте и установите бесплатно:
👉 https://vb-audio.com/Cable/

После установки **перезагрузите компьютер**.

### 2. Python и зависимости

```bash
pip install -r requirements.txt
```

> Python 3.8+ обязателен. Скачать: https://python.org

---

## Запуск

```bash
python main.py
```

---

## Настройка

### Шаг 1 — Устройства (кнопка ⚙ УСТРОЙСТВА)

| Поле | Что выбрать |
|------|-------------|
| 🎤 Микрофон | Ваш реальный микрофон |
| 🔌 VB-Cable Input | `CABLE Input (VB-Audio Virtual Cable)` |
| 🎧 Мониторинг | Ваши наушники/колонки |

### Шаг 2 — Discord / Zoom
В настройках голосового приложения выберите микрофон:
`CABLE Output (VB-Audio Virtual Cable)`

> Важно: выбирайте **CABLE Output**, а не Input.
> — Input это "вход" куда пишет ваше приложение
> — Output это "выход" откуда читает Discord


---

## Форматы файлов

MP3, WAV, OGG, FLAC, AAC, M4A


