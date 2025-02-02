from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
import tempfile
import os
import yt_dlp
import whisper
import requests

# Константы
WHISPER_MODEL = "base"
OLLAMA_MODEL = "deepseek-r1:70b"
OLLAMA_API_URL = "http://localhost:11434/api/generate"

app = FastAPI()

# Загружаем модель Whisper один раз при старте приложения
model = whisper.load_model(WHISPER_MODEL)

# Проверка доступности Ollama при запуске
@app.on_event("startup")
async def startup_event():
    test_prompt = "Привет! Как дела?"
    try:
        print("Тестирование подключения к Ollama...")
        response = requests.post(
            OLLAMA_API_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": test_prompt,
                "stream": False
            },
            timeout=30
        )
        if response.status_code == 200:
            print("Ollama успешно отвечает")
        else:
            print(f"Предупреждение: Ollama вернула статус {response.status_code}")
    except Exception as e:
        print(f"Предупреждение: Не удалось подключиться к Ollama: {str(e)}")

def download_and_transcribe(url: str) -> str:
    """Скачивает видео и извлекает текст"""
    with tempfile.TemporaryDirectory() as tmpdirname:
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": os.path.join(tmpdirname, "temp.%(ext)s"),
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }],
            "quiet": True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        audio_file = os.path.join(tmpdirname, "temp.mp3")
        if not os.path.exists(audio_file):
            files = os.listdir(tmpdirname)
            if len(files) == 0:
                raise Exception("Не удалось скачать аудиофайл")
            audio_file = os.path.join(tmpdirname, files[0])
        
        result = model.transcribe(audio_file)
        return result.get("text", "")

def summarize_text(text: str) -> str:
    """Отправляет текст в Ollama для суммаризации"""
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": f"Создай краткое и четкое резюме следующего текста на русском языке (не на английском):\n{text}",
        "stream": False
    }
    try:
        response = requests.post(OLLAMA_API_URL, json=payload, timeout=600)
        response.raise_for_status()
        return response.json().get("response", "")
    except Exception as e:
        print(f"Ошибка при обращении к Ollama: {str(e)}")
        raise

@app.get("/", response_class=HTMLResponse)
def read_form():
    return """
    <html>
        <head>
            <title>Transcribe and Summarize Video</title>
            <style>
                body { padding: 20px; }
                .container { max-width: 800px; margin: 0 auto; }
                .result { white-space: pre-wrap; margin-top: 20px; }
                button { margin-top: 10px; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Транскрипция и суммаризация видео</h1>
                <div>
                    <h3>Получить текст из видео:</h3>
                    <input type="text" id="videoUrl" placeholder="URL видео" size="50">
                    <button onclick="transcribe()">Транскрибировать</button>
                </div>
                <div>
                    <h3>Суммаризировать текст:</h3>
                    <textarea id="textToSummarize" rows="10" cols="80" placeholder="Вставьте текст для суммаризации"></textarea>
                    <br>
                    <button onclick="summarize()">Суммаризировать</button>
                </div>
                <div id="result" class="result"></div>
            </div>
            <script>
                async function transcribe() {
                    const url = document.getElementById('videoUrl').value;
                    if (!url) {
                        alert('Введите URL видео');
                        return;
                    }
                    document.getElementById('result').textContent = 'Загрузка...';
                    try {
                        const response = await fetch('/transcribe', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify({url: url})
                        });
                        const data = await response.json();
                        document.getElementById('textToSummarize').value = data.text;
                        document.getElementById('result').textContent = data.text;
                    } catch (error) {
                        document.getElementById('result').textContent = 'Ошибка: ' + error;
                    }
                }

                async function summarize() {
                    const text = document.getElementById('textToSummarize').value;
                    if (!text) {
                        alert('Введите текст для суммаризации');
                        return;
                    }
                    document.getElementById('result').textContent = 'Обработка...';
                    try {
                        const response = await fetch('/summarize', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify({text: text})
                        });
                        const data = await response.json();
                        if (!response.ok) {
                            throw new Error(data.detail.message || 'Произошла ошибка при суммаризации');
                        }
                        document.getElementById('result').textContent = data.summary;
                    } catch (error) {
                        document.getElementById('result').textContent = 'Ошибка: ' + error.message;
                        console.error('Ошибка:', error);
                    }
                }
            </script>
        </body>
    </html>
    """

@app.post("/transcribe")
async def transcribe_video(payload: dict):
    """Эндпоинт для извлечения текста из видео"""
    url = payload.get("url")
    if not url:
        raise HTTPException(status_code=400, detail="URL не передан")
    try:
        text = download_and_transcribe(url)
        return {"text": text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/summarize")
async def summarize_endpoint(payload: dict):
    """Эндпоинт для суммаризации текста"""
    text = payload.get("text")
    if not text:
        raise HTTPException(status_code=400, detail="Текст не передан")
    try:
        summary = summarize_text(text)
        return {"summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 