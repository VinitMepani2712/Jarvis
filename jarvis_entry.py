from dotenv import load_dotenv
import os
import threading
import queue
import time

load_dotenv()

from jarvis_llm import chat_with_ai
from jarvis_core import handle_command, speak, listen, greet_on_startup, init_audio

EXIT_KEYWORDS = ("exit", "quit", "goodbye", "stop")

LISTEN_TIMEOUT = 10        # seconds
LLM_TIMEOUT = 20           # seconds


def listen_with_timeout(timeout=LISTEN_TIMEOUT):
    """Run listen() in a thread so it can never block forever."""
    q = queue.Queue()

    def _listen():
        try:
            q.put(listen(timeout=timeout, phrase_time_limit=12))
        except Exception as e:
            q.put(e)

    t = threading.Thread(target=_listen, daemon=True)
    t.start()

    try:
        result = q.get(timeout=timeout + 2)
        if isinstance(result, Exception):
            raise result
        return result
    except queue.Empty:
        return None


def llm_with_timeout(prompt, timeout=LLM_TIMEOUT):
    """Run LLM in a thread to prevent hangs."""
    q = queue.Queue()

    def _run():
        try:
            q.put(chat_with_ai(prompt))
        except Exception as e:
            q.put(e)

    t = threading.Thread(target=_run, daemon=True)
    t.start()

    try:
        result = q.get(timeout=timeout)
        if isinstance(result, Exception):
            raise result
        return result
    except queue.Empty:
        return "Sorry, I am taking too long to think. Please try again."


def main():
    init_audio()
    greet_on_startup()
    speak("I am Jarvis. I am listening.")

    while True:
        try:
            #  Non-blocking listen
            cmd = listen_with_timeout()

            if not cmd:
                continue

            cmd = cmd.lower().strip()
            print("User:", cmd)

            #  Exit
            if any(k in cmd for k in EXIT_KEYWORDS):
                speak("Goodbye.")
                break

            #  Built-in commands
            handled = handle_command(cmd)
            if handled:
                speak(handled)
                continue

            #  LLM with hard timeout
            reply = llm_with_timeout(cmd)
            speak(reply)

        except KeyboardInterrupt:
            speak("Goodbye.")
            break
        except Exception as e:
            print("Error:", e)
            speak("I had an internal error, but I am still running.")
            time.sleep(1)


if __name__ == "__main__":
    main()
