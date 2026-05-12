#!/bin/bash
#SBATCH --job-name=uv-va-en-documents                # Job name
#SBATCH --output=logs/uv-va-en-documents-[%j].out    # Standard output (stdout) file
#SBATCH --error=logs/uv-va-en-documents-[%j].err     # Standard error (stderr) file
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

python -m src.split "data/UV (plain)/" "output/UV (plain)/va-en-documents/" --lang0 va --lang1 en --skip-aligned --disable-dump --target document --static-split

################################
if [ $? -ne 0 ]; then          #
    exit 1                     #  [STOP ON ERROR]
fi                             #
################################

python -m src.dir2file "output/UV (plain)/va-en-documents/" --lang0 va --lang1 en --format jsonl

#-------------------------------------------------

echo "Job finished at $(date)"