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
        Sei un valutatore SEVERO della qualità di parsing web.

        Confronta il DOCUMENTO PARSATO con il GOLD STANDARD e valuta quanto il parsing abbia preservato correttamente il contenuto informativo.

        Considera questi difetti:
        - contenuti mancanti;
        - contenuti errati o aggiunti;
        - rumore (menu, footer, banner, cookie notice, pubblicità);
        - duplicazioni;
        - problemi strutturali (titoli, sezioni, liste, tabelle, ordine dei contenuti).

        Usa questa scala in modo rigoroso:
        - 1 = i due testi parlano di cose diverse, oppure manca quasi tutto il contenuto, oppure uno dei due è vuoto;
        - 2 = molti errori: gran parte del contenuto è persa, sbagliata o sommersa dal rumore;
        - 3 = contenuto solo parziale, con errori evidenti o rumore significativo;
        - 4 = buono: il contenuto coincide quasi del tutto, restano solo piccole imperfezioni;
        - 5 = estrazione quasi perfetta: nessuna parte importante mancante, nessun rumore.

        Regole:
        - Basati ESCLUSIVAMENTE sui due testi qui sotto: non usare conoscenze esterne e non inventare contenuti, difetti o informazioni non presenti nei testi.
        - Scrivi PRIMA il feedback elencando i difetti concreti, POI assegna un voto coerente con quei difetti.
        - Assegna 4 o 5 SOLO se il contenuto informativo dei due testi coincide davvero.
        - Se i due testi trattano argomenti diversi, assegna 1.
        - Non essere generoso: nel dubbio, abbassa il voto.

        Esempi di output:
        {{"feedback": "I due testi parlano di argomenti completamente diversi: nessun contenuto in comune.", "score": 1}}
        {{"feedback": "Manca circa metà del contenuto ed è presente molto rumore da menu e footer.", "score": 2}}
        {{"feedback": "Contenuto fedele al riferimento, solo piccole differenze di formattazione.", "score": 5}}

        Testo estratto dal parser:
        {parsed_truncated}

        Testo di riferimento (Gold Standard):
        {gold_truncated}

        Rispondi SOLO con un JSON nel seguente formato (il feedback deve essere una o due frasi al massimo):
        {{"feedback": "<difetti principali del testo>", "score": <intero tra 1 e 5>}}
        """
    )
