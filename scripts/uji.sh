python -m src.split "data/UJI (plain)/" "output/UJI (plain)/" --lang0 va --lang1 en --use-alignment-embeddings --skip-aligned --disable-dump


python -m src.filter_items "output/UJI (plain)/" "output/UJI (plain aligned-and-filtered)" --lang0 va --lang1 en

find "output/UJI (plain aligned-and-filtered)/" -type f -name '*.jsonl' -exec cat {} + > "output/UJI (plain aligned-and-filtered).jsonl"