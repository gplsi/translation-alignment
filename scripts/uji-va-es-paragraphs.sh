python -m src.split "data/UJI (plain)/" "output/UJI (plain)/va-es-paragraph/" --lang0 va --lang1 es --use-alignment-embeddings --skip-aligned --disable-dump --target paragraph --static-split
if [ $? -ne 0 ]; then
    exit 1
fi

python -m src.filter_items "output/UJI (plain)/va-es-paragraph/" --lang0 va --lang1 es --enable-length --enable-ner --verbose
if [ $? -ne 0 ]; then
    exit 1
fi

python -m src.dir2file "output/UJI (plain)/va-es-paragraph.length.ner" --lang0 va --lang1 es --format jsonl
if [ $? -ne 0 ]; then
    exit 1
fi