#!/bin/bash
#SBATCH --job-name=uji-va-es-documents                # Job name
#SBATCH --output=logs/uji-va-es-documents-[%j].out    # Standard output (stdout) file
#SBATCH --error=logs/uji-va-es-documents-[%j].err     # Standard error (stderr) file
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

python -m src.split "data/UJI (plain)/" "output/UJI (plain)/va-es-documents/" --lang0 va --lang1 es --skip-aligned --disable-dump --target document --static-split

################################
if [ $? -ne 0 ]; then          #
    exit 1                     #  [STOP ON ERROR]
fi                             #
################################

python -m src.dir2file "output/UJI (plain)/va-es-documents/" --lang0 va --lang1 es --format jsonl

#-------------------------------------------------

echo "Job finished at $(date)"