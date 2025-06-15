import os
import json
import queue
import requests
import pyttsx3
import sounddevice as sd
from vosk import Model, KaldiRecognizer


class VoiceAssistant:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.model_path = "model"
        self.model = self.load_model()
        self.recognizer = KaldiRecognizer(self.model, 16000)
        self.audio_queue = queue.Queue()
        self.current_user = {}

    def load_model(self):
        if not os.path.exists(self.model_path):
            self.speak("Модель не найдена. Скачайте модель Vosk и положите в папку model.")
            exit()
        return Model(self.model_path)

    def speak(self, text):
        print("Ассистент:", text)
        self.engine.say(text)
        self.engine.runAndWait()

    def listen(self):
        with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                               channels=1, callback=self.callback):
            self.speak("Говорите команду...")
            while True:
                data = self.audio_queue.get()
                if self.recognizer.AcceptWaveform(data):
                    result = json.loads(self.recognizer.Result())
                    command = result.get("text", "")
                    if command:
                        print("Вы сказали:", command)
                        self.handle_command(command)
                        break

    def callback(self, indata, frames, time, status):
        if status:
            print("Ошибка аудио:", status)
        self.audio_queue.put(bytes(indata))

    def handle_command(self, command):
        if "создать" in command:
            self.create_user()
        elif "имя" in command:
            self.say_name()
        elif "страна" in command:
            self.say_country()
        elif "анкета" in command:
            self.say_profile()
        elif "сохранить" in command or "фото" in command:
            self.save_photo()
        elif "выход" in command or "завершить" in command:
            self.speak("Завершаю работу. До свидания!")
            exit(0)
        else:
            self.speak("Команда не распознана.")


    def create_user(self):
        try:
            response = requests.get("https://randomuser.me/api/")
            self.current_user = response.json()['results'][0]
            self.speak("Пользователь успешно создан.")
        except Exception as e:
            self.speak("Ошибка при создании пользователя.")
            print("Ошибка:", e)

    def say_name(self):
        if self.current_user:
            name = self.current_user['name']
            full_name = f"{name['title']} {name['first']} {name['last']}"
            self.speak(f"Имя пользователя: {full_name}")
        else:
            self.speak("Пользователь не создан.")

    def say_country(self):
        if self.current_user:
            country = self.current_user['location']['country']
            self.speak(f"Страна пользователя: {country}")
        else:
            self.speak("Пользователь не создан.")

    def say_profile(self):
        if self.current_user:
            name = self.current_user['name']
            loc = self.current_user['location']
            email = self.current_user['email']
            profile = (
                f"Анкета пользователя:\n"
                f"Имя: {name['title']} {name['first']} {name['last']}\n"
                f"Город: {loc['city']}, страна: {loc['country']}\n"
                f"Электронная почта: {email}"
            )
            self.speak(profile)
        else:
            self.speak("Пользователь не создан.")

    def save_photo(self):
        if self.current_user:
            try:
                photo_url = self.current_user['picture']['large']
                image = requests.get(photo_url).content
                with open("user_photo.jpg", "wb") as f:
                    f.write(image)
                self.speak("Фото пользователя сохранено.")
            except Exception as e:
                self.speak("Не удалось сохранить фото.")
                print("Ошибка:", e)
        else:
            self.speak("Пользователь не создан.")


if __name__ == "__main__":
    assistant = VoiceAssistant()
    while True:
        assistant.listen()
