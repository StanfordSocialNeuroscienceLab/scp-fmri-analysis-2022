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

import os, pathlib, sys, shutil, glob, json
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

    # Removes old directory, which should be empty
    shutil.rmtree(os.path.join(path_to_sub_id, session_id))


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


def cleanup_fmap(path_to_sub_id):
    """
    This function accomplishes the following tasks:
        * Determines which file set is MAGNITUDE and which file set is FIELDMAP
        * Renames both sets appropriately (while removing any lingering ses- tags)
        * Updates INTENDEDFOR fields for all JSON files

    NOTE: This function should be run last, after all directory reorganizing has
    already been taken care of

    Parameters
        path_to_sub_id: str | Relative path to our subject's data
        sub_id: str | Participant identifier in BIDS project
    """

    # ==== Renaming magnitude files ====
    def isolate_fieldmap(fmap_path):
        """
        This function determines which file set is the FIELDMAP and which
        file set is the MAGNITUDE
        """

        # Loop through relevant JSON files
        for path in tqdm(glob.glob(os.path.join(fmap_path, "**/*.json"), recursive=True)):
            
            # Read in file as a dictionary
            with open(path) as incoming:
                temp_data = json.load(incoming)

                # Determine if file is FIELDMAP or MAGNITUDE
                if 'fieldmap' in temp_data['fslhd']['filename']:

                    # Return file type agnostic identifier
                    return path.split('/')[-1].split('.json')[0]
                else:
                    continue

        raise OSError("No fieldmap identified")

    # Relative path to fmap subdirectory
    fmap_path = os.path.join(path_to_sub_id, "fmap")

    # Isolate fieldmap key
    fieldmap_key = isolate_fieldmap(fmap_path=fmap_path)

    # Magnitude key is the same convention with one word changed
    magnitude_key = fieldmap_key.replace("fieldmap", "magnitude")

    # Loop through ALL fmap files
    for file in glob.glob(os.path.join(fmap_path, "**/*"), recursive=True):
        
        # Skip over actual fieldmap files
        if fieldmap_key in file:
            continue

        # Create file type specific filenames
        if ".json" in file:
            new_filename = os.path.join(fmap_path, f"{magnitude_key}.json")
        elif ".nii.gz" in file:
            new_filename = os.path.join(fmap_path, f"{magnitude_key}.nii.gz")

        # Rename magnitude files
        os.rename(file, new_filename)


    # ==== Updated `IntendedFor` keys ===
    def isolate_session(incoming_DICT):
        """
        This function isolates the session ID for each subject
        """

        return [x for x in incoming_DICT['IntendedFor'][0].split('/')[-1].split('_') if 'ses-' in x][0]


    def update_field(incoming_JSON):
        """
        This function iteratively updates the IntendedFor fields in all JSON files
        """

        # Read in JSON as dictionary object
        with open(incoming_JSON) as incoming:
            data = json.load(incoming)

        # Get session ID
        session_label = isolate_session(incoming_DICT=data)

        # Update IntendedFor key with list comprehension
        data['IntendedFor'] = [x.replace(session_label, '').replace('__', '_')[1:]
                              for x in data['IntendedFor']]

        # Save JSON to fmap directory
        with open(incoming_JSON, "w") as outgoing:
            json.dump(data, outgoing, indent=5)


    def rewrite_metadata(fmap_path):
        """
        This function wraps the helpers above to seamlessly update
        the IntendedFor fields in all JSON files per subject
        """

        for file in glob.glob(os.path.join(fmap_path, "**/*.json"), recursive=True):
            update_field(file)


    # Run wrapper
    rewrite_metadata(fmap_path=fmap_path)

    
def run_single_subject(sub_id, bids_path="./bids"):
    """
    Applies all of the helper functions outlined above

    Parameters
        sub_id: str | Individual subject ID (e.g., 12345)
        bids_path: str | Relative path to the full BIDS data set
    """

    # Path to single subject's BIDS data
    subject_path = os.path.join(bids_path, f"sub-{sub_id}")

    try:
        # Move files from nested session subdirectory
        move_files_up(path_to_sub_id=subject_path)
    except Exception as e:
        print(f"\nsub-{sub_id}:\t\t{e}")

    # Rename files to strip out ses
    try:
        rename_all_files(path_to_sub_id=subject_path)
    except Exception as e:
        print(f"sub-{sub_id}:\t\t{e}")

    # Update fieldmap info
    try:
        cleanup_fmap(path_to_sub_id=subject_path)
    except Exception as e:
        print(f"sub-{sub_id}:\t\t{e}")


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