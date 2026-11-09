#!/bin/bash
#SBATCH --job-name=postprocess-dogv-va-es-documents               # Job name
#SBATCH --output=logs/postprocess-dogv-va-es-documents-[%j].out   # Standard output (stdout) file
#SBATCH --error=logs/postprocess-dogv-va-es-documents-[%j].err    # Standard error (stderr) file
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

python -m src.crop_dogv_documents "output/dogv (md)/va-es-documents.curated.jsonl"

#-------------------------------------------------

echo "Job finished at $(date)"