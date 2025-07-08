# Translation Alignment Tool

This project provides a tool for aligning sentences between two languages (e.g., Spanish and Valencian) using either naive or embeddings-based alignment. It supports preprocessing, sentence splitting, and alignment of text files in a directory structure.

## Features

- **Preprocessing**: Handles Markdown formatting, whitespace aggregation, and more.
- **Sentence Splitting**: Uses spaCy or a static method for splitting text into sentences.
- **Sentence Alignment**: Supports naive 1-to-1 alignment or embeddings-based alignment using SentenceTransformers.
- **Batch Processing**: Processes directories recursively, aligning files in `<lang0>/` and `<lang1>/` subdirectories.
- **Output**: Saves aligned sentences in JSON format and optionally dumps split sentences to separate files.

## Requirements

- Python 3.7+
- Required Python packages:
  - `spacy`
  - `markdown`
  - `beautifulsoup4`
  - `sentence-transformers`

Install the dependencies using:
```bash
pip install -r requirements.txt
```

## Usage

### Command-Line Arguments

Run the script with the following arguments:

```bash
python split.py <input_dir> <output_dir> [options]
```

#### Positional Arguments:
- `input_dir`: Path to the input directory containing `<lang0>/` and `<lang1>/` subdirectories.
- `output_dir`: Path to the output directory where results will be saved.

#### Optional Arguments:
- `--disable-dump`: Disable dumping of split sentences to separate files.
- `--static-split`: Use static sentence splitting instead of spaCy.
- `--markdown-format`: Enable Markdown format preprocessing.
- `--aggregate-whitespaces`: Aggregate whitespaces in the text.
- `--verbose`: Enable verbose output.
- `--use-multilingual`: Use a multilingual spaCy model (`xx_sent_ud_sm`) for sentence splitting.
- `--use-alignment-embeddings`: Use embeddings-based alignment instead of naive alignment.
- `--alignment-model-name`: Specify the model name for embeddings-based alignment (default: `distiluse-base-multilingual-cased-v2`).

### Example

Align files in the `input` directory and save results to the `output` directory:

```bash
python split.py input/ output/ --markdown-format --use-alignment-embeddings
```

### Directory Structure

The input directory should have the following structure:
```
input/
├── <lang0>/
│   ├── file1.txt
│   └── file2.txt
├── <lang1>/
│   ├── file1.txt
│   └── file2.txt
```

The output directory will have the following structure:
```
output/
├── <lang0>/
│   ├── file1.txt
│   └── file2.txt
├── <lang1>/
│   ├── file1.txt
│   └── file2.txt
├── aligned/
│   ├── file1.json
│   └── file2.json
```

### Output Format

Aligned sentences are saved in JSON format:
```json
[
    {
        "lang0": "Sentence in language 0.",
        "lang1": "Sentence in language 1."
    },
    ...
]
```

## Notes

- Ensure that the input files in `<lang0>/` and `<lang1>/` subdirectories have matching filenames.
- For embeddings-based alignment, the default model is `distiluse-base-multilingual-cased-v2`. You can specify a different model using the `--alignment-model-name` option.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.