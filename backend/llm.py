import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "phi3"


def call_llm(prompt):
    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False
            },
            timeout=(3, 8)  # connect: 3s, read: 8s (fail fast, use fallbacks)
        )

        if response.status_code != 200:
            print("LLM HTTP ERROR:", response.status_code, response.text)
            return ""

        data = response.json()

        # 🔥 SAFE RESPONSE EXTRACTION
        if "response" in data and data["response"]:
            return data["response"].strip()

        print("LLM EMPTY RESPONSE:", data)
        return ""

    except Exception as e:
        print("LLM ERROR:", e)
        return ""
