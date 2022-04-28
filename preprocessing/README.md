# Preprocessing with `fmriprep`

We are running `fmriprep v20.2.1` as of April 2022. There is no need to call the single subject script directly, run `bash Job-Script.sh` in your HPC environment to iteratively schedule single-subject scripts in SLURM. Running these in parallel is faster and less computationally demanding.

See the `update_fmriprep.py` script in the Utilities sub-directory to update the Job Script with subjects who have not been preprocessed.