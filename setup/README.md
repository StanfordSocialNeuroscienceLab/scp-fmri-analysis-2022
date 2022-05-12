# Setup Scripts

These scripts are used to help process incoming data from Flywheel (data warehoue) to Oak (Stanford storage space)

* `directory_hierarchy.py`: Moves all BIDS data up from a session sub-directory and iteratively renames them to strip session identifiers
  
* `populate.py`: This script is hard-coded to update acquisition labels for our project derived from Flywheel's BIDS pre-curate gear.
  
* `session_cleanup.py`: Iteratively updates fieldmap and magnitude `JSON` files (`IntendedFor` fields) to suppress future `BIDS` errors
  
* `update_fmriprep.py`: Our `fmriprep` job script takes a Unix-style list of subject IDs. This script checks (i) who is in our BIDS project and (ii) who has been preprocessed already. Subjects that have already been preprocessed are excluded from the resulting text output.