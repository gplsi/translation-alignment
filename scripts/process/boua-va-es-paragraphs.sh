#!/bin/bash
#SBATCH --job-name=boua-va-es-paragraphs              # Job name
#SBATCH --output=logs/boua-va-es-paragraphs-[%j].out  # Standard output (stdout) file
#SBATCH --error=logs/boua-va-es-paragraphs-[%j].err   # Standard error (stderr) file
#SBATCH --partition=dgx                               # Cluster partition to use
#SBATCH --mem=32G                                     # Required RAM memory
#SBATCH --nodes=1                                     # Number of nodes
#SBATCH --cpus-per-task=2                             # Number of CPUs per task
#SBATCH --time=48:00:00                               # Maximum execution time (HH:MM:SS)


##################################################
if [ -n "$CONDA_PATH" ]; then                    #
    source "$CONDA_PATH/etc/profile.d/conda.sh"  # 
    conda activate alia-data-scripts             #
fi                                               #
##################################################

python -m src.split "data/boua (md)/" "output/boua (md)/va-es-paragraph/" --lang0 va --lang1 es --use-alignment-embeddings --skip-aligned --disable-dump --target paragraph --static-split --markdown-format

################################
if [ $? -ne 0 ]; then          #
    exit 1                     #  [STOP ON ERROR]
fi                             #
################################

python -m src.filter_items "output/boua (md)/va-es-paragraph/" --lang0 va --lang1 es --enable-length --verbose

################################
if [ $? -ne 0 ]; then          #
    exit 1                     #  [STOP ON ERROR]
fi                             #
################################

python -m src.dir2file "output/boua (md)/va-es-paragraph.length" --lang0 va --lang1 es --format jsonl

#-------------------------------------------------

echo "Job finished at $(date)"