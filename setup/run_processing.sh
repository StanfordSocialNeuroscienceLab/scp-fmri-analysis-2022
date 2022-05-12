#!/bin/bash

# Runs our processing scripts in one shot
# Ian Richard Ferguson | Stanford University

python3 directory_hierarchy.py ../bids $1

python3 session_cleanup.py ../bids $1