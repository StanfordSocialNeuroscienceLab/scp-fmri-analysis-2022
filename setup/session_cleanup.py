#!/bin/python3

"""
ABOUT THIS SCRIPT

This is the second script run in our pre-fmripep
pipeline. It performs the following operations:

      * Confirms naming conventions have session ID removed
      * Isolates JSON files in fmap/ subdirectory
      * Updates the IntendedFor fields if necessary

Ian Richard Ferguson | Stanford University
"""


# --- Imports
import warnings
warnings.filterwarnings('ignore')

import os, pathlib, sys, shutil, glob, json
from tqdm import tqdm
from bids import BIDSLayout


# --- Helpers
def get_session_id(incoming):
      """
      Simple helper to isolate a session ID if
      exists in an oncoming string

      Parameters
            incoming: str | Pathlike string

      Returns
            Isolated session ID (e.g., ses-12345) or None
      """

      if "ses-" in incoming:
            return [k for k in incoming.split("_") if "func" not in k
                                            if "anat" not in k
                                            if "ses-" in k][0]

      return None


def get_new_filename(incoming):
      """
      Simple helper to remove session ID from filename
      """

      session_id = get_session_id(incoming)

      return incoming.replace(f"{session_id}/", "").replace(f"{session_id}_", "")


def rename_files(path_to_sub_dir):
      """
      This function loops through all files in a
      subject's directory and renames any stragglers that still
      have session IDs included

      Parameters
            path_to_sub_dir: str | Relative path to subject's BIDS data
      """

      for file in glob.glob(os.path.join(path_to_sub_dir, "**/*"), recursive=True):

            if "ses-" in file:

                  new_filename = get_new_filename(file)

                  os.rename(file, new_filename)


def clean_intended_for(incoming):
      """
      This function loops through a list (the IntendedFor field
      of a fmap JSON file) and iteratively renames the files

      Parameters
            x: List | List of relative paths from IntendedFor field

      Returns
            List of pristine relative paths
      """

      for ix, k in enumerate(incoming):

            if "ses-" in k:
                  incoming[ix] = get_new_filename(k)

            else:
                  incoming[ix] = k

      return incoming


def update_indented_for(path_to_sub_dir):
      """
      Cleans up the IntendedFor list for each fmap JSON file (fieldmap and magnitude)

      Parameters
            path_to_sub_dir: str | Relative path to subject's BIDS data
      """

      # Loop through JSON files in fmap sub-directory
      for json_file in glob.glob(os.path.join(path_to_sub_dir, "fmap/**/*.json"), recursive=True):

            # Open JSON as dictionary
            with open(json_file) as incoming:
                  temp = json.load(incoming)

            # Obtain clean list of relative paths
            temp["IntendedFor"] = clean_intended_for(temp["IntendedFor"])

            # Drop JSON files from IntendedFor field
            temp["IntendedFor"] = [x for x in temp["IntendedFor"] if ".json" not in x]

            # Add units to fieldmap files only
            if "fieldmap.json" in json_file:
                  temp["Units"] = "Hz"

            # Save file to its original filename
            with open(json_file, "w") as outgoing:
                  json.dump(temp, outgoing, indent=5)


def run_single_subject(subject_id, bids_path, log):
      """
      Wrapper for all helper functions written above

      Parameters
            subject_id: str | Subject's identifier in BIDS project
            bids_path: str | Relative path to top of BIDS project
            log: I/O streamer | Text file opened outside this function
      """

      # E.g., ./bids/sub-12345
      path_to_sub_dir = os.path.join(bids_path, f"sub-{subject_id}")

      # Catch typos
      if not os.path.exists(path_to_sub_dir):
            raise OSError(f"\n\nInvalid file path ... {path_to_sub_dir}")

      log.write(f"\n\n** sub-{subject_id}\n\n")

      try:
            rename_files(path_to_sub_dir)
            log.write("rename_files:\t\tSuccessful\n")
      except Exception as e:
            log.write(f"rename_files:\t\t{e}\n")

      try:
            update_indented_for(path_to_sub_dir)
            log.write("update_intended_for:\tSuccessful\n")
      except Exception as e:
            log.write(f"update_intended_for:\t{e}\n")


def main():

      # Relative path to BIDS project
      bids_root = sys.argv[1]

      # Subject ID or ALL
      subject = sys.argv[2]

      with open("./session_cleanup.txt", "w") as log:
            if subject.upper() == "ALL":
                  for sub in tqdm(BIDSLayout(bids_root).get_subjects()):
                        run_single_subject(subject_id=sub, 
                                           bids_path=bids_root,
                                           log=log)

            else:
                  run_single_subject(subject_id=subject, 
                                     bids_path=bids_root,
                                     log=log)


if __name__ == "__main__":
      main()