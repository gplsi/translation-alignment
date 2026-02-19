#!/bin/bash
#SBATCH --job-name=boua-va-es-sentences               # Job name
#SBATCH --output=logs/boua-va-es-sentences-[%j].out   # Standard output (stdout) file
#SBATCH --error=logs/boua-va-es-sentences-[%j].err    # Standard error (stderr) file
#SBATCH --partition=titan                             # Cluster partition to use
#SBATCH --mem=32G                                     # Required RAM memory
#SBATCH --nodes=1                                     # Number of nodes
#SBATCH --cpus-per-task=4                             # Number of CPUs per task
#SBATCH --time=24:00:00                               # Maximum execution time (HH:MM:SS)


##################################################
if [ -n "$CONDA_PATH" ]; then                    #
    source "$CONDA_PATH/etc/profile.d/conda.sh"  # 
    conda activate alia-data-scripts             #
fi                                               #
##################################################

python -m src.split "data/boua (md)/" "output/boua (md)/va-es-sentence/" --lang0 va --lang1 es --use-alignment-embeddings --skip-aligned --disable-dump --target sentence --static-split --markdown-format

################################
if [ $? -ne 0 ]; then          #
    exit 1                     #  [STOP ON ERROR]
fi                             #
################################

python -m src.filter_items "output/boua (md)/va-es-sentence/" --lang0 va --lang1 es --enable-length --enable-ner --verbose

################################
if [ $? -ne 0 ]; then          #
    exit 1                     #  [STOP ON ERROR]
fi                             #
################################

python -m src.dir2file "output/boua (md)/va-es-sentence.length.ner" --lang0 va --lang1 es --format jsonl

#-------------------------------------------------

echo "Job finished at $(date)"