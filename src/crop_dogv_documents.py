import argparse
import json
import re
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

VA_START_REGEX = r"\n:[^\n]*\n\n"
VA_END_REGEX = r"\n\n\n\nDescarregar\sel\sdocument\samb\sformat\sPDF\n"
VA_ONLY_PDF_REGEX = (
    r"\n[^\n]*Aquest\sdocument\sestà\sdisponible\súnicament\sen\sformat\sPDF.\n"
)
ES_START_REGEX = VA_START_REGEX
ES_END_REGEX = r"\n\n\n\nDescargar\sel\sdocumento\sen\sformato\sPDF\n"
ES_ONLY_PDF_REGEX = (
    r"\n[^\n]*Este\sdocumento\sestá\sdisponible\súnicamente\sen\sformato\sPDF.\n"
)


class CropError(Exception):
    pass


class OverlapCropError(CropError):
    def __init__(self, start_match, end_match, text, line_number, language):
        self.start_match = start_match
        self.end_match = end_match
        self.text = text
        self.line_number = line_number
        self.language = language

    def __str__(self):
        return (
            f"Line {self.line_number}: regex matches overlap or are out of order for '{self.language}'\n"
            + "[BEGIN-START]\n"
            + self.text[: self.start_match.end()]
            + "\n[BEGIN-END]\n"
            + self.text[self.start_match.end() : self.end_match.start()]
            + "\n[END-START]\n"
            + self.text[self.end_match.start() :]
            + "\n[END-END]"
        )


class MissingMatchError(CropError):
    def __init__(self, pattern_type, language, line_number):
        self.pattern_type = pattern_type
        self.language = language
        self.line_number = line_number

    def __str__(self):
        return f"Line {self.line_number}: {self.pattern_type} regex did not match '{self.language}'"


class OnlyPDFDocumentError(CropError):
    def __init__(self, language, line_number):
        self.language = language
        self.line_number = line_number

    def __str__(self):
        return f"Line {self.line_number}: '{self.language}' states that the documnent is only available as a PDF document"


def crop_text(text, start_pattern, end_pattern, only_pdf, language, line_number):
    if not isinstance(text, str):
        raise ValueError(f"Line {line_number}: '{language}' must contain a string")

    if only_pdf.search(text):
        raise OnlyPDFDocumentError(language, line_number)

    start_matches = list(start_pattern.finditer(text))
    end_matches = list(end_pattern.finditer(text))
    if not start_matches:
        raise MissingMatchError("start", language, line_number)
    if not end_matches:
        raise MissingMatchError("end", language, line_number)
    start_match = start_matches[-1]
    end_match = end_matches[0]
    if start_match.end() > end_match.start():
        raise OverlapCropError(start_match, end_match, text, line_number, language)

    return text[start_match.end() : end_match.start()]


def main():
    parser = argparse.ArgumentParser(
        description="Crop VA and ES text using the regex constants defined in this script."
    )
    parser.add_argument("input_path", type=Path, help="Input JSONL file")
    args = parser.parse_args()

    patterns = {
        "VA": (
            re.compile(VA_START_REGEX),
            re.compile(VA_END_REGEX),
            re.compile(VA_ONLY_PDF_REGEX),
        ),
        "ES": (
            re.compile(ES_START_REGEX),
            re.compile(ES_END_REGEX),
            re.compile(ES_ONLY_PDF_REGEX),
        ),
    }
    output_path = args.input_path.with_name(f"{args.input_path.stem}.cropped.jsonl")

    with args.input_path.open("r", encoding="utf-8") as source, output_path.open(
        "w", encoding="utf-8"
    ) as destination:
        for line_number, line in enumerate(source, start=1):
            if not line.strip():
                continue

            try:
                record = json.loads(line)
                for language, (
                    start_pattern,
                    end_pattern,
                    only_pdf,
                ) in patterns.items():
                    if language in record:
                        record[language] = crop_text(
                            record[language],
                            start_pattern,
                            end_pattern,
                            only_pdf,
                            language,
                            line_number,
                        )
                destination.write(json.dumps(record, ensure_ascii=False) + "\n")
            except CropError as e:
                logging.warning(f"Skipping line {line_number} due to cropping error: {type(e).__name__}.")
                logging.error(e)
                continue

    logging.info(f"Cropped JSONL written to {output_path}")


if __name__ == "__main__":
    main()
