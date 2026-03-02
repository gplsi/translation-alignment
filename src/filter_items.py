import json
import argparse
from src.apply import process_directory

RAISE_ON_ERROR = True

_nlp_cache = {}

def _get_nlp(lang: str):
    # Map language codes to spaCy models
    model_map = {
        "es": "es_core_news_sm",
        "ca": "ca_core_news_sm",
        "va": "ca_core_news_sm",  # Valencian -> Catalan model
        "en": "en_core_web_sm",
    }
    import spacy
    if lang not in _nlp_cache:
        model_name = model_map.get(lang)
        if not model_name:
            return None
        try:
            _nlp_cache[lang] = spacy.load(model_name)
        except Exception:
            if RAISE_ON_ERROR:
                raise
            else:
                print(f"Warning: Could not load spaCy model for language '{lang}' ({model_name}). NER will be disabled for this language.")
                _nlp_cache[lang] = None
    return _nlp_cache[lang]

def _count_person_org(text: str, nlp):
    if not nlp or not text:
        return {"PERSON": 0, "ORG": 0}
    doc = nlp(text)
    persons = sum(1 for ent in doc.ents if ent.label_ == "PER" or ent.label_ == "PERSON")
    orgs = sum(1 for ent in doc.ents if ent.label_ == "ORG")
    return {"PERSON": persons, "ORG": orgs}

def filter_items(content, threshold=0.67, min_length=0, verbose=False, deprecated_json=False, lang0="va", lang1="es", enable_length=True, enable_ner=True):
    """
    Filters out items where the length of one language's text is noticeably longer than the other
    or where the text in any language is shorter than a specified number of characters.
    Also performs NER on both texts; if counts of PERSON and ORG do not match, the item is skipped.
    
    Args:
        content (str): Content of the input file.
        threshold (float): Minimum acceptable ratio of shorter text length to longer text length.
        min_length (int): Minimum acceptable length for text in any language.
        verbose (bool): Enable verbose output for the filtering process.
        deprecated_json (bool): Use the old JSON approach instead of JSONL.
        lang0 (str): Language code for the first language.
        lang1 (str): Language code for the second language.
        enable_length (bool): Apply length/ratio filter.
        enable_ner (bool): Apply NER matching filter.
    """
    if deprecated_json:
        data = json.loads(content)
    else:
        data = []
        for line in content.splitlines():
            try:
                data.append(json.loads(line))
            except json.JSONDecodeError:
                print(f"Warning: Skipping invalid JSON line: {line}")

    nlp0 = _get_nlp(lang0) if enable_ner else None
    nlp1 = _get_nlp(lang1) if enable_ner else None

    filtered_data = []
    for item in data:
        t0 = item.get(lang0, "")
        t1 = item.get(lang1, "")
        # Length and ratio checks (conditional)
        if enable_length:
            if not (len(t1) >= min_length and len(t0) >= min_length):
                continue
            ratio = min(len(t1), len(t0)) / max(len(t1), len(t0)) if max(len(t1), len(t0)) > 0 else 0
            if ratio < threshold:
                continue
        # NER checks (conditional): require PERSON and ORG counts to match
        if enable_ner:
            c0 = _count_person_org(t0, nlp0)
            c1 = _count_person_org(t1, nlp1)
            if c0["PERSON"] != c1["PERSON"] or c0["ORG"] != c1["ORG"]:
                continue
        filtered_data.append(item)
    
    if len(filtered_data) == 0:
        if verbose:
            print("❌", end="", flush=True)
        return ""
    elif verbose:
        match len(data) - len(filtered_data):
            case 0:
                print("✅", end="", flush=True)
            case 1:
                print("1️⃣", end=" ", flush=True)
            case 2:
                print("2️⃣", end=" ", flush=True)
            case 3:
                print("3️⃣", end=" ", flush=True)
            case 4:
                print("4️⃣", end=" ", flush=True)
            case 5:
                print("5️⃣", end=" ", flush=True)
            case 6:
                print("6️⃣", end=" ", flush=True)
            case 7:
                print("7️⃣", end=" ", flush=True)
            case 8:
                print("8️⃣", end=" ", flush=True)
            case 9:
                print("9️⃣", end=" ", flush=True)
            case 10:
                print("🔟", end="", flush=True)
            case _:
                print(f"🟨", end="", flush=True)
    if deprecated_json:
        output = json.dumps(filtered_data, ensure_ascii=False, indent=4)
    else:
        output = "\n".join(json.dumps(item, ensure_ascii=False) for item in filtered_data)
    return output

def main():
    parser = argparse.ArgumentParser(description="Filter items based on selectable filters (length/ratio and NER).")
    parser.add_argument("input_path", type=str, help="Path to the input JSON or JSONL file.")
    parser.add_argument("--output_suffix", type=str, help="Suffix to append to the output file name (e.g., '.filtered').", default=None)
    parser.add_argument("--threshold", type=float, default=0.67, help="Minimum acceptable ratio of shorter text length to longer text length (default: 0.67).")
    parser.add_argument("--min_length", type=int, default=0, help="Minimum acceptable length for text in any language (default: 0).")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output.")
    parser.add_argument("--deprecated-json", action="store_true", help="Use the old JSON approach instead of JSONL.")
    parser.add_argument("--lang0", default="va", help="Language code for the first language (default: va)")
    parser.add_argument("--lang1", default="es", help="Language code for the second language (default: es)")
    parser.add_argument("--enable-length", action="store_true", help="Enable length/ratio filter.")
    parser.add_argument("--enable-ner", action="store_true", help="Enable NER matching filter.")
    
    args = parser.parse_args()

    # Require at least one filter selected
    if not (args.enable_length or args.enable_ner):
        parser.error("You must enable at least one filter: --enable-length or --enable-ner")

    if args.output_suffix is None:
        suffix_parts = []
        if args.enable_length:
            suffix_parts.append("length")
        if args.enable_ner:
            suffix_parts.append("ner")
        args.output_suffix = '.'.join(suffix_parts)

    process_directory(
        args.input_path,
        args.output_suffix,
        lambda content: filter_items(
            content,
            args.threshold,
            args.min_length,
            args.verbose,
            args.deprecated_json,
            args.lang0,
            args.lang1,
            enable_length=args.enable_length,
            enable_ner=args.enable_ner,
        ),
        verbose=not args.verbose,
    )

    print(f"Filtering completed! Args: {args}")

if __name__ == "__main__":
    main()
