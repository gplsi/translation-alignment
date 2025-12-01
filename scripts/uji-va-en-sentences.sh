python -m src.split "data/UJI (plain)/" "output/UJI-VA-EN (plain)/" --lang0 va --lang1 en --use-alignment-embeddings --skip-aligned --disable-dump

python -m src.filter_items "output/UJI-VA-EN (plain)/" "output/UJI-VA-EN (plain aligned-and-filtered)" --lang0 va --lang1 en

python -m src.dir2file "output/UJI-VA-EN (plain aligned-and-filtered)" va-en.jsonl --add-partitions --lang0 va --lang1 en --format jsonl