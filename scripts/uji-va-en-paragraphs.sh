python -m src.split "data/UJI (plain)/" "output/UJI-VA-EN-PARAGRAPH (plain)/" --lang0 va --lang1 en --use-alignment-embeddings --skip-aligned --disable-dump --target paragraph --static-split
if [ $? -ne 0 ]; then
    exit 1
fi

python -m src.filter_items "output/UJI-VA-EN-PARAGRAPH (plain)/" "output/UJI-VA-EN-PARAGRAPH (plain aligned-and-filtered)" --lang0 va --lang1 en
if [ $? -ne 0 ]; then
    exit 1
fi

python -m src.dir2file "output/UJI-VA-EN-PARAGRAPH (plain aligned-and-filtered)" va-en-paragraphs.jsonl --add-partitions --lang0 va --lang1 en --format jsonl
if [ $? -ne 0 ]; then
    exit 1
fi