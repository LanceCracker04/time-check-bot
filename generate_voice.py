import asyncio
import edge_tts
import os  # Make sure this is here!

VOICE = "en-GB-RyanNeural"


async def create_audio(text, filename):
    communicate = edge_tts.Communicate(text, VOICE)
    await communicate.save(filename)
    print(f"Generated: {filename}")


async def main():
    # --- ADD THESE LINES HERE ---
    os.makedirs("sounds/hours", exist_ok=True)
    os.makedirs("sounds/minutes", exist_ok=True)
    # ----------------------------

    # 1. Generate the "Intros"
    await create_audio("It is", "sounds/intro.mp3")
    await create_audio("Sir, the time today is", "sounds/intro_formal.mp3")
    await create_audio("sir", "sounds/sir.mp3")

    # Change the range to start at 0
    for i in range(0, 60):
        if i == 0:
            # This makes '0.mp3' say "oh" instead of "zero"
            await create_audio("oh", "sounds/minutes/0.mp3")
        else:
            if i <= 12:
                await create_audio(str(i), f"sounds/hours/{i}.mp3")
            await create_audio(str(i), f"sounds/minutes/{i}.mp3")


if __name__ == "__main__":
    asyncio.run(main())
