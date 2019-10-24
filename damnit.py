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
PAGE_COLLECTION = []
HELP_TXT = """
- build    Builds the website project located in the current directory
- new      Creates a new project at the specified path
"""
VERSION = "Version 0.0.2"

# Get the current working directory
CWD = os.getcwd()
PROG_HOME = Path(os.path.abspath(getsourcefile(lambda:0))).parent
#print(PROG_HOME)
DATA_DIR = os.path.join(PROG_HOME, "res")
#print(DATA_DIR)



### Utility functions ###
# Get the current time as a string.
def strip_string(string):
    """Strip spaces and special characters from a string. Useful for URLS.

    Arguments:
    string -- The string to strip

    Returns the stripped string
    """
    new_string = ''.join(e for e in string if e.isalnum())
    return new_string

def get_datetime():
    """ Get the current date and time in a sensible format. """
    c_time = datetime.now()
    time_str = c_time.strftime("%Y-%m-%d %H-%M")
    return time_str

# Convert time strings into other formats
def get_split_datetime(fmt):
    """Converts 'datestr' into a string according to 'fmt'.
    
    Arguments:
    fmt -- A standard time format string. Look up 'strftime'
    """

    # Get the the date object
    date_obj = datetime.strptime(datestr, "%Y-%m-%d %H:%M")

    # Make a new time string
    new_date = date_obj.strftime(fmt)
    return new_date

def sort_date_sring_list(date_list, direction='asc'):
    """Sorts an array of date strings by date. The date string must have the
    format '%Y-%m-%d %H-%M'.
    Arguments:
    date_list -- The array to work on.
    direction -- Which direction to sort in. It can be 'asc' for ascending or
    'des' for descending.

    Conversion happens in-place via lambda.
    """

    # Sort the date strings with a lambda
    date_list.sort(key = lambda date: datetime.strptime(date, "%Y-%m-%d %H:%M"))

    # Ascending order is the default, so just return the list
    if direction == 'asc':
        return date_list

    elif direction == 'des':
        date_list.reverse()
        return date_list


def sort_pages_by_date():
    global PAGE_COLLECTION

    page_dates = []
    new_collection = []

    # Grab all date strings
    for page in PAGE_COLLECTION:
        if 'page_datetime' in page['page_vars']:
            page_dates.append(page['page_vars']['page_datetime'])

    sorted_dates = sort_date_sring_list(page_dates, 'des')

    # Generate a new list with the pages in the right order
    for date in page_dates:
        for page in PAGE_COLLECTION:
            if 'page_datetime' in page['page_vars']:
                if date == page['page_vars']['page_datetime']:
                    new_collection.append(page)

    # Now make new_collection the new PAGE_COLLECTION
    PAGE_COLLECTION = new_collection
            



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
    """Attempts to set up a new project directory at the specified path.
    If the directory already exists, it displays an error and does nothing."""
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
    global PAGE_COLLECTION
    """Iterate over files in the 'content' directory and generate appropriate
    in the 'output' directory."""

    # First make sure that the current directory contains a file called
    # 'config.json' and that we can read it.
    if os.access("config.json", os.R_OK):

        # Try to load the file
        with open("config.json") as f:

            # Assign the file to the global config
            SITE_CONF = json.load(f)

        # Next, try to dive into the 'content' directory
        for root, dirs, files in os.walk("content"):
            path = root.split(os.sep)

            # Specify the files we're looking for
            vars_file = os.path.join(root, "vars.json")
            content_file = os.path.join(root, "page.html")

            # If a file is missing or can not be read, don't try to process it
            skip_file = False

            # Try to read the variables file
            if os.access(vars_file, os.R_OK):
                with open(vars_file) as m:
                    page_vars = json.load(m)

                # Remove 'content' from the page path
                path.pop(0)
                sep = "{}".format(os.sep)
                new_path = sep.join(path)
                print("New path: {}".format(new_path))
                # Also need to check if 'page_vars' has a url specified
                # If not, generate one
                if "page_url" not in page_vars:

                    # Need know whether the domain should be appended
                    if SITE_CONF["site_config_absolute_urls"] == True:
                        p_path = SITE_CONF['site_domain'] + "/" + new_path + ".html"

                    else:
                        p_path = "/" + new_path + ".html"

                    page_vars["page_url"] = p_path

                # Category handling
                if "page_category" in page_vars:
                    page_vars["page_has_category"] = True

                # Tag handling
                if "page_tags" in page_vars:
                    page_vars["page_has_tags"] = True

                    # Convert tags into a format for adding additional
                    # functionality
                    new_tags = []
                    for x in page_vars["page_tags"]:
                        new_tags.append({"name": x})
                    
                    page_vars["page_tags"] = new_tags

                # Date time handling
                # ALL PAGES MUST HAVE DATE / TIME. If not, generate one.
                if "page_datetime" not in page_vars:
                    page_vars["page_datetime"] = datetime.now().strftime("%Y-%m-%d %H:%M")
                    #page_vars["page_has_datetime"] = True

                # Make sure all pages have a 'type'.
                if "page_type" not in page_vars:
                    page_vars["page_type"] = "none"

                # Output path won't be in page_vars by default
                f_name = path.pop(-1)
                new_path = sep.join(path)

                # Make sure output path never ends in 'os.sep'
                if new_path != "":
                    page_vars['page_output_path'] = "output" + sep + new_path
                else:
                    page_vars['page_output_path'] = "output"

                # Neither will filename
                page_vars['page_file_name'] = f_name + ".html"


                #print(page_vars)


            else:
                print("File '{}' is missing or can not be read!".format(vars_file))
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
                print("Processing '{}'".format(root))
                
                # Collect page contents and metadata before anything else
                print(SITE_CONF)
                collect_page(page_vars, page_content)
                
            else:
                print("Skipping '{}'".format(root))


            print(root)
        
        # Print the collection to see where we're at
        #print(PAGE_COLLECTION)

        # Now that page data has been collected, it needs to be sorted by date
        sort_pages_by_date()

        # Before going any further, we need to create the output directory
        if not os.path.exists('output'):
            os.makedirs('output')

        # Check to see if the directory is writable
        if os.access('output', os.W_OK):

            # Generate the tag pages
            build_tag_pages(SITE_CONF, PAGE_COLLECTION)

            # Generate category pages
            build_category_pages(SITE_CONF, PAGE_COLLECTION)
            
            # Build regualar pages
            for page in PAGE_COLLECTION:
                build_page(SITE_CONF, page['page_vars'], page['page_content'])
                #print(page)


        else:
            print("Output directory can not be written to!")
            print("Please adjust permissions on the directory (or delete it) and try again.")


    else:
        print("Config file does not exist! Aborting...")


    # Print JSON to see if it's working
    # print(SITE_CONF)

