python -m src.split "data/dogv (md)/" "output/dogv (md)/va-es-paragraph/" --lang0 va --lang1 es --use-alignment-embeddings --skip-aligned --disable-dump --target paragraph --static-split --markdown-format

################################
if [ $? -ne 0 ]; then          #
    exit 1                     #  [STOP ON ERROR]
fi                             #
################################

python -m src.filter_items "output/dogv (md)/va-es-paragraph/" --lang0 va --lang1 es --enable-length --enable-ner --verbose --deprecated-json

################################
if [ $? -ne 0 ]; then          #
    exit 1                     #  [STOP ON ERROR]
fi                             #
################################

python -m src.dir2file "output/dogv (md)/va-es-paragraph.length.ner" --lang0 va --lang1 es --format jsonl