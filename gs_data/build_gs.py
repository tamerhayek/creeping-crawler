"""
Gold Standard Builder
=====================
Ogni entry è un file .txt dentro la cartella del dominio.
Lo script legge tutti i file e produce un unico JSON.

STRUTTURA CARTELLE:
  gs_input/
    www.cnbc.com/
      1.txt
      2.txt
      3.txt
      4.txt
      5.txt
    espn.com/
      1.txt
      ...

FORMATO DI OGNI FILE .txt:
  URL: https://www.cnbc.com/articolo
  TITLE: Titolo dell'articolo
  HTML:
  <html>...tutto l'html grezzo...</html>
  GOLD:
  Testo informativo dell'articolo
  su più righe, scrivi liberamente
  fino alla fine del file

USO:
  # Singolo dominio
  python build_gold_standard.py --domain cnbc.com

  # Tutti i domini in gs_data/ in una volta sola
  python build_gold_standard.py --all

  # Mostra il template da copiare
  python build_gold_standard.py --template
"""

import json
import os
import re
import argparse
from pathlib import Path

INPUT_FOLDER  = "gs_data"
OUTPUT_FOLDER = "gs_data"

def parse_entry_file(filepath: Path, domain: str) -> dict:
    """
    Legge un file .txt nel formato:
      URL: ...
      TITLE: ...
      HTML:
      <contenuto multiriga>
      GOLD:
      <contenuto multiriga fino alla fine del file>
    """
    content = filepath.read_text(encoding="utf-8")

    # Estrai URL
    url_match = re.search(r"^URL:\s*(.+)$", content, re.MULTILINE)
    if not url_match:
        raise ValueError(f"[{filepath.name}] Manca il campo 'URL:'")
    url = url_match.group(1).strip()

    # Estrai TITLE
    title_match = re.search(r"^TITLE:\s*(.+)$", content, re.MULTILINE)
    if not title_match:
        raise ValueError(f"[{filepath.name}] Manca il campo 'TITLE:'")
    title = title_match.group(1).strip()

    # Estrai HTML (tutto tra riga "HTML:" e riga "GOLD:")
    html_match = re.search(r"^HTML:\s*\n(.*?)\nGOLD:", content, re.DOTALL | re.MULTILINE)
    if not html_match:
        raise ValueError(f"[{filepath.name}] Manca il blocco 'HTML:' oppure 'GOLD:'")
    html_text = html_match.group(1).strip()

    # Estrai GOLD (tutto dopo "GOLD:" fino alla fine del file)
    gold_match = re.search(r"^GOLD:\s*\n(.+)$", content, re.DOTALL | re.MULTILINE)
    if not gold_match:
        raise ValueError(f"[{filepath.name}] Manca il blocco 'GOLD:' o è vuoto")
    gold_text = gold_match.group(1).strip()

    return {
        "url":       url,
        "domain":    domain,
        "title":     title,
        "html_text": html_text,
        "gold_text": gold_text,
    }


def build_domain(domain: str) -> list[dict]:
    folder = Path(INPUT_FOLDER) / domain

    if not folder.exists():
        raise FileNotFoundError(
            f"Cartella non trovata: '{folder}'\n"
            f"Crea la cartella e inserisci i file 1.txt, 2.txt, ..."
        )

    txt_files = sorted(folder.glob("*.txt"), key=lambda f: f.stem)
    if not txt_files:
        raise ValueError(f"Nessun file .txt trovato in '{folder}'")

    entries = []
    errors  = []

    for f in txt_files:
        try:
            entry = parse_entry_file(f, domain)
            entries.append(entry)
            print(f"  ✓ {f.name:12s} → {entry['url'][:70]}")
        except Exception as e:
            errors.append(str(e))
            print(f"  ✗ {f.name:12s} → ERRORE: {e}")

    if errors:
        print(f"\n  ⚠️  {len(errors)} file con errori ignorati.")

    return entries


def validate(entries: list[dict], domain: str):
    required = {"url", "domain", "title", "html_text", "gold_text"}
    for i, e in enumerate(entries, 1):
        missing = required - set(e.keys())
        if missing:
            print(f"  ⚠️  Entry {i}: campi mancanti → {missing}")
        if len(e.get("gold_text", "")) < 50:
            print(f"  ⚠️  Entry {i}: gold_text molto corto ({len(e.get('gold_text',''))} chars)")
    if len(entries) < 5:
        print(f"  ⚠️  Solo {len(entries)} entry per '{domain}' (minimo richiesto: 5)")


def save_gs(entries: list[dict], domain: str):
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    domain_safe = domain.replace(".", "_")
    output_path = Path(OUTPUT_FOLDER) / f"{domain_safe}_gs.json"

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)

    print(f"\n  ✅ Salvato: {output_path}  ({len(entries)} entry)\n")


def print_template():
    template = """\
# Copia questo testo in un file (es. 1.txt) e compila i campi.
# Le righe che iniziano con # sono commenti e vengono ignorati.

URL: https://www.cnbc.com/tuo-articolo
TITLE: Titolo dell'articolo
HTML:
<html>
  <body>
    <h1>Incolla qui l'HTML grezzo della pagina</h1>
    <p>Puoi ottenerlo da DevTools → Console → document.documentElement.outerHTML</p>
  </body>
</html>
GOLD:
Titolo dell'articolo

Primo paragrafo del testo informativo, copiato manualmente dal browser.
Puoi andare a capo liberamente, scrivere su più righe senza problemi.

Sezione successiva dell'articolo

Altro testo informativo...
"""
    print("\nTEMPLATE per i file .txt\n" + "=" * 40)
    print(template)


def main():
    parser = argparse.ArgumentParser(description="Gold Standard Builder")
    parser.add_argument("--domain",   help="Es: cnbc.com, espn.com, xe.com")
    parser.add_argument("--all",      action="store_true",
                        help="Processa tutti i domini trovati in gs_input/")
    parser.add_argument("--template", action="store_true",
                        help="Mostra il template da usare per i file .txt")
    args = parser.parse_args()

    if args.template:
        print_template()
        return

    if not args.domain and not args.all:
        parser.print_help()
        return

    # Determina quali domini processare
    if args.all:
        input_path = Path(INPUT_FOLDER)
        if not input_path.exists():
            print(f"❌ Cartella '{INPUT_FOLDER}' non trovata.")
            return
        domains = [d.name for d in sorted(input_path.iterdir()) if d.is_dir()]
        if not domains:
            print(f"❌ Nessuna sottocartella trovata in '{INPUT_FOLDER}'")
            return
    else:
        domains = [args.domain]

    for domain in domains:
        print(f"\n📂 Dominio: {domain}")
        print(f"   {'─' * 50}")
        try:
            entries = build_domain(domain)
            validate(entries, domain)
            save_gs(entries, domain)
        except Exception as e:
            print(f"  ❌ {e}\n")


if __name__ == "__main__":
    main()
