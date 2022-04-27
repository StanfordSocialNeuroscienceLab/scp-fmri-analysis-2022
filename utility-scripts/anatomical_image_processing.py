#!/bin/python3

"""
About this Script

We're giving subjects plots of their anatomical
images as a part of their compensation. This script
creates a subject-specific ouput folder and saves a local
mosaic and ortho plot of their T1w image

IRF | SSNL
"""

# --- Imports
import sys, os, pathlib, glob, warnings
import nilearn.plotting as nip
from tqdm import tqdm
from bids import BIDSLayout

warnings.filterwarnings('ignore')

# --- Functions
def make_output_file(sub_id, suppress=False):
      """
      Creates a subject specific output directory

      Parameters
            sub_id: str | Subject ID from BIDS project, e.g., 10245
            suppress: Boolean | if True, print statements are suppressed
      """

      # Path to output
      output_path = os.path.join(f'./participant_images/sub-{sub_id}')

      if not os.path.exists(output_path):

            if not suppress:
                  print('\n== Creating subject output directory ==')

            pathlib.Path(output_path).mkdir(exist_ok=True, parents=True)


def isolate_anat_path(sub_id, bids_root):
      """
      Finds relative path to the participant's T1w anatomical scan

      Parameters
            sub_id: str | Subject ID from BIDS project, e.g., 10245
            bids_root: str | Relative path to top of BIDS project

      Returns
            Single-string relative path to the participant's T1w file
      """

      subject_path = os.path.join(bids_root, f'sub-{sub_id}')

      return [x for x in glob.glob(os.path.join(subject_path, '**/*.nii.gz'), recursive=True) if 'T1w' in x][0]


def build_plots(sub_id, path_to_T1, suppress=False):
      """
      Creates plots of the participant's T1w anatomical scan

      Parameters
            sub_id: str | Subject ID from BIDS project, e.g., 10245
            path_to_T1 : str | Relative path to participant's T1 scan
            suppress: Boolean | if True, print statements are suppressed
      """

      output_path = os.path.join(f'./participant_images/sub-{sub_id}')

      """
      print('\n== Plotting mosaic ==')
      k = nip.plot_anat(path_to_T1, draw_cross=False, display_mode='mosaic',
                        dim=-1.65, threshold=5.,
                        output_file=os.path.join(output_path, f'sub-{sub_id}_T1w-mosaic.png'))

      """

      if not suppress:
            print('\n== Plotting ortho ==')

      m = nip.plot_anat(path_to_T1, draw_cross=False, display_mode='ortho',
                        dim=-1.65, threshold=5.,
                        output_file=os.path.join(output_path, f'sub-{sub_id}_T1w-ortho.png'))


      if not suppress:
            print('\n== Plotting mid-saggital ==')

      s = nip.plot_anat(path_to_T1, 
                        draw_cross=False, 
                        display_mode='x',
                        dim=-1.65, threshold=5.,
                        output_file=os.path.join(output_path, f'sub-{sub_id}_T1w-saggital.png'))



def main():
      """
      USAGE: Supply two command line args to run this function

      (1) Subject id (e.g., "01024")
      (2) Relative path to BIDS project (e.g., "./bids/")
      """

      try:
            sub_id = sys.argv[1]
      except:
            raise OSError('We\'re missing a subject ID ...')

      try:
            bids_path = sys.argv[2]
      except:
            raise OSError('We\'re missing a relative path to your BIDS project...')

      if str(sub_id).upper() != 'ALL':

            # Create subject specific output directory
            make_output_file(sub_id=sub_id)
            
            # Isolate path to T1w scan
            path_to_T1 = isolate_anat_path(sub_id=sub_id, bids_root=bids_path)
            
            # Plot and save anatomical plots
            build_plots(sub_id=sub_id, path_to_T1=path_to_T1)

      else:
            """
            If you supply ALL in place of a subject ID, we'll loop through
            each BIDS subject and save their plots locally
            """

            # Instantiate BIDSLayout object
            bids = BIDSLayout(bids_path)
            
            # Get list of BIDS subjects
            subjects = bids.get_subjects()

            for sub in tqdm(subjects):

                  # Create output directory for each subject
                  make_output_file(sub_id=sub, suppress=True)
                  
                  # Isolate T1w file
                  path_to_T1 = isolate_anat_path(sub_id=sub, bids_root=bids_path)
                  
                  # Plot anatomical files for subject
                  build_plots(sub_id=sub, path_to_T1=path_to_T1, suppress=True)


if __name__ == "__main__":
      main()