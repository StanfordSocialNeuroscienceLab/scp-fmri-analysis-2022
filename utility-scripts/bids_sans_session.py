#!/bin/python3

"""
ABOUT THIS SCRIPT

We have single-session data acqusistion in this project; as a 
result, we do not need the BIDS session label included in our
data at this time. This script iteratively moves and renames
all files in order to fit our specs

This script performs the following operations:
    * Creates anat/func/fmap directories if they do not exist
    * Moves all files from the ses- subdirectory to the higher-level BIDS directory
    * Rename each file to strip out the ses- tag

IRF | SSNL
"""

# --- Imports
import warnings
warnings.filterwarnings('ignore')

import os, pathlib, sys, shutil, glob
from tqdm import tqdm
from bids import BIDSLayout


# --- Helpers
def create_correct_subdirs(path_to_sub_id):
    """
    This function sets the table for us to move our nested 
    files up one level

    Parameters
        path_to_sub_id: str | Relative path to subject BIDS data
    """

    for k in ["anat", "fmap", "func"]:

        # If the subject doesn't have a subdirectory, we'll create it
        if not os.path.exists(os.path.join(path_to_sub_id, k)):
            os.mkdir(os.path.join(path_to_sub_id, k))


def isolate_session_id(path_to_sub_id):
    """
    Utility function to help us identify the session ID for a given subject.
    There should only be one session ID per subject so we hard code the first
    index as our value of interest

    Parameters
        path_to_sub_id: str | Relative path to subject BIDS data

    Return
        Session identifier as a string
    """

    return [x for x in os.listdir(path_to_sub_id) if "ses-" in x][0]


def move_files_up(path_to_sub_id):
    """
    This function recursively loops through our subdirectories
    and moves files up from session subdirectories to the highest level

    Parameters
        path_to_sub_id: str | Relative path to subject BIDS data
    """

    create_correct_subdirs(path_to_sub_id)

    # Session ID, e.g., ses-12345
    session_id = isolate_session_id(path_to_sub_id)


    # Loop through subdirectories
    for subdir in ["anat", "fmap", "func"]:

        # Nested subdirs
        old = os.path.join(path_to_sub_id, session_id, subdir)
        
        # Target subdirs
        new = os.path.join(path_to_sub_id, subdir)

        """
        For every file in the 'old' 
        """

        for file in os.listdir(old):
            shutil.move(os.path.join(old, file), new)

    #shutil.rmtree(os.path.join(path_to_sub_id, session_id))


def rename_all_files(path_to_sub_id):
    """
    This function loops through our recently moved files and cleans up
    the filenames by stripping out the session IDs

    Parameters
        path_to_sub_id: str | Relative path to subject BIDS data
    """

    # Session ID, e.g., ses-12345
    session_id = isolate_session_id(path_to_sub_id)

    def get_new_filename(old):
        """
        Parameters
            old: str | File path to rename (includes ses-)
        """

        # This avoids double underscores
        inclusive_replacement = session_id + "_"

        return old.replace(inclusive_replacement, "")


    # Loop through subdirectories
    for subdir in ["anat", "fmap", "func"]:

        # For every file in each subdirectory
        for file in glob.glob(os.path.join(path_to_sub_id, subdir, "**/*"), recursive=True):
            
            # New filename (stripped out ses- IDs)
            new_name = get_new_filename(file)

            # Rename file
            os.rename(file, new_name)


def run_single_subject(sub_id, bids_path="./bids"):
    """
    Applies all of the helper functions outlined above

    Parameters
        sub_id: str | Individual subject ID (e.g., 12345)
        bids_path: str | Relative path to the full BIDS data set
    """

    # Path to single subject's BIDS data
    subject_path = os.path.join(bids_path, f"sub-{sub_id}")

    # Move files from nested session subdirectory
    move_files_up(subject_path)

    # Rename files to strip out ses
    rename_all_files(subject_path)


def main():

    # User-supplied path to BIDS data
    bids_path = sys.argv[1]

    # Instantiate BIDSLayout object for easy looping
    bids = BIDSLayout(bids_path)

    # Loop through all subjects and apply the run_single_subject function
    for sub in tqdm(bids.get_subjects()):
        run_single_subject(sub_id=sub, bids_path=bids_path)


# --- Main
if __name__ == "__main__":
    main()