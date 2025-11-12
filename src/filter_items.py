import json
import argparse
from src.apply import process_directory

def filter_items(content, threshold=0.67, min_length=0, verbose=False, deprecated_json=False, lang0="va", lang1="es"):
    """
    Filters out items where the length of one language's text is noticeably longer than the other
    or where the text in any language is shorter than a specified number of characters.
    
    Args:
        content (str): Content of the input file.
        threshold (float): Minimum acceptable ratio of shorter text length to longer text length.
        min_length (int): Minimum acceptable length for text in any language.
        verbose (bool): Enable verbose output for the filtering process.
        deprecated_json (bool): Use the old JSON approach instead of JSONL.
        lang0 (str): Language code for the first language.
        lang1 (str): Language code for the second language.
    """
    if deprecated_json:
        data = json.loads(content)
    else:
        data = [json.loads(line) for line in content.splitlines()]

    filtered_data = [
        item for item in data
        if len(item[lang1]) >= min_length
        and len(item[lang0]) >= min_length
        and min(len(item[lang1]), len(item[lang0])) / max(len(item[lang1]), len(item[lang0])) >= threshold
    ]
    
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
    parser = argparse.ArgumentParser(description="Filter items based on text length ratio and minimum text length.")
    parser.add_argument("input_path", type=str, help="Path to the input JSON or JSONL file.")
    parser.add_argument("output_path", type=str, help="Path to save the filtered JSON or JSONL file.")
    parser.add_argument("--threshold", type=float, default=0.67, help="Minimum acceptable ratio of shorter text length to longer text length (default: 0.67).")
    parser.add_argument("--min_length", type=int, default=0, help="Minimum acceptable length for text in any language (default: 0).")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output.")
    parser.add_argument("--deprecated-json", action="store_true", help="Use the old JSON approach instead of JSONL.")
    parser.add_argument("--lang0", default="va", help="Language code for the first language (default: va)")
    parser.add_argument("--lang1", default="es", help="Language code for the second language (default: es)")
    
    args = parser.parse_args()
    process_directory(
        args.input_path,
        args.output_path,
        lambda content: filter_items(content, args.threshold, args.min_length, args.verbose, args.deprecated_json, args.lang0, args.lang1),
    )

if __name__ == "__main__":
    main()
