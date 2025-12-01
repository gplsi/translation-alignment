python -m src.split "data/UJI (plain)/" "output/UJI-VA-ES-PARAGRAPH (plain)/" --lang0 va --lang1 es --use-alignment-embeddings --skip-aligned --disable-dump --target paragraph --static-split
if [ $? -ne 0 ]; then
    exit 1
fi

python -m src.filter_items "output/UJI-VA-ES-PARAGRAPH (plain)/" "output/UJI-VA-ES-PARAGRAPH (plain aligned-and-filtered)" --lang0 va --lang1 es
if [ $? -ne 0 ]; then
    exit 1
fi

python -m src.dir2file "output/UJI-VA-ES-PARAGRAPH (plain aligned-and-filtered)" va-eS-paragraphs.jsonl --add-partitions --lang0 va --lang1 es --format jsonl
if [ $? -ne 0 ]; then
    exit 1
fi