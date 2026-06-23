"""Builds the prompt sent to the LLM judge.

Inputs are truncated to ``MAX_TEXT_CHARS`` to keep CPU inference fast.
"""

MAX_TEXT_CHARS = 1500


def build_judge_prompt(parsed_text: str, gold_text: str) -> str:
    """Return the prompt to send to the judge model."""
    parsed_truncated = parsed_text[:MAX_TEXT_CHARS]
    gold_truncated = gold_text[:MAX_TEXT_CHARS]
    return (
        f"""
        Sei un valutatore della qualità di parsing web.

        Confronta il DOCUMENTO PARSATO con il GOLD STANDARD e valuta quanto il parsing abbia preservato correttamente il contenuto.

        Identifica:

        contenuti mancanti;
        contenuti errati o aggiunti;
        rumore (menu, footer, banner, cookie notice, pubblicità);
        duplicazioni;
        problemi strutturali (titoli, sezioni, liste, tabelle, ordine dei contenuti).
        
        Testo estratto dal parser:
        {parsed_truncated}
        
        Testo di riferimento (Gold Standard):
        {gold_truncated}

        Rispondi SOLO con un JSON nel seguente formato (il feedback deve essere una o due frasi al massimo):
        {{"score": <intero tra 1 e 5>, "feedback": "<breve descrizione della qualità del testo>"}}
        """
    )
