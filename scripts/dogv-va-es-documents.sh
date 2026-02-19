#!/bin/bash
#SBATCH --job-name=dogv-va-es-documents               # Job name
#SBATCH --output=logs/dogv-va-es-documents-[%j].out   # Standard output (stdout) file
#SBATCH --error=logs/dogv-va-es-documents-[%j].err    # Standard error (stderr) file
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

python -m src.split "data/dogv (md)/" "output/dogv (md)/va-es-documents/" --lang0 va --lang1 es --skip-aligned --disable-dump --target document --static-split

################################
if [ $? -ne 0 ]; then          #
    exit 1                     #  [STOP ON ERROR]
fi                             #
################################

python -m src.dir2file "output/dogv (md)/va-es-documents/" --lang0 va --lang1 es --format jsonl

#-------------------------------------------------

echo "Job finished at $(date)"