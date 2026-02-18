python -m src.split "data/UJI (plain)/" "output/UJI (plain)/va-en-sentence/" --lang0 va --lang1 en --use-alignment-embeddings --skip-aligned --disable-dump --target sentence --static-split

################################
if [ $? -ne 0 ]; then          #
    exit 1                     #  [STOP ON ERROR]
fi                             #
################################

python -m src.filter_items "output/UJI (plain)/va-en-sentence/" --lang0 va --lang1 en --enable-length --enable-ner --verbose

################################
if [ $? -ne 0 ]; then          #
    exit 1                     #  [STOP ON ERROR]
fi                             #
################################

python -m src.dir2file "output/UJI (plain)/va-en-sentence.length.ner" --lang0 va --lang1 en --format jsonl