#!/bin/python3

"""
ABOUT THIS SCRIPT

This script automates opening surveys for SCP fMRI
participants. Run like this from the command line:

python3 open_survey.py 12345 PRE

Ian Richard Ferguson | Stanford University
"""

# --- Imports
import pandas as pd
import webbrowser, sys


# --- Functions
def get_link(PID, SCAN):
      """
      Gets link for survey (can be PRE or POST scan)

      Parameters
            PID: int or str | Participant identifier
            SCAN: str | Should be PRE or POST

      Returns
            URL to survey in string form
      """

      # Read in Recruitment CSV
      log = pd.read_csv("./scp_recruitment.csv")

      # Convert PID column to string
      log["PID"] = log["PID"].astype(str)

      # Isolate PID values
      log = log[log["PID"] == PID].reset_index(drop=True)

      # Length of DF should be exactly 1 observation
      if len(log) != 1:
            raise ValueError(f"PID invalid ... rendered log of length {len(log)}")

      if SCAN.upper() == "PRE":
            return list(log["baseline_link"])[0]
      elif SCAN.upper() == "POST":
            return list(log["postScan_link"])[0]
      else:
            raise ValueError(f"{SCAN} is invalid input ... type PRE or POST next time")


def main():

      if len(sys.argv) < 3:
            PID = input("\nSubject ID:\t\t\t")
            SESSION = input("Scan session (Pre or Post):\t")
      else:
            PID = sys.argv[1]
            SESSION = sys.argv[2]

      target_url = get_link(PID=PID, SCAN=SESSION)

      try:
            webbrowser.open(target_url)
      except Exception as e:
            raise OSError(f"Caught an error:\t{e}")


if __name__ == "__main__":
      main()