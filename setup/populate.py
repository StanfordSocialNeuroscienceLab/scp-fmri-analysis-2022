#!/bin/python3

"""
ABOUT THIS SCRIPT

I'm tired of filling the same cells
for the BIDS curation template, so this
script takes care of it

Ian Richard Ferguson | Stanford University
"""

# --- Imports
import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import os, sys
from tqdm import tqdm


# --- Helpers
def match_incoming(incoming_text):
      """
      Returns value from replacement map key
      """

      replacement_map = {
          # -- Anatomical and spatial conventions
          "T1w .9mm BRAVO": "anat-T1w_acq-9mmBRAVO",
          "spiral fieldmap": "fmap-fieldmap",
          
          # -- Social evaluation task
          "fMRI social eval run1 HB4": "func-bold_task-socialeval_run-1",
          "fMRI social eval run2 HB4": "func-bold_task-socialeval_run-2",
          
          # -- Stress buffering task
          "fMRI stress buff run1 HB4": "func-bold_task-stressbuffer_run-1",
          "fMRI stress buff run1 HB4_1": "func-bold_task-stressbuffer_run-1_v2",
          "fMRI stress buff run2 HB4": "func-bold_task-stressbuffer_run-2",

          # -- Passive faces task
          "fMRI faces run1 HB4": "func-bold_task-faces_run-1",

          # -- Resting state
          "fMRI rest run1 HB4": "func-bold_task-rest_run-1",
          "fMRI rest run2 HB4": "func-bold_task-rest_run-2"
      }


      # Label needs to be replaced
      if incoming_text in list(replacement_map.keys()):
            return replacement_map[incoming_text]

      # Label is BIDS compliant
      elif incoming_text in list(replacement_map.values()):
            return incoming_text

      # Localizer 
      else:
            return ""


def main():

      # Path to labels
      try:
            path = sys.argv[1]
      except:
            raise OSError("HEY! Missing a command line argument!")

      
      # Read in relpath as DataFrame
      try:
            labels = pd.read_csv(path)
      except Exception as e:
            raise e


      # Loop through EXISTING acquisition labels
      for ix, val in tqdm(enumerate(labels["existing_acquisition_label"])):

            # Generate NEW acquisition labels
            new_label = match_incoming(val)

            # Assign to column position
            labels["new_acquisition_label"][ix] = new_label

      labels.to_csv(path, index=False)
      print("\n** Acquisition table saved **\n")


if __name__ == "__main__":
      main()