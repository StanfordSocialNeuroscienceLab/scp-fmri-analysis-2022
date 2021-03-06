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

Ian Richard Ferguson | Stanford University
"""

# --- Imports
import warnings
warnings.filterwarnings('ignore')

import os, sys, shutil, glob
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


def get_session_id(x):
      """
      This function isolates the session ID if it exists

      Parameters
            x: str | Any incoming relative path

      Returns
            Clean string with ses- tag removed
      """

      if "ses-" in x:
            return [k.strip() for k in x.split("_") if "ses" in k][0]

      return None


def move_files_up(path_to_sub_id):
      """
      This function recursively loops through our subdirectories
      and moves files up from session subdirectories to the highest level

      Parameters
            path_to_sub_id: str | Relative path to subject BIDS data
      """

      # Session ID, e.g., ses-12345
      try:
            session_id = [x for x in os.listdir(path_to_sub_id) if "ses-" in x][0]
            directory_formatted = False
      except:
            directory_formatted = True

      # Directory has not been re-formatted, we'll do that here
      if not directory_formatted:
            # Loop through subdirectories
            for subdir in ["anat", "fmap", "func"]:

                  # Nested subdirs
                  old = os.path.join(path_to_sub_id, session_id, subdir)

                  # Target subdirs
                  new = os.path.join(path_to_sub_id, subdir)

                  # Move all files up out of sesion subdirectory
                  for file in os.listdir(old):
                        shutil.move(os.path.join(old, file), new)

            # Removes old directory, which should be empty
            if session_id is not None:
                  shutil.rmtree(os.path.join(path_to_sub_id, session_id))


def rename_all_files(path_to_sub_id):
      """
      This function iteratively loops through all files
      and strips out the session ID if it exists
      """

      for file in glob.glob(os.path.join(path_to_sub_id, "**/*"), recursive=True):

            session_id = get_session_id(file)

            if session_id is not None:

                  new_filename = file.replace(f"{session_id}_", "")

                  os.rename(file, new_filename)


def run_single_subject(subject_id, bids_path, log):
      """
      Loops through our functions above and applies them to a given subject

      Parameters
            subject_id: str | Subject's identifier in the BIDS project
            bids_path: str | Relative path to BIDS project
            log: I/O stream | Text file opened outside of this function
      """

      # Relative path to subject's BIDS data
      filepath = os.path.join(bids_path, f"sub-{subject_id}")
      log.write(f"\n** sub-{subject_id} **\n")

      # -- Create new subdirectories
      try:
            create_correct_subdirs(filepath)
            log.write("Created subdirs:\t\tSuccessful\n")
      except Exception as e:
            log.write(f"Created subdirs:\t\t{e}\n")

      # -- Move files up from session subdirectory
      try:
            move_files_up(filepath)
            log.write("Files moved up:\t\tSuccessful\n")
      except Exception as e:
            log.write(f"Files moved up:\t\t{e}\n")

      # -- Strip session identifier from all files
      try:
            rename_all_files(filepath)
            log.write("Renamed files:\t\tSuccessful\n")
      except Exception as e:
            log.write(f"Renamed files:\t\t{e}\n")
      

def main():

      # Relative path to BIDS project
      bids_root = sys.argv[1]

      # Subject identifier or ALL
      subject = sys.argv[2]

      # Open text file to log any issues
      with open("./directory_hierarchy.txt", "w") as log:

            # Accept ALL as input to run every subject
            if subject.upper() == "ALL":

                  all_subjects = BIDSLayout(bids_root).get_subjects()

                  for sub in tqdm(all_subjects):
                        run_single_subject(sub, 
                                           bids_root, 
                                           log)

            # Run single subject through our script
            else:
                  run_single_subject(subject, 
                                     bids_root, 
                                     log)


if __name__ == "__main__":
      main()