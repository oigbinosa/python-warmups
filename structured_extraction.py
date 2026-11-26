import csv
import os
import time
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types
from purchase_extraction import PurchaseExtraction

load_dotenv()

LOG_FILE = Path("llm_usage.csv")
FIELDS = [
    "timestamp",
    "model",
    "input_tokens",
    "output_tokens",
    "latency_s",
    "est_cost_usd",
]
PRICES = {
    "Gemini 3.5 Flash-Lite": {"input": 0.30, "output": 2.50},
}
MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")

SYSTEM_PROMPT = (
    "extract from this supplier email the vendor, item being supplied, quantity, and the date it's needed by."
    "if any value can not be confidently determined leave as None"
)


def log_call(row: dict) -> None:
    is_new_file = not LOG_FILE.exists()
    with LOG_FILE.open("a", newline="") as f:  # "a" = append, keeps earlier rows
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        if is_new_file:
            writer.writeheader()  # column names, written once
        writer.writerow(row)


def estimate_cost(model: str, usage) -> float:
    price = PRICES[model]
    input_tokens = usage.prompt_token_count or 0
    output_tokens = (usage.candidates_token_count or 0) + (
        usage.thoughts_token_count or 0
    )
    return (input_tokens * price["input"] + output_tokens * price["output"]) / 1_000_000


def extract(email_text: str) -> PurchaseExtraction:

    start = time.perf_counter()

    client = genai.Client()
    response = client.models.generate_content(
        model=MODEL,
        contents=email_text,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            response_mime_type="application/json",  # return JSON, not prose
            response_schema=PurchaseExtraction,  # ...in exactly this shape
            temperature=0.0,
        ),
    )

    latency = time.perf_counter() - start
    usage = response.usage_metadata
    result = response.parsed  # a PurchaseExtraction instance, or None if parsing failed

    if result is None:
        # fall back to validating the raw text yourself, to see the actual error
        result = PurchaseExtraction.model_validate_json(response.text)
    cost = estimate_cost("Gemini 3.5 Flash-Lite", usage)
    log_call(
        {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "model": MODEL,
            "input_tokens": usage.prompt_token_count,
            "output_tokens": usage.candidates_token_count,
            "latency_s": round(latency, 2),
            "est_cost_usd": round(cost, 6),
        }
    )
    return result


def main() -> None:  # 5. a main() that runs the script's steps
    for path in sorted(Path("sample_emails").glob("*.txt")):
        email_text = path.read_text()

        print(f"\n=== {path.name} ===")

        purchase_extract = extract(email_text)

        print(
            purchase_extract.vendor,
            purchase_extract.quantity,
            purchase_extract.needed_by,
        )


if __name__ == "__main__":
    main()
