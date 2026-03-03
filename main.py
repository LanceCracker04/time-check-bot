import speech_recognition as sr
import pygame
from datetime import datetime
import time
import os
import asyncio
import edge_tts

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
    # Format: "7:05" becomes "Seven Oh Five"
    h = now.strftime("%I")
    m = now.strftime("%M")

    # Construct the full natural sentence
    time_text = f"It is {int(h)} {m} Sir."
    if 0 < int(m) < 10:
        time_text = f"It is {int(h)} oh {int(m)} Sir."

    print(f"J.A.R.V.I.S.: {time_text}")

    # Generate audio synchronously
    try:
        # Ensure sounds directory exists
        os.makedirs("sounds", exist_ok=True)

        # Stop and unload any currently playing music to avoid file lock
        pygame.mixer.music.stop()
        pygame.mixer.music.unload()
        time.sleep(0.2)  # Small delay to release file lock

        communicate = edge_tts.Communicate(time_text, "en-GB-RyanNeural")
        # Use asyncio to run the async save method
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(communicate.save("sounds/current_time.mp3"))
        loop.close()

        # Play the audio file using Sound channel instead of music player
        sound = pygame.mixer.Sound("sounds/current_time.mp3")
        channel = sound.play()
        while channel.get_busy():
            time.sleep(0.05)
    except Exception as e:
        print(f"Error speaking: {e}")


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
