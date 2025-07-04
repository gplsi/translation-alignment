import spacy
import argparse
import os
import json
import re
import markdown
from bs4 import BeautifulSoup


class SentenceAlignmentError(Exception):
    """Custom exception for sentence alignment errors."""
    def __init__(self, message, difference):
        super().__init__(message)
        self.difference = difference


ES = "es"
VA = "va"
nlp = {}


def preprocess_text(text, markdown_format=False, aggregate_whitespaces=False):
    """Preprocess text based on markdown format."""

    if aggregate_whitespaces:
        text = re.sub(r"\s+", " ", text).strip()

    elif markdown_format:
        # Step 1: Remove list markers at the beginning of lines
        text = re.sub(r"\n\s*(-|\+|\*|·)\s*", "\n", text)

        # Step 2: Preserve paragraph breaks (normalize to '\n\n')
        text = re.sub(r"\s*\n\s*\n\s*", "\n\n", text)

        # Step 3: Collapse soft line breaks to spaces (single newlines only)
        text = re.sub(r"(?<!\n)\n(?!\n)", " ", text)

        # Step 4: Convert Markdown to HTML
        html = markdown.markdown(text)

        # Step 5: Strip HTML tags
        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text()

        # Step 6: Optional cleanup of multiple newlines
        text = re.sub(r"\n{2,}", "\n", text.strip())

        # Step 7: Aggregate whitespaces
        text = re.sub(r"\s+", " ", text).strip()

    return text


def split_into_sentences(
    text, language, markdown_format=False, aggregate_whitespaces=False
):
    """Tokenize text into sentences using spaCy."""
    text = preprocess_text(text, markdown_format, aggregate_whitespaces)
    doc = nlp[language](text)
    return [sent.text.strip() for sent in doc.sents if sent.text.strip()]


def static_split_into_sentences(
    text, language, markdown_format=False, aggregate_whitespaces=False
):
    """Static function to split text into sentences for testing purposes."""
    text = preprocess_text(text, markdown_format, aggregate_whitespaces)
    return [
        sentence.strip() + "."  # Add a period to each sentence for consistency
        for paragraph in text.split("\n")
        for sentence in re.split("\.(?=\s+(?![0-9])|[^a-zA-Z0-9\s])", paragraph)
        if sentence.strip()
    ]


def align_sentences(sentences1, sentences2):
    """Naive alignment: 1-to-1, truncate to shortest."""
    if len(sentences1) != len(sentences2):
        difference = abs(len(sentences1) - len(sentences2))
        raise SentenceAlignmentError(
            f"Sentence count mismatch: Spanish: {len(sentences1)}, Valencian: {len(sentences2)}",
            difference,
        )
    return list(zip(sentences1, sentences2))


def dump_sentences(sentences, output_file):
    """Dump sentences to a file."""
    with open(output_file, "w", encoding="utf-8") as f:
        for sentence in sentences:
            f.write(sentence + "\n")


def main(
    valencian_file,
    spanish_file,
    output_file,
    output_valencian_file,
    output_spanish_file,
    dump_sentences_enabled=True,
    static_split=False,
    markdown_format=False,
    aggregate_whitespaces=False,
):
    with open(spanish_file, "r", encoding="utf-8") as f:
        spanish_text = f.read()
    with open(valencian_file, "r", encoding="utf-8") as f:
        valencian_text = f.read()

    split = split_into_sentences if not static_split else static_split_into_sentences

    spanish_sentences = split(
        spanish_text,
        ES,
        markdown_format,
        aggregate_whitespaces,
    )
    valencian_sentences = split(
        valencian_text,
        VA,
        markdown_format,
        aggregate_whitespaces,
    )

    # Dump split sentences to separate files if enabled
    if dump_sentences_enabled:
        dump_sentences(spanish_sentences, output_spanish_file)
        dump_sentences(valencian_sentences, output_valencian_file)

    if len(spanish_sentences) != len(valencian_sentences):
        raise SentenceAlignmentError(
            f"Number of sentences do not match: Spanish: {len(spanish_sentences)}, Valencian: {len(valencian_sentences)}",
            abs(len(spanish_sentences) - len(valencian_sentences)),
        )

    aligned = align_sentences(valencian_sentences, spanish_sentences)

    with open(output_file, "w", encoding="utf-8") as out:
        json.dump(
            [{"valencian": val, "spanish": spa} for val, spa in aligned],
            out,
            ensure_ascii=False,
            indent=4,
        )

