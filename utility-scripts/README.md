# Utility Scripts

* `hiearachy.py`: This script pulls all `BIDS` data up one level, and renames each file to neglect the `ses-` identifier implicitly included in the data.

* `open_survey.py`: This is hard-coded to open pre- and post-scan Qualtrics survey for a given Subject ID in a web browser.

* `populate.py`: This script is hard-coded to update acquisition labels for our project derived from Flywheel's BIDS pre-curate gear.

* `t1_processor.py`: This script creates and saves anatomical images for each participant (or a given participant, depending on the command line arg). We supply participants with an anatomical image as one component of their compensation, and this also allows you to easily sanity check your data.

* `update_fmriprep.py`: Our `fmriprep` job script takes a Unix-style list of subject IDs. This script checks (i) who is in our BIDS project and (ii) who has been preprocessed already. Subjects that have already been preprocessed are excluded from the resulting text output.