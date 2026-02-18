python -m src.split "data/UJI (plain)/" "output/UJI (plain)/va-es-documents/" --lang0 va --lang1 es --skip-aligned --disable-dump --target document --static-split

################################
if [ $? -ne 0 ]; then          #
    exit 1                     #  [STOP ON ERROR]
fi                             #
################################

python -m src.dir2file "output/UJI (plain)/va-es-documents/" --lang0 va --lang1 es --format jsonl