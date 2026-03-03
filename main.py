import speech_recognition as sr
import pygame
from datetime import datetime
import time
import os

# initialize the speech recognizer as a global object so it can be
# referenced inside listener functions without scope errors
recognizer = sr.Recognizer()
# set a low energy threshold so the microphone is actually sensitive
recognizer.energy_threshold = 300

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

    print(f"J.A.R.V.I.S.: It is {h}:{m:02d} Sir.")

    # 1. This list builds the "Sentence" in the computer's memory first
    # This is why the robot pauses will disappear.
    sentence = []
    sentence.append(pygame.mixer.Sound("sounds/intro.mp3"))
    sentence.append(pygame.mixer.Sound(f"sounds/hours/{h}.mp3"))

    if 0 < m < 10:
        # LOGIC: We explicitly point to your new 0.mp3 here
        if os.path.exists("sounds/minutes/0.mp3"):
            sentence.append(pygame.mixer.Sound("sounds/minutes/0.mp3"))
        sentence.append(pygame.mixer.Sound(f"sounds/minutes/{m}.mp3"))
    elif m >= 10:
        sentence.append(pygame.mixer.Sound(f"sounds/minutes/{m}.mp3"))

    sentence.append(pygame.mixer.Sound("sounds/sir.mp3"))

    # 2. THE PLAYBACK (No Pauses)
    for snd in sentence:
        snd.play()
        # We subtract 0.1s from the length to "stitch" the words together
        # This is the 'Freelancer' fix for the slow robot voice.
        time.sleep(max(0, snd.get_length() - 0.1))


def listen_for_command():
    # refer to the global recognizer instead of recreating it in every call
    global recognizer

    with sr.Microphone() as source:
        # show current energy threshold and adjust for ambient noise
        print(f"Current Noise Level: {recognizer.energy_threshold}")
        recognizer.adjust_for_ambient_noise(source, duration=0.5)

        try:
            # listen for up to 4 seconds of speech
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
