import os
import json
import argparse
from tqdm import tqdm  # Added tqdm import

def find_json_files(directories, extension):
    """Recursively find all files with the given extension in the directories."""
    files = []
    for directory in directories:
        for root, _, filenames in os.walk(directory):
            files.extend(os.path.join(root, file) for file in filenames if file.endswith(extension))
    return files

def read_objects(fd, is_json):
    if is_json:
        yield from json.load(fd)
    else:
        for line in fd:
            yield json.loads(line)


def process_jsonl_files(jsonl_files, is_json):
    """Process each .jsonl file and write sentences in the specified format."""
    output_file = "processed_sentences.jsonl"
    with open(output_file, 'w', encoding='utf-8') as outfile:
        for jsonl_file in tqdm(jsonl_files, desc="Processing files"):  # Added tqdm for file iteration
            with open(jsonl_file, 'r', encoding='utf-8') as infile:
                for json_obj in read_objects(infile, is_json):
                    sentences = []
                    for lang, sentence in json_obj.items():
                        lang_name = get_language_name(lang)
                        sentences.append(f"{lang_name}: {sentence}")
                    outfile.write(json.dumps({"text": "\n".join(sentences)}) + "\n")

def get_language_name(lang_code):
    """Map language codes to their full names."""
    language_map = {
        "va": "Valencià",
        "es": "Español",
        "en": "English",
        # Add more mappings as needed
    }
    return language_map.get(lang_code, lang_code.capitalize())

parser = argparse.ArgumentParser(description="Process JSONL or JSON files.")
parser.add_argument("--deprecated-json", action="store_true", help="Search for .json files instead of .jsonl")
args = parser.parse_args()

# Determine the file extension based on the flag
file_extension = ".json" if args.deprecated_json else ".jsonl"

directories = [
    "./output/amic-paralelo (plain aligned-and-filtered)/",
    "./output/boua (md aligned-and-filtered)/",
    "./output/dogv (md aligned-and-filtered)/",
]
json_files = find_json_files(directories, file_extension)
process_jsonl_files(json_files, file_extension == ".json")
