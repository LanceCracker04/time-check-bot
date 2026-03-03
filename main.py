import speech_recognition as sr
import pygame
from datetime import datetime
import time
import os

# 1. PRE-LOAD SOUNDS (Instant J.A.R.V.I.S. Voice)
pygame.mixer.init()


def play_audio(file_path):
    if os.path.exists(file_path):
        sound = pygame.mixer.Sound(file_path)
        channel = sound.play()
        while channel.get_busy():
            time.sleep(0.01)
    else:
        print(f"Missing file: {file_path}")


def tell_time():
    now = datetime.now()
    h = str(int(now.strftime("%I")))
    m = int(now.strftime("%M"))

    # 1. Load sounds for instant playback
    playlist = [
        pygame.mixer.Sound("sounds/intro.mp3"),
        pygame.mixer.Sound(f"sounds/hours/{h}.mp3"),
    ]

    if 0 < m < 10:
        playlist.append(pygame.mixer.Sound("sounds/minutes/0.mp3"))
        playlist.append(pygame.mixer.Sound(f"sounds/minutes/{m}.mp3"))
    elif m >= 10:
        playlist.append(pygame.mixer.Sound(f"sounds/minutes/{m}.mp3"))

    playlist.append(pygame.mixer.Sound("sounds/sir.mp3"))

    # 2. Play with "Overlap" to remove the robotic gaps
    for snd in playlist:
        snd.play()
        # Overlap by 0.1s to make it sound human
        time.sleep(max(0, snd.get_length() - 0.1))

# 2. THE EAR (Google Engine - Always Active)
recognizer = sr.Recognizer()
recognizer.energy_threshold = 1200  # Ignores background noise effectively
recognizer.dynamic_energy_threshold = False


def listen_for_command():
    with sr.Microphone() as source:
        # Add this line to see the volume in your terminal
        print(f"Current Noise Level: {recognizer.energy_threshold}")
        recognizer.adjust_for_ambient_noise(source, duration=0.5)

        try:
            # listem for up to 4 seconds of speech
            audio = recognizer.listen(source, timeout=None, phrase_time_limit=4)

            # Use Google for high accuracy (no more "Hey Jack")
            command = recognizer.recognize_google(audio).lower()
            print(f"I heard: '{command}'")

            # Use a "fuzzy" check so "time check" or "what time is it" both work
            if "time" in command and ("check" in command or "is" in command):
                tell_time()

        except sr.UnknownValueError:
            # He heard noise but didn't know the word - keep listening
            pass
        except sr.RequestError:
            print("ERROR: Internet connection lost. Checking...")
            time.sleep(5)  # Wait before trying again
        except Exception:
            pass


if __name__ == "__main__":
    while True:
        listen_for_command()
