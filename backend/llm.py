import time
import requests
from requests.exceptions import RequestException, Timeout

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "phi3"


def call_llm(prompt, max_retries: int = 3):
    """
    Call the local LLM with simple retry/backoff logic and safer timeouts.

    Returns a string (empty string on failure).
    """
    # retry schedule: tuple of (connect_timeout, read_timeout, backoff_seconds)
    attempts = [((3, 8), 0), ((3, 15), 1), ((3, 30), 2)]

    for attempt in range(min(max_retries, len(attempts))):
        (timeouts, backoff) = attempts[attempt]
        try:
            response = requests.post(
                OLLAMA_URL,
                json={
                    "model": MODEL_NAME,
                    "prompt": prompt,
                    "stream": False,
                },
                timeout=timeouts,
            )

            if response.status_code != 200:
                print(f"LLM HTTP ERROR (attempt {attempt+1}):", response.status_code, response.text)
                # try again after backoff if attempts remain
                if attempt < max_retries - 1:
                    time.sleep(backoff)
                    continue
                return ""

            data = response.json()

            # Safe extraction
            if "response" in data and data["response"]:
                return data["response"].strip()

            print("LLM EMPTY RESPONSE (attempt {}):".format(attempt + 1), data)
            return ""

        except Timeout as te:
            print(f"LLM TIMEOUT (attempt {attempt+1}):", te)
            if attempt < max_retries - 1:
                time.sleep(backoff)
                continue
            return ""
        except RequestException as re:
            print(f"LLM REQUEST ERROR (attempt {attempt+1}):", re)
            if attempt < max_retries - 1:
                time.sleep(backoff)
                continue
            return ""
        except Exception as e:
            print(f"LLM UNEXPECTED ERROR (attempt {attempt+1}):", e)
            return ""
