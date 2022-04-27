# Utility Scripts

* `anatomical_image_processing.py`: This script creates and saves anatomical images for each participant (or a given participant, depending on the command line arg). We supply participants with an anatomical image as one component of their compensation, and this also allows you to easily sanity check your data.

* `bids_sans_session.py`: This script pulls all `BIDS` data up one level, and renames each file to neglect the `ses-` identifier implicitly included in the data.