def process_directory(
    input_dir,
    output_dir,
    dump_sentences_enabled=True,
    static_split=False,
    markdown_format=False,
    aggregate_whitespaces=False,
    verbose=True,
):
    """Process input directory recursively, aligning files in 'va/' and 'es/' subdirectories."""
    for root, dirs, files in os.walk(input_dir):
        if "va" in dirs and "es" in dirs:
            va_dir = os.path.join(root, "va")
            es_dir = os.path.join(root, "es")

            pivot_dir = root.replace(input_dir, output_dir)
            va_sentences_dir = os.path.join(pivot_dir, "va")
            es_sentences_dir = os.path.join(pivot_dir, "es")
            aligned_dir = os.path.join(pivot_dir, "aligned")

            for dirpath, _, filenames in os.walk(va_dir):
                for va_file in filenames:
                    va_file_path = os.path.join(dirpath, va_file)
                    relative_path = os.path.relpath(va_file_path, va_dir)
                    es_file_path = os.path.join(es_dir, relative_path)

                    aligned_file_path = os.path.join(
                        aligned_dir, os.path.splitext(relative_path)[0] + ".json"
                    )
                    va_sentences_path = os.path.join(va_sentences_dir, relative_path)
                    es_sentences_path = os.path.join(es_sentences_dir, relative_path)

                    if os.path.isfile(es_file_path):
                        os.makedirs(os.path.dirname(aligned_file_path), exist_ok=True)
                        if dump_sentences_enabled:
                            os.makedirs(
                                os.path.dirname(va_sentences_path), exist_ok=True
                            )
                            os.makedirs(
                                os.path.dirname(es_sentences_path), exist_ok=True
                            )
                        try:
                            main(
                                va_file_path,
                                es_file_path,
                                aligned_file_path,
                                va_sentences_path,
                                es_sentences_path,
                                dump_sentences_enabled,
                                static_split,
                                markdown_format,
                                aggregate_whitespaces,
                            )
                            if verbose:
                                print(
                                    f"Successfully aligned {va_file_path} and {es_file_path}: saved to {aligned_file_path}"
                                )
                            else:
                                print("✅", end="", flush=True)
                        except SentenceAlignmentError as e:
                            if verbose:
                                print(
                                    f"Error aligning {va_file_path} and {es_file_path}: {e}"
                                )
                            elif e.difference == 1:
                                print("🟨", end="", flush=True)
                            else:
                                print("❌", end="", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input_dir", help="Path to input directory")
    parser.add_argument("output_dir", help="Path to output directory")
    parser.add_argument(
        "--disable-dump",
        action="store_true",
        help="Disable dumping of split sentences to separate files",
    )
    parser.add_argument(
        "--static-split",
        action="store_true",
        help="Use static sentence splitting instead of spaCy",
    )
    parser.add_argument(
        "--markdown-format",
        action="store_true",
        help="Enable markdown format preprocessing",
    )
    parser.add_argument(
        "--aggregate-whitespaces",
        action="store_true",
        help="Aggregate whitespaces in the text",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output",
    )
    parser.add_argument(
        "--use-multilingual",
        action="store_true",
        help="Use multilingual model (xx_sent_ud_sm) for sentence splitting",
    )
    args = parser.parse_args()

    if not args.use_multilingual:
        nlp[ES] = spacy.load("es_dep_news_trf")  # Load Spanish tokenizer
        nlp[VA] = spacy.load("ca_core_news_trf")  # Load Valencian tokenizer
    else:
        nlp[ES] = nlp[VA] = spacy.load("xx_sent_ud_sm")  # Use multilingual model

    process_directory(
        args.input_dir,
        args.output_dir,
        not args.disable_dump,
        args.static_split,
        args.markdown_format,
        args.aggregate_whitespaces,
        args.verbose,
    )