def collect_page_category(page_vars):
    """Scans page variables and adds the category to the global SITE_CONF
    variable.

    Arguments:
    page_vars -- Variables specified in 'var.json' for the given page.

    This function is used in collect_page()
    """
    global SITE_CONF
    
    #print(page_vars)

    # Pages should only have one category
    cat = page_vars['page_category']
    print(cat)

    # Need this to prevent repeating code
    add_cat = False

    # Case 1: 'site_categories' is not in SITE_CONF
    if 'site_categories' not in SITE_CONF.keys():
        # Create it
        SITE_CONF['site_categories'] = []
   

    SITE_CATS = SITE_CONF['site_categories']


    # Case 2: 'site_categories' is empty
    if len(SITE_CATS) == 0:
        add_cat = True

    # Case 3: Iterate over SITE_CATS
    else:
        for SC in SITE_CATS:

            # Check each of the  in page_vars
            if cat == SC['category_name']:

                # Increment if so
                SC['category_count'] += 1

            else:
                # Add the tag if not
                add_cat = True

    # If the tag doesn't exist, create it
    if add_cat == True:
        new_pc = {}
        new_pc['category_name'] = cat 
        new_pc['category_count'] = 1

        # Need know whether the domain should be appended
        if SITE_CONF['site_config_absolute_urls'] == True:
            p_path = SITE_CONF['site_domain'] + "/categories/" + strip_string(new_pc['category_name']) + ".html"

        else:
            p_path = "/categories/" + strip_string(new_pc['category_name']) + ".html"

        new_pc['category_page_url'] = p_path

        print(new_pc)
        SITE_CATS.append(new_pc)


def collect_page_tags(page_vars):
    """Scans page variables and adds tags to the global SITE_CONF variable.

    Arguments:
    page_vars -- Variables specified in 'var.json' for the given page.
    
    This function is used in collect_page()
    """
    global SITE_CONF
    
    if 'site_tags' not in SITE_CONF.keys():
        # Create it
        SITE_CONF['site_tags'] = []
    
    SITE_TAGS = SITE_CONF['site_tags']

    # Iterate over the tags
    for tag in page_vars['page_tags']:
        print(tag)

        # Need this to prevent repeating code
        add_tag = False

        # Case 1: PAGE_TAGS is empty
        if len(SITE_TAGS) == 0:
            add_tag = True

        else:
            # Iterate over PAGE_TAGS
            for ST in SITE_TAGS:

                # Check each of the tags in page_vars
                if tag['name'] == ST['tag_name']:

                    # Increment if so
                    ST['tag_count'] += 1
                else:
                    # Add the tag if not
                    add_tag = True

        # If the tag doesn't exist, create it
        if add_tag == True:
            new_pt = {}
            new_pt['tag_name'] = tag['name']
            new_pt['tag_count'] = 1

            # Need know whether the domain should be appended
            if SITE_CONF['site_config_absolute_urls'] == True:
                p_path = SITE_CONF['site_domain'] + "/tags/" + strip_string(new_pt['tag_name']) + ".html"

            else:
                p_path = "/tags/" + strip_string(new_pt['tag_name']) + ".html"

            new_pt['tag_page_url'] = p_path

            SITE_TAGS.append(new_pt)
    
    # Add PAGE_TAGS to SITE_CONF
    #SITE_CONF['site_tags'] = SITE_TAGS


def collect_page_list_item(page_vars, target_key="", target_val=""):
    """Scans page variables and adds page list items to the SITE_CONF variable.

    Arguments:
    page_vars -- Variables specified in 'var.json' for the given page.
    target_key -- Specifies what page key to group by. 
    target_val -- If specified, only pages with 'target_key = target_val' will
    be added to the list.
   
    Required templates:
    page_list_item.mustache
   
    Notes:
    If 'target_key' is NOT set, the key 'site_page_list_all' will be created in
    SITE_CONF.

    If 'target_key' is set, but 'target_val' is not, the key
    'site_page_list_<target_key>' will be created in SITE_CONF.

    If 'target_key' and 'target_val' are set, the key 
    'site_page_list_<target_key>_<target_val>' will be created in SITE_CONF.
    """
    global SITE_CONF
    
    page_list_item_template_name = "page_list_item"
    if os.access(os.path.join("templates", page_list_item_template_name + ".mustache"), os.R_OK):
        with open(os.path.join("templates", page_list_item_template_name + ".mustache")) as t:
            page_list_item_template = t.read()

    # List item content
    content = ""
    
    # Generate a site variable named after the collection. The default is "",
    # which means key_name = "site_page_list_all".
    if target_key == "":
        key_name = "site_page_list_all"
        
        for p in PAGE_COLLECTION:
            content += pystache.render(page_list_item_template, p['page_vars'])

    else:

        if target_val == "":
            key_name = "site_page_list_" + str(target_key)
            
            for p in PAGE_COLLECTION:
                target_key_name = "page_" + target_key
                if target_key_name in p['page_vars']:
                    content += pystache.render(page_list_item_template, p['page_vars'])

        else:
            key_name = "site_page_list_" + str(target_key) + "_" + str(target_val)
            
            for p in PAGE_COLLECTION:
                target_key_name = "page_" + target_key
                if target_key_name in p['page_vars']:
                    if target_val == p['page_vars'][target_key_name]:
                        content += pystache.render(page_list_item_template, p['page_vars'])


    
    if key_name not in SITE_CONF.keys():
        SITE_CONF[key_name] = ""

    SITE_CONF[key_name] = content
    #print(SITE_CONF[key_name])



def collect_page(page_vars, page_content):
    global PAGE_COLLECTION
    """Collects the contents of a page and it's variables into a dictionary, which
    is then added to PAGE_COLLECTION."""

    # Create a new dict to hold the data
    pg_dict = {}
    pg_dict['page_vars'] = page_vars
    pg_dict['page_content'] = page_content

    # Add to the page
    PAGE_COLLECTION.append(pg_dict)

    # Also collect the metadata
                
    # Make sure the page has categories to avoid errors
    if 'page_category' in page_vars.keys():
        collect_page_category(page_vars)

    # Make sure the page has tags to avoid errors
    if 'page_tags' in page_vars.keys():
        collect_page_tags(page_vars)

    # Generate list items
    collect_page_list_item(page_vars)
    collect_page_list_item(page_vars, "type", "articles")
    #print(SITE_CONF['site_page_list_type_articles'])




def build_page(site_conf, page_vars, content):
    """Build a page using template specified in 'page_vars', and information from 'site_conf' and 'page_vars'.
    
    Arguments:
    site_conf -- Pass the global SITE_CONF variable.
    page_vars -- Variables specified in 'var.json' for the given page.
    content   -- The contents of 'page.html' for a given page.
    """
    # Get the template page name
    template_name = "{}.mustache".format(page_vars['page_template'])
    base_template_name = "base.mustache"

    # Check the required templates
    template_ok = True
    if os.access(os.path.join("templates", template_name), os.R_OK):

        # Grab the page template contents
        with open(os.path.join("templates", template_name)) as pt:
            page_template = pt.read();
    else:
        template_ok = False
        failed_template = os.path.join("templates", template_name)

    if os.access(os.path.join("templates", base_template_name), os.R_OK):
        # Grab the base template contents
        with open(os.path.join("templates", base_template_name)) as base:
            base_template = base.read()
    else:
        template_ok = False
        failed_template = os.path.join("templates", base_template_name)

    # If we're still good, render the page
    if template_ok == True:
        # Create a combined object for rendering
        combo_vars = {}

        for k in page_vars:
            combo_vars[k] = page_vars[k]

        # Add the site variables
        for c in site_conf:
            combo_vars[c] = site_conf[c]

        # See what we have so far
        #print(combo_vars)
        #print(page_vars)

        # Step 1: render page content
        combo_vars['page_content'] = content
        rendered_contents = pystache.render(page_template, combo_vars)
        #print(rendered_contents)

        # Step 2: render with 'base.mustache'
        combo_vars['page_content'] = rendered_contents
        rendered_contents = pystache.render(base_template, combo_vars)
        #print(rendered_contents)

        # Need to write the page. This is where Pathlib really shines.
        Path(combo_vars['page_output_path']).mkdir(parents=True, exist_ok=True)

        # Now try to write the page
        page_target = os.path.join(combo_vars['page_output_path'], combo_vars['page_file_name']) 
        with open(page_target, 'w') as p:
            p.write(rendered_contents)


    # If the page template can not be found, tell the user.
    else:
        print("Template '{}' not found! Skipping....".format(template_name))


def build_category_pages(site_conf, page_collection):
    """Builds category pages in 'output/categories/<category_name>', and the
    main 'output/category.html' list page.

    Arguments:
    site_conf -- The globe SITE_CONF variable.
    page_collection -- The globe PAGE_COLLECTION variable.

    Required templates:
    category_list_page.mustache
    category_page.mustache
    page_list_item.mustache
    """

    # Start by looking for the right templates
    templates_ok = True
    cats_found = False
    category_list_template_name = "category_list_page"
    category_page_template_name = "category_page"
    page_list_item_template_name = "page_list_item"
    if not os.access(os.path.join("templates", category_list_template_name + ".mustache"), os.R_OK):

    # Tell the user what went wrong
        print("Template '{}' not found!".format(category_list_template_name))
        templates_ok = False

    if not os.access(os.path.join("templates", category_page_template_name + ".mustache"), os.R_OK):
        print("Template '{}' not found!".format(category_page_template_name))
        templates_ok = False
   
    # This is the ONLY template file that must be opened and read within this
    # function.
    if os.access(os.path.join("templates", page_list_item_template_name + ".mustache"), os.R_OK):
        with open(os.path.join("templates", page_list_item_template_name + ".mustache")) as t:
            page_list_item_template = t.read()

    else:
        print("Template '{}' not found!".format(page_list_item_template_name))
        templates_ok = False


    if templates_ok:

        # Try to collect the page categories
        #for page in page_collection:

            #page_vars = page['page_vars']
            # Make sure the page has tags to avoid errors
            #if 'page_category' in page_vars.keys():
                #collect_page_category(page_vars)

        # Check if we have page categories to work with
        if 'site_categories' in site_conf.keys():
            cats_found = True

            # Need to build page variables to use build_page()
            page_vars = {}
            page_vars['page_title'] = "Categories"
            page_vars['page_template'] = category_list_template_name
            page_vars['page_output_path'] = "output"
            page_vars['page_file_name'] = "categories.html"
            page_vars["page_datetime"] = datetime.now().strftime("%Y-%m-%d %H:%M")
            build_page(site_conf, page_vars, "")

            # Now for the crazy part: Getting the individual cat pages to generate
            for cat in site_conf['site_categories']:
                page_vars['page_title'] = cat['category_name']
                page_vars['page_template'] = category_page_template_name
                page_vars['page_output_path'] = "output/categories"
                page_vars['page_file_name'] = cat['category_name'] + ".html"
                page_vars["page_datetime"] = datetime.now().strftime("%Y-%m-%d %H:%M")

                # Need to generate some pre-rendered content
                page_list = []

                # Search all pages for the current category and add them to the page
                # list.
                for page in page_collection:
                    if 'page_category' in page['page_vars']: 
                        if page['page_vars']['page_category'] == cat['category_name']:
                            page_list.append(page)

                # Render the pages
                content = ""
                for p in page_list:
                    content += pystache.render(page_list_item_template, p['page_vars'])
                
                page_vars['category_page_list'] = content
                page_vars['category_name'] = cat['category_name']
                build_page(site_conf, page_vars, "")
               

        # Tell the user there are no categories
        #else:
        #    print("No page categories found! Skipping category page generation."

    else:
        print("Unable to generate category pages!")

    if cats_found == False:
        print("No page categories found. Skipping...")


def build_tag_pages(site_conf, page_collection):
    """Builds tag pages in 'output/tags/<tag_name>', and the main 'output/tags.html' list page.

    Arguments:
    site_conf -- The globe SITE_CONF variable.
    page_collection -- The globe PAGE_COLLECTION variable.

    Required templates:
    tag_list_page.mustache
    tag_page.mustache
    page_list_item.mustache
    """

    # Start by looking for the right templates
    templates_ok = True
    tags_found = False
    tag_list_template_name = "tag_list_page"
    tag_page_template_name = "tag_page"
    page_list_item_template_name = "page_list_item"
    if not os.access(os.path.join("templates", tag_list_template_name + ".mustache"), os.R_OK):

        # Tell the user what went wrong
        print("Template '{}' not found!".format(tag_list_template_name))
        templates_ok = False

    if not os.access(os.path.join("templates", tag_page_template_name + ".mustache"), os.R_OK):
        print("Template '{}' not found!".format(tag_page_template_name))
        templates_ok = False
   
    # This is the ONLY template file that must be opened and read within this
    # function.
    if os.access(os.path.join("templates", page_list_item_template_name + ".mustache"), os.R_OK):
        with open(os.path.join("templates", page_list_item_template_name + ".mustache")) as t:
            page_list_item_template = t.read()

    else:
        print("Template '{}' not found!".format(page_list_item_template_name))
        templates_ok = False

    if templates_ok:
        # Collect the tags
        #print(PAGE_COLLECTION)

        # By this point, collect_page() should have already collected all page
        # tags

        # Check if we have page categories to work with
        if 'site_tags' in site_conf.keys():
            tags_found = True
            # Take a look at PAGE_TAGS and see what happened
            #print(SITE_CONF)

            # Now generate the main tags.html page

            # Generate the content to feed into build_page()
            #tags_page_content = pystache.render(tag_list_template, site_conf)
            #print(tags_page_content)

            # Need to build page variables to use build_page()
            page_vars = {}
            page_vars['page_title'] = "Tags"
            page_vars['page_template'] = tag_list_template_name
            page_vars['page_output_path'] = "output"
            page_vars['page_file_name'] = "tags.html"
            page_vars["page_datetime"] = datetime.now().strftime("%Y-%m-%d %H:%M")
            build_page(site_conf, page_vars, "")

            # Now for the crazy part: Getting the individual tag pages to generate
            for tag in site_conf['site_tags']:
                page_vars['page_title'] = tag['tag_name']
                page_vars['page_template'] = tag_page_template_name
                page_vars['page_output_path'] = "output/tags"
                page_vars['page_file_name'] = tag['tag_name'] + ".html"
                page_vars["page_datetime"] = datetime.now().strftime("%Y-%m-%d %H:%M")

                # Need to generate some pre-rendered content
                page_list = []

                # Search all pages for the current tag and add them to the page
                # list.
                for page in page_collection:
                    if 'page_tags' in page['page_vars']: 
                        for pt in page['page_vars']['page_tags']:
                            if pt['name'] == tag['tag_name']:
                                page_list.append(page)

                # Render the pages
                content = ""
                for p in page_list:
                    content += pystache.render(page_list_item_template, p['page_vars'])
                
                page_vars['tag_page_list'] = content
                page_vars['tag_name'] = tag['tag_name']
                build_page(site_conf, page_vars, "")
           

    else:
        print("Unable to generate tag pages!")

    if not tags_found:
        print("No page tags found. Skipping...")
    


# Run program
input_handler(HELP_TXT, VERSION)
