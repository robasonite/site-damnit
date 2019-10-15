from datetime import datetime
from inspect import getsourcefile
from pathlib import Path
import pystache
import sys
import os
import shutil


### Variables ###
HELP_TXT = "Help text here"
VERSION = "Version 0.0.1"

# Get the current working directory
CWD = os.getcwd()
PROG_HOME = Path(os.path.abspath(getsourcefile(lambda:0))).parent
print(PROG_HOME)
DATA_DIR = os.path.join(PROG_HOME, "res")
print(DATA_DIR)



### Utility functions ###
# Get the current time as a string.
def get_datetime():
    """ Get the current date and time in a sensible format. """
    c_time = datetime.now()
    time_str = c_time.strftime("%Y-%m-%d %H-%M")
    return time_str

# Convert time strings into other formats
def get_split_datetime(fmt):
    """ Converts 'datestr' into a string according to 'format' """

    # Get the the date object
    date_obj = datetime.strptime(datestr, "%Y-%m-%d %H-%M")

    # Make a new time string
    new_date = date_obj.strftime(fmt)
    return new_date


# Handle CLI input
def input_handler(help_text, version):
    """ Handle command line arguments from the user """
    args = sys.argv
    length = len(sys.argv)
    if (length == 1):
        print(version)
        print(help_text)
    else:
        if (args[1] == "new"):
            print("'new' command");
            print(args)
            if len(args) > 2:
                new_site(args[2])
            else:
                new_site()
            
        elif (args[1] == "build"):
            print("'build' command")

        elif (args[1] == "list"):
            print("'link' command")

        elif (args[1] == "edit"):
            print("'edit' command")

        else:
            print("'{0}' is not a valid option.".format(args[1]))
            print(help_text)


### Site generation functions ###


def new_site(p=""):
    """
    Attempts to set up a new project directory at the specified path.
    If the directory already exists, it displays an error and does nothing.
    """
    # If the target directory is not specified, tell the user
    if p == "":
        print("You need to specifiy a location!")

    # Else, append the path the user provided to CWD
    else:
        if os.path.exists(p):
            print("Path '{}' exists!".format(p))
            print("Process aborted")

        # Try to make the directories
        else:
            print("Generating a new project in '{}'".format(p))
            os.makedirs(p)
            os.chdir(p)
            CWD = os.getcwd()

            # Make the required directories
            os.makedirs("content")
            os.makedirs("output")
            os.makedirs("templates")

            # Copy config file
            src = os.path.join(DATA_DIR, "config.json")
            dst = os.path.join(CWD, "config.json")
            shutil.copyfile(src, dst)
            print("Done!")




input_handler(HELP_TXT, VERSION)
