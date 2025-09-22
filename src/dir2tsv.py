import os
import json
import pandas as pd
import argparse
from tqdm import tqdm
from pathlib import Path

def explore_directory_to_dataframe(directory):
    data = []
    files = [os.path.join(root, file) for root, _, files in os.walk(directory) for file in files if file.endswith('.json')]
    
    # Add a progress bar for files
    for file_path in tqdm(files, desc="Processing files"):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = json.load(f)
            # Add a progress bar for JSON items
            for item in tqdm(content, desc=f"Processing JSON in {os.path.basename(file_path)}", leave=False):
                data.append({
                    'VA': item.get('va', ''),
                    'ES': item.get('es', ''),
                    'source': os.path.basename(file_path)
                })
    return pd.DataFrame(data)

def inspect_and_dump(df, output_path):
    print("DataFrame Statistics:")
    print(df.describe(include='all'))
    print("\nDataFrame Head:")
    print(df.head())
    
    if output_path:
        df.to_csv(output_path, index=False, sep='\t')
        print(f"DataFrame saved to {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Explore a directory and process JSON files into a DataFrame.")
    parser.add_argument("directory", type=str, help="Path to the directory to explore.")
    parser.add_argument("output", type=str, help="Path to save the resulting DataFrame as a TSV file.", default=None)
    parser.add_argument("--add-partitions", action='store_true', help="Process files in chunks to manage memory usage.")
    args = parser.parse_args()

    if args.add_partitions:
        for file in Path(args.directory).iterdir():
            df = explore_directory_to_dataframe(str(file))
            inspect_and_dump(df, f"{file.stem}_{args.output}")
    else:
        df = explore_directory_to_dataframe(args.directory)
        inspect_and_dump(df, args.output)