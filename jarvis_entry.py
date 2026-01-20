from dotenv import load_dotenv
import os

# Load .env (still useful for future config, but no wake keys needed)
load_dotenv()

from jarvis_llm import chat_with_ai
from jarvis_core import handle_command, speak, listen, greet_on_startup, init_audio

EXIT_KEYWORDS = ("exit", "quit", "goodbye", "stop")


def main():
    # Initialize audio once
    init_audio()
    greet_on_startup()

    speak("I am Jarvis. I am listening.")

    while True:
        try:
            # 🎤 Always listen
            cmd = listen(timeout=8, phrase_time_limit=12)

            if not cmd:
                continue

            cmd = cmd.lower().strip()
            print("User:", cmd)

            # 🚪 Exit condition
            if any(k in cmd for k in EXIT_KEYWORDS):
                speak("Goodbye.")
                break

            # ⚙️ Built-in command handler
            handled = handle_command(cmd)
            if handled:
                speak(handled)
                continue

            reply = chat_with_ai(cmd)
            speak(reply)

        except KeyboardInterrupt:
            speak("Goodbye.")
            break
        except Exception as e:
            speak("Something went wrong.")
            print("Error:", e)


if __name__ == "__main__":
    main()
