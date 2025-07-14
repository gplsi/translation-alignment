import json
import argparse

def filter_items(input_path, output_path, threshold=0.67, min_length=0):
    """
    Filters out items where the length of one language's text is noticeably longer than the other
    or where the text in any language is shorter than a specified number of characters.
    
    Args:
        input_path (str): Path to the input JSON file.
        output_path (str): Path to save the filtered JSON file.
        threshold (float): Minimum acceptable ratio of shorter text length to longer text length.
        min_length (int): Minimum acceptable length for text in any language.
    """
    with open(input_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    filtered_data = [
        item for item in data
        if len(item['spanish']) >= min_length
        and len(item['valencian']) >= min_length
        and min(len(item['spanish']), len(item['valencian'])) / max(len(item['spanish']), len(item['valencian'])) >= threshold
    ]

    with open(output_path, 'w', encoding='utf-8') as file:
        json.dump(filtered_data, file, ensure_ascii=False, indent=4)

def main():
    parser = argparse.ArgumentParser(description="Filter items based on text length ratio and minimum text length.")
    parser.add_argument("input_path", type=str, help="Path to the input JSON file.")
    parser.add_argument("output_path", type=str, help="Path to save the filtered JSON file.")
    parser.add_argument("--threshold", type=float, default=0.67, help="Minimum acceptable ratio of shorter text length to longer text length (default: 0.67).")
    parser.add_argument("--min_length", type=int, default=0, help="Minimum acceptable length for text in any language (default: 0).")
    
    args = parser.parse_args()
    filter_items(args.input_path, args.output_path, args.threshold, args.min_length)

if __name__ == "__main__":
    main()
