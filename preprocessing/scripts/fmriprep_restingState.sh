#!/bin/bash

# FMRIPREP single subject preprocessing script
# This script is fed subject information and deployed via Job-Script.sh
#
# Ian Richard Ferguson | Stanford University

# === User input parameters ===
SUBJ=$1                                                                         # Read in from command line
THREADS=16
MEM=30
DUMMY_SCANS=2

BIDS_ROOT="/oak/stanford/groups/jzaki/scp_2022/bids"                            # Path to BIDS data
IMAGE=/"oak/stanford/groups/jzaki/zaki_images/fmriprep-20.2.1.simg"             # Path to singularity image
SURFER="/oak/stanford/groups/jzaki/zaki_images/FS_LICENSE.txt"                  # Path to FreeSurfer license
TFLOW="$HOME/.cache/templateflow"                                               # Path to templateflow sub-dir
mkdir -p $TFLOW                                                                 # Make templateflow dir if it doesn't exist


# === Run singularity script ===
singularity run --home $HOME --cleanenv $IMAGE          \
  $BIDS_ROOT $BIDS_ROOT/derivatives                     \
  participant                                           \
  --participant-label $SUBJ                             \
  --task-id rest                                        \                
  --md-only-boilerplate                                 \
  --fs-license-file $SURFER                             \
  --output-spaces                                       \
      MNI152NLin2009cAsym:res-2                         \
      MNI152NLin6Asym:res-2                             \
  --nthreads $THREADS                                   \
  --stop-on-first-crash                                 \
  --mem_mb $MEM                                         \
  --dummy-scans $DUMMY_SCANS
