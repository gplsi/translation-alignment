python -m src.split "data/boua (md)/" "output/boua (md)/va-es-paragraph/" --lang0 va --lang1 es --use-alignment-embeddings --skip-aligned --disable-dump --target paragraph --static-split --markdown-format

################################
if [ $? -ne 0 ]; then          #
    exit 1                     #  [STOP ON ERROR]
fi                             #
################################

python -m src.filter_items "output/boua (md)/va-es-paragraph/" --lang0 va --lang1 es --enable-length --enable-ner --verbose --deprecated-json

################################
if [ $? -ne 0 ]; then          #
    exit 1                     #  [STOP ON ERROR]
fi                             #
################################

python -m src.dir2file "output/boua (md)/va-es-paragraph.length.ner" --lang0 va --lang1 es --format jsonl