from datetime import datetime
from inspect import getsourcefile
from pathlib import Path
from distutils.dir_util import copy_tree
import pystache
import sys
import os
import shutil
import json
import glob


### Variables ###
SITE_CONF = {}
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
            build_site()

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

            # Copy resource files
            src = DATA_DIR
            dst = CWD
            copy_tree(src, dst)
            print("Done!")


def build_site():
    global SITE_CONF
    """ Iterate over files the content directory """

    # First make sure that the current directory contains a file called
    # 'config.json' and that we can read it.
    if os.access("config.json", os.R_OK):

        # Try to load the file
        with open("config.json") as f:

            # Assign the file to the global config
            SITE_CONF = json.load(f)

        # Next, try to dive into the 'content' directory
        for filename in glob.iglob("content" + '**/*', recursive=True):
            meta_file = os.path.join(filename, "meta.json")
            content_file = os.path.join(filename, "page.html")

            # If a file is missing or can not be read, don't try to process it
            skip_file = False

            # Try to read the meta file
            if os.access(meta_file, os.R_OK):
                with open(meta_file) as m:
                    page_meta = json.load(m)

            else:
                print("File '{}' is missing or can not be read!".format(meta_file))
                skip_file = True

            # Try to get the page contents
            if os.access(content_file, os.R_OK):
                with open(content_file) as c:
                    page_content = c.read()

            else:
                print("File '{}' is missing or can not be read!".format(content_file))
                skip_file = True

            # If we're still good, process the page
            if skip_file == False:
                # Stuff
                print("Processing '{}'".format(filename))

                # The page building function all of the data it needs
                build_page(SITE_CONF, page_meta, page_content)
            else:
                print("Skipping '{}'".format(filename))

            print(filename)

    else:
        print("Config file does not exist! Aborting...")


    # Print JSON to see if it's working
    # print(SITE_CONF)

def build_page(site_conf, meta, content):
    # Get the template page name
    template_name = "{}.mustache".format(meta['template'])

    # Try to find that template in the templates directory
    if os.access(os.path.join("templates", template_name), os.R_OK):
        with open(os.path.join("templates", template_name)) as pt:
            page_template = pt.read();

        # Create a combined object for rendering
        combo_vars = {}

        for k in meta:

            # Rename the keys to match patch page variable
            key_name = "page_" + str(k)
            combo_vars[key_name] = meta[k]

        # Add the site variables
        for c in site_conf:
            combo_vars[c] = site_conf[c]

        # See what we have so far
        #print(combo_vars)
        #print(meta)

        # Step 1: render page content
        combo_vars['page_content'] = content
        rendered_contents = pystache.render(page_template, combo_vars)
        print(rendered_contents)

    # If the page template can not be found, tell the user
    else:
        print("Template '{}' not found! Skipping....".format(template_name))



# Run program
input_handler(HELP_TXT, VERSION)
