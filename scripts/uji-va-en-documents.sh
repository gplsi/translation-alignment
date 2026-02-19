#!/bin/bash
#SBATCH --job-name=uji-va-en-documents                # Job name
#SBATCH --output=logs/uji-va-en-documents-[%j].out    # Standard output (stdout) file
#SBATCH --error=logs/uji-va-en-documents-[%j].err     # Standard error (stderr) file
#SBATCH --partition=titan                             # Cluster partition to use
#SBATCH --mem=32G                                     # Required RAM memory
#SBATCH --nodes=1                                     # Number of nodes
#SBATCH --cpus-per-task=1                             # Number of CPUs per task
#SBATCH --time=24:00:00                               # Maximum execution time (HH:MM:SS)


##################################################
if [ -n "$CONDA_PATH" ]; then                    #
    source "$CONDA_PATH/etc/profile.d/conda.sh"  # 
    conda activate alia-data-scripts             #
fi                                               #
##################################################

python -m src.split "data/UJI (plain)/" "output/UJI (plain)/va-en-documents/" --lang0 va --lang1 en --skip-aligned --disable-dump --target document --static-split

################################
if [ $? -ne 0 ]; then          #
    exit 1                     #  [STOP ON ERROR]
fi                             #
################################

python -m src.dir2file "output/UJI (plain)/va-en-documents/" --lang0 va --lang1 en --format jsonl

#-------------------------------------------------

echo "Job finished at $(date)"