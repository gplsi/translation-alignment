#!/bin/bash
#SBATCH --job-name=amic_paralelo-va-es-paragraphs               # Job name
#SBATCH --output=logs/amic_paralelo-va-es-paragraphs-[%j].out   # Standard output (stdout) file
#SBATCH --error=logs/amic_paralelo-va-es-paragraphs-[%j].err    # Standard error (stderr) file
#SBATCH --partition=titan                                       # Cluster partition to use
#SBATCH --mem=32G                                               # Required RAM memory
#SBATCH --nodes=1                                               # Number of nodes
#SBATCH --cpus-per-task=1                                      # Number of CPUs per task
#SBATCH --time=24:00:00                                         # Maximum execution time (HH:MM:SS)


##################################################
if [ -n "$CONDA_PATH" ]; then                    #
    source "$CONDA_PATH/etc/profile.d/conda.sh"  # 
    conda activate alia-data-scripts             #
fi                                               #
##################################################

python -m src.split "data/amic-paralelo (plain)/" "output/amic-paralelo (plain)/va-es-paragraph/" --lang0 va --lang1 es --use-alignment-embeddings --skip-aligned --disable-dump --target paragraph --static-split

################################
if [ $? -ne 0 ]; then          #
    exit 1                     #  [STOP ON ERROR]
fi                             #
################################

python -m src.filter_items "output/amic-paralelo (plain)/va-es-paragraph/" --lang0 va --lang1 es --enable-length --enable-ner --verbose

################################
if [ $? -ne 0 ]; then          #
    exit 1                     #  [STOP ON ERROR]
fi                             #
################################

python -m src.dir2file "output/amic-paralelo (plain)/va-es-paragraph.length.ner" --lang0 va --lang1 es --format jsonl

#-------------------------------------------------

echo "Job finished at $(date)"