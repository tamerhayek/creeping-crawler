"""Builds the prompt sent to the LLM judge.

Inputs are truncated to ``MAX_TEXT_CHARS`` to keep CPU inference fast.
"""

MAX_TEXT_CHARS = 1500


def build_judge_prompt(parsed_text: str, gold_text: str) -> str:
    """Return the prompt to send to the judge model."""
    parsed_truncated = parsed_text[:MAX_TEXT_CHARS]
    gold_truncated = gold_text[:MAX_TEXT_CHARS]
    return (
        "Valuta la qualità del seguente testo estratto da una pagina web.\n\n"
        "Testo estratto dal parser:\n"
        f"{parsed_truncated}\n\n"
        "Testo di riferimento (Gold Standard):\n"
        f"{gold_truncated}\n\n"
        "Rispondi SOLO con un JSON nel seguente formato:\n"
        '{"score": <intero tra 1 e 5>, "feedback": "<breve descrizione della qualità del testo>"}'
    )
