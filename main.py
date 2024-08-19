#VoiceHelper 0.0.2
import os
import sys
import webbrowser
import customtkinter as ctk
import threading
from speech_recognition import Recognizer, Microphone, UnknownValueError
import time
from PIL import Image, ImageTk
from g4f.client import Client
from gtts import gTTS
import winsound
import asyncio

if sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

client = Client()

class VoiceHelperApp:
    def __init__(self, root):
        self.root = root
        self.root.withdraw()  # Скрыть основное окно при загрузке
        self.loading_label = None
        self.show_loading_animation()
    def chatgptquestion(self, zadanie):
        response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": zadanie}],
            )
        audio = gTTS(text=response.choices[0].message.content, lang="ru", slow=False)
        audio.save("example.wav")
        filename = "example.wav"
        winsound.PlaySound("example.wav", winsound.SND_FILENAME | winsound.SND_ASYNC)

    def show_loading_animation(self):
        loading_window = ctk.CTkToplevel(self.root)
        loading_window.geometry("300x200")
        loading_window.title("Загрузка")

        self.loading_label = ctk.CTkLabel(loading_window, text="Загрузка...", font=("Helvetica", 20))
        self.loading_label.pack(pady=(20, 10))

        self.progress_bar = ctk.CTkProgressBar(loading_window, width=200)
        self.progress_bar.pack(pady=20)
        self.progress_bar.set(0)  # Устанавливаем начальное значение

        self.loading_animation(loading_window, 0)

    def loading_animation(self, loading_window, value):
        if value <= 100:
            self.progress_bar.set(value / 100)  # Устанавливаем значение прогресс-бара
            loading_window.update_idletasks()
            self.root.after(30, self.loading_animation, loading_window, value + 2)
        else:
            self.loading_complete(loading_window)

    def loading_complete(self, loading_window):
        loading_window.destroy()  # Закрыть окно загрузки
        self.initialize_interface()

    def initialize_interface(self):
        self.root.deiconify()  # Показать основное окно
        self.root.title("VoiceHelper 0.0.1")
        self.root.geometry("400x500")
        self.root.configure(bg="black")

        self.status_label = ctk.CTkLabel(self.root, text="Состояние: Жду команды 'привет'", font=("Helvetica", 16), text_color="white")
        self.status_label.pack(pady=20)

        self.image = Image.open("VCLOGO.png")
        self.photo = ImageTk.PhotoImage(self.image)
        self.image_label = ctk.CTkLabel(self.root, image=self.photo, text="")
        self.image_label.pack(pady=20)

        self.recognizer = Recognizer()
        self.listen_start_greeting()

    def listen_start_greeting(self):
        threading.Thread(target=self.wait_for_greeting, daemon=True).start()

    def wait_for_greeting(self):
        while True:
            self.status_label.configure(text="Состояние: Жду команды 'привет'")
            if self.command_with_timeout(2) == "привет":
                filename = 'greet1.wav'
                winsound.PlaySound(filename, winsound.SND_FILENAME)
                self.status_label.configure(text="Состояние: Готов к работе")
                self.listen_commands()

    def listen_commands(self):
        while True:
            self.status_label.configure(text="Состояние: Слушаю команды...")
            zadanie = self.command_with_timeout(2)  # 2 секунды на прослушивание
            if zadanie:
                self.makeSomething(zadanie)

    def command_with_timeout(self, timeout):
        with Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            try:
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=timeout)
                return self.recognizer.recognize_google(audio, language="ru-RU").lower()
            except (UnknownValueError, Exception):
                return ""

    def makeSomething(self, zadanie):
        if 'открой youtube' in zadanie:
            print("Уже открываю")
            webbrowser.open('https://youtube.com')
            filename = 'ok3.wav'
            winsound.PlaySound(filename, winsound.SND_FILENAME)
        elif 'стоп' in zadanie:
            filename = 'thanks.wav'
            winsound.PlaySound(filename, winsound.SND_FILENAME)
            print("До свидания!")
            sys.exit()
        elif 'спасибо' in zadanie:
            filename = 'thanks.wav'
            winsound.PlaySound(filename, winsound.SND_FILENAME)
        elif 'отмена' in zadanie:
            filename = 'thanks.wav'
            winsound.PlaySound(filename, winsound.SND_FILENAME)
        elif(zadanie != ""):
            self.chatgptquestion(zadanie)
        self.wait_for_greeting()  # Возвращаемся к ожиданию команды "привет"

if __name__ == "__main__":
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("blue")
    root = ctk.CTk()
    app = VoiceHelperApp(root)
    root.mainloop()