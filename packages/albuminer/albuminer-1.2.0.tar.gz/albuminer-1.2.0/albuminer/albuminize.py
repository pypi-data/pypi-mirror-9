#!/usr/bin/env python
from . import Albuminer
import sys
import os

"""
Binary: $ Albuminize.py path/to/file.mp3
Summary: Wraps Albuminer
"""


def wrap():
    fname_defined = True if len(sys.argv) >= 2 else False
    fname = sys.argv[1] if fname_defined else "unknown"

    print("Welcome to Albuminize. This is a Python wrapper to Albuminer.")

    # Get the filename
    if not fname_defined:
        while fname == "unknown":
            fname = input("Enter the path to the file/directory you want to albuminize: ")
            if not (os.path.isfile(fname) or os.path.isdir(fname)):
                print("Error! The given file or directory does not exist.")
                fname = "unknown"

    is_directory = True if os.path.isdir(fname) else False
    k = 0  # counter
    q = 1 if not is_directory else len([name for name in os.listdir(fname)])  # total files

    # Perform loop if a directory
    if is_directory:
        while k < q:
            sfn = fname + "/" + os.listdir(fname)[k]
            print("I'm going to try to find some covers for " + sfn + "...")
            alb = Albuminer(sfn)  # Initiate the albuminer
            alb.get_covers()        # Get 3 covers and choose one.
            alb.set_cover()         # Set the cover to the chosen one.
            print("'%s's cover has been added!" % alb.album)
            k += 1
    else:
        print("I'm going to try to find some covers for " + fname + "...")
        alb = Albuminer(fname)
        alb.get_covers()
        alb.set_cover()
        print("'%s's cover has been added!" % alb.album)
