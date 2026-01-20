# jarvis_llm.py

import os
os.environ["TQDM_DISABLE"] = "1"

import sys
from gpt4all import GPT4All
from contextlib import contextmanager


@contextmanager
def _suppress_c_stderr():
    """
    Redirect C-level stderr (fd=2) to os.devnull
    to silence native library noise.
    """
    devnull = open(os.devnull, 'w')
    original_stderr_fd = os.dup(2)
    os.dup2(devnull.fileno(), 2)
    try:
        yield
    finally:
        os.dup2(original_stderr_fd, 2)
        os.close(original_stderr_fd)
        devnull.close()


# Initialize GPT4All under suppressed stderr
with _suppress_c_stderr():
    bot = GPT4All(
        "Meta-Llama-3-8B-Instruct.Q4_0.gguf",
        allow_download=False,   # safe now
        verbose=False
    )


def chat_with_ai(prompt: str, max_tokens: int = 128) -> str:
    """Zero-quota local LLM via GPT4All (CPU-only)."""
    try:
        return bot.generate(prompt, max_tokens=max_tokens)
    except Exception as e:
        return f"[Local LLM error]: {e}"
