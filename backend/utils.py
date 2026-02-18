import json
import re

def safe_json_parse(text):
    if not text:
        return None

    start = text.find("{")
    end = text.rfind("}") + 1

    if start == -1 or end == -1:
        return None

    json_str = text[start:end]
    json_str = json_str.replace("'", '"')
    json_str = re.sub(r",\s*}", "}", json_str)

    try:
        return json.loads(json_str)
    except:
        return None
