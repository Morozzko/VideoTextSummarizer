# 🎤 VideoTextSummarizer

> 📹 Извлечение текста из видео с YouTube и его суммаризация с помощью Whisper и Ollama.

![FastAPI](https://img.shields.io/badge/FastAPI-0.100.0-blue?style=for-the-badge&logo=fastapi)
![Python](https://img.shields.io/badge/Python-3.10-blue?style=for-the-badge&logo=python)
![Whisper](https://img.shields.io/badge/Whisper-OpenAI-green?style=for-the-badge)
![yt-dlp](https://img.shields.io/badge/yt--dlp-Youtube%20Downloader-red?style=for-the-badge)
![Ollama](https://img.shields.io/badge/Ollama-Local%20LLM-orange?style=for-the-badge)

## 🚀 Стек технологий
- **FastAPI** – REST API на Python 🚀
- **Whisper (OpenAI)** – Распознавание речи 🎙️
- **yt-dlp** – Загрузка видео с YouTube 🎥
- **Ollama (Llama3)** – Локальная суммаризация текста 🤖
- **FFmpeg** – Обработка аудио 🎼

## 📌 Установка и запуск
### 1️⃣ Установка зависимостей
```bash
pip install -r requirements.txt
```

### 2️⃣ Установка FFmpeg (если не установлен)
#### Ubuntu/Debian:
```bash
sudo apt install ffmpeg
```
#### macOS (через Homebrew):
```bash
brew install ffmpeg
```
#### Windows:
Скачивание с [официального сайта](https://ffmpeg.org/download.html) и добавление в `PATH`.

### 3️⃣ Установка Ollama
Скачивание и установка **Ollama** с [официального сайта](https://ollama.com).
Затем загрузка модели LLaMA 3:
```bash
ollama pull llama3
```

### 4️⃣ Запуск сервиса
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 5️⃣ Использование API
#### 🔹 Транскрипция видео
```bash
curl -X POST "http://localhost:8000/transcribe" -H "Content-Type: application/json" -d '{"url": "https://www.youtube.com/watch?v=XXXXXX"}'
```

#### 🔹 Суммаризация текста
```bash
curl -X POST "http://localhost:8000/summarize" -H "Content-Type: application/json" -d '{"text": "Ваш текст..."}'
```

## 📝 Лицензия
All Rights Reserved

