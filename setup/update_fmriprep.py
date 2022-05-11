#!/bin/python3

"""
ABOUT THIS SCRIPT

We're running fmriprep on a rolling basis as
we obtain new participant data. This script identifies
subjects that have already been preprocessed, and does NOT
include them in the preprocessing script

Ian Richard Ferguson | SSNL
"""

# --- Imports
from bids import BIDSLayout
import os, sys
from datetime import datetime


# --- Helpers
def get_preprocessed(path_to_prep):
    """
    Parameters
        path_to_prep: str | Relative path to fmriprep output directory

    Returns
        List of preprocessed subjects
    """

    return [x.split('sub-')[1] for x in os.listdir(path_to_prep) 
            
            # We want directories only
            if os.path.isdir(x)
            
            # Redundant but excludes output HTML summaries
            if ".html" not in x]


def derive_subs_to_process(bids_path):
    """
    Compare all subjects with those already preprocessed

    Parameters
        bids_path: str | Relative path to BIDS project (top level)

    Returns
        List of subjects that require preprocessing
    """

    bids_project = BIDSLayout(bids_path)
    all_subjects = bids_project.get_subjects()
    
    path_to_fmriprep = os.path.join(bids_path, "derivatives/fmriprep")
    preprocessed = get_preprocessed(path_to_prep=path_to_fmriprep)

    return [x for x in all_subjects if x not in preprocessed]


def write_locally(new_subjects):
    """
    This function writes a local text file optimized to copy
    and paste directly into the fmriprep script

    Parameters
        new_subjects: list | List of subjects that have not been preprocessed
    """

    formatted = " ".join(new_subjects)
    today = datetime.today().strftime("%Y_%b_%d")

    filename = f"{today}_fmriprep.txt"

    with open(filename, "w") as log:
        log.write("INSTRUCTIONS\nPaste the output below directly into your Job Script\n\n")
        log.write(f"({formatted})")


def main():

    try:
        bids_path = sys.argv[1]
    except Exception as e:
        raise e

    new_subjects = derive_subs_to_process(bids_path=bids_path)

    if len(new_subjects) > 0:
        write_locally(new_subjects=new_subjects)
        print("\n** File successfully saved! **\n")
    else:
        print("\n** No subjects to preprocess! **\n")


if __name__ == "__main__":
    main()