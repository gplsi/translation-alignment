import spacy
import argparse
import os
import json
import re
import markdown
from bs4 import BeautifulSoup
from sentence_transformers import SentenceTransformer, util
from functools import lru_cache


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


def align_sentences(sentences0, sentences1):
    """Naive alignment: 1-to-1, truncate to shortest."""
    if len(sentences0) != len(sentences1):
        difference = abs(len(sentences0) - len(sentences1))
        raise SentenceAlignmentError(
            f"Sentence count mismatch: Spanish: {len(sentences0)}, Valencian: {len(sentences1)}",
            difference,
        )
    return list(zip(sentences0, sentences1))


@lru_cache(maxsize=1)
def get_model(model_name):
    """Get the SentenceTransformer model with caching."""
    try:
        model = SentenceTransformer(model_name)
        return model
    except Exception as e:
        raise ValueError(f"Failed to load model '{model_name}': {e}")


def align_sentences_with_embeddings(
    sentences0,
    sentences1,
    model_name,
    threshold=0.7,
    loose=False,
    attempts=5,
):
    """Align sentences using embeddings and cosine similarity."""

    if not sentences0 or not sentences1:
        raise SentenceAlignmentError(
            "One or both sentence lists are empty.", len(sentences0) + len(sentences1)
        )

    model = get_model(model_name)
    sentences = [sentences0, sentences1]

    @lru_cache(maxsize=6)
    def get_embedding(group, pivot):
        """Get the embedding for a sentence, caching results."""
        return model.encode(sentences[group][pivot], convert_to_tensor=True)

    pivot0 = 0
    pivot1 = 0
    aligned_sentences = []

    while pivot0 < len(sentences0) and pivot1 < len(sentences1):
        embedding0 = get_embedding(0, pivot0)
        embedding1 = get_embedding(1, pivot1)
        similarity = util.cos_sim(embedding0, embedding1)

        if similarity.item() >= threshold:
            aligned_sentences.append((sentences0[pivot0], sentences1[pivot1]))
            pivot0 += 1
            pivot1 += 1
        else:
            similarities = [
                (
                    similarity.item(),
                    pivot0 + 1,
                    pivot1 + 1,
                    sentences0[pivot0],
                    sentences1[pivot1],
                )
            ]

            if pivot0 + 1 < len(sentences0):
                candidate0 = sentences0[pivot0 + 1]
                candidate0_embedding = get_embedding(0, pivot0 + 1)
                candidate0_similarity = util.cos_sim(candidate0_embedding, embedding1)
                if candidate0_similarity.item() >= threshold:
                    aligned_sentences.append((candidate0, sentences1[pivot1]))
                    pivot0 += 2
                    pivot1 += 1
                    continue
                similarities.append(
                    (
                        candidate0_similarity.item(),
                        pivot0 + 2,
                        pivot1 + 1,
                        candidate0,
                        sentences1[pivot1],
                    )
                )

            if pivot1 + 1 < len(sentences1):
                candidate1 = sentences1[pivot1 + 1]
                candidate1_embedding = get_embedding(1, pivot1 + 1)
                candidate1_similarity = util.cos_sim(embedding0, candidate1_embedding)
                if candidate1_similarity.item() >= threshold:
                    aligned_sentences.append((sentences0[pivot0], candidate1))
                    pivot0 += 1
                    pivot1 += 2
                    continue
                similarities.append(
                    (
                        candidate1_similarity.item(),
                        pivot0 + 1,
                        pivot1 + 2,
                        sentences0[pivot0],
                        candidate1,
                    )
                )

            if loose:
                best_similarity, pivot0, pivot1, sentence0, sentence1 = max(
                    similarities,
                    key=lambda x: x[0],
                )
                aligned_sentences.append((sentence0, sentence1))
            elif attempts > 0:
                attempts -= 1
                pivot0 += 1
                pivot1 += 1
            else:
                raise SentenceAlignmentError(
                    "No suitable alignment found.", float("inf")
                )

    return aligned_sentences


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
    alignment_model_name=None,
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

    if alignment_model_name is None:
        aligned = align_sentences(valencian_sentences, spanish_sentences)
    else:
        aligned = align_sentences_with_embeddings(
            valencian_sentences, spanish_sentences, alignment_model_name
        )

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
    alignment_model_name=None,
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
                                alignment_model_name,
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
    parser.add_argument(
        "--use-alignment-embeddings",
        action="store_true",
        help="Use embeddings-based alignment instead of naive alignment",
    )
    parser.add_argument(
        "--alignment-model-name",
        default="distiluse-base-multilingual-cased-v2",
        help="Model name for embeddings-based alignment (default: distiluse-base-multilingual-cased-v2)",
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
        args.alignment_model_name if args.use_alignment_embeddings else None,
    )
