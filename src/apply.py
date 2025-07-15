import os
import shutil
import argparse

def transform_function(content):
    # Example transformation: convert content to uppercase
    return content.upper()

def process_directory(input_dir, output_dir, transform_function, verbose=False, keep_empty=False):
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    for root, dirs, files in os.walk(input_dir):
        # Recreate directory structure in output_dir
        relative_path = os.path.relpath(root, input_dir)
        target_dir = os.path.join(output_dir, relative_path)
        os.makedirs(target_dir, exist_ok=True)

        for file in files:
            input_file_path = os.path.join(root, file)
            output_file_path = os.path.join(target_dir, file)

            if verbose:
                print(f"Processing file: {input_file_path} -> {output_file_path}")

            # Read, transform, and write the file content
            with open(input_file_path, 'r', encoding='utf-8') as infile:
                content = infile.read()
            transformed_content = transform_function(content)

            if not transformed_content.strip() and not keep_empty:
                if verbose:
                    print(f"Skipping empty file: {input_file_path}")
                continue

            with open(output_file_path, 'w', encoding='utf-8') as outfile:
                outfile.write(transformed_content)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process files in a directory and apply a transformation.")
    parser.add_argument("input_dir", help="Path to the input directory")
    parser.add_argument("output_dir", help="Path to the output directory")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument("--keep-empty", action="store_true", help="Process empty files")
    args = parser.parse_args()

    process_directory(args.input_dir, args.output_dir, transform_function, verbose=args.verbose, keep_empty=args.keep_empty)
