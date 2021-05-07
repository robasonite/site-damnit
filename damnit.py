#!/usr/bin/env python3
#
# Site Damnit v0.0.3
#
# Copyright (C) 2020 Robert Kight.
#
# This program is free and open source software released under the GNU GPLv3.
# See COPYING for full license text.

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
import pystache # external
import commonmark # external
import yaml # external? Fedora 30 seemed to install it by default, but not Ubuntu
import sys
import os
import shutil
import errno
import json
from datetime import datetime

VERSION = """Site Damnit v0.0.3
Copyright 2020 Robert Kight

This software is made available under the terms and conditions of the MIT
license. See LICENSE file for details.
"""


# Rename the config dict to keep stuff from breaking.
SITE_VARS = {}

DEFAULT_CONFIG = """siteAuthor: Your Name Here
siteDefaultKeywords: default, key, words, here
siteDescription: Enter a default description here.
siteGenLunrJson: false
siteName: Your site name here

# Don't change this unless you know what you're doing.
siteRoot: /

# Can be either 'number' or 'alpha'
siteTagSort: number

# Can be either 'number' or 'alpha'
siteCategorySort: number
"""


# Define standard directories. Don't touch unless you know what you're doing.
CWD = os.getcwd()
TEMPLATES = os.path.join(CWD, "templates")
OUTPUT = os.path.join(CWD, "output")
CONTENT = os.path.join(CWD, "content")
CONFIG = os.path.join(CWD, "config.yaml")


# Functions

def genLunrJson(page_list):
    """ Generates a file called index.json and writes it to the output
    directory.

    Arguments:
    page_list -- The dictionary of pages to encode
    """

    global OUTPUT

    # The dictionary needs to be filtered to get the relevent data
    filtered_list = []

    # Every page needs an id
    page_id = 0

    for p in page_list:

        # A page must have content to be included
        if (p['content'] != ""):
            page_item = {}
            page_item['id'] = page_id

            # Need to increment page_id every time
            page_id += 1

            page_item['title'] = p['title']
            page_item['date'] = "{0}/{1}/{2}".format(p['year'], p['month'], p['day'])
            #if ('title' in p):
            #if ('date' in p):
            if ('tags' in p):
                page_item['tags'] = p['tags']
            else:
                page_item['tags'] = ['none']

            if ('categories' in p):
                page_item['categories'] = p['categories']
            else:
                page_item['categories'] = ['none']

            page_item['content'] = render_cmark(p['content'])
            filtered_list.append(page_item)

    with open(os.path.join(OUTPUT, 'index.json'), 'w') as f:
        json.dump(filtered_list, f)



def copy_path(src, dest):
    """ Attempts to copy files and directories from 'src' to 'dest'. It will
    automatically switch between `shutil.copy` and `shutil.copytree` based on
    whether the `src` is a file or directory. When copying a directory, the
    operation is recursive and will copy the entire contents of the directory.

    Arguments:
    src -- The file or directory to be copied.
    dest -- The destination to copy to.
    """

    try:
        shutil.copytree(src, dest)
    except OSError as e:
        # If the error was caused because the source wasn't a directory
        if e.errno == errno.ENOTDIR:
            shutil.copy(src, dest)
        else:
            print('Directory not copied. Error: %s' % e)

def sort_date_obj_list(date_list, direction='asc'):
    """Sorts an array of datetime objects by date.

    Arguments:
    date_list -- The array to work on.
    direction -- Which direction to sort in. It can be 'asc' for ascending or
    'des' for descending.

    Conversion happens in-place via list.sort(). Returns a sorted list of
    datetime objects.
    """

    # Sort the date strings with a lambda
    #date_list.sort(key = lambda date: datetime.strptime(date, "%Y-%m-%d %H:%M"))

    # Sort datetime objects
    date_list.sort()

    # Ascending order is the default, so just return the list
    if direction == 'asc':
        return date_list

    elif direction == 'des':
        date_list.reverse()
        return date_list

def sort_date_string_list(date_list, direction='asc'):
    """Sorts an array of date strings by date. The date string must have the
    format '%Y-%m-%d %H-%M'.

    Arguments:
    date_list -- The array to work on.
    direction -- Which direction to sort in. It can be 'asc' for ascending or
    'des' for descending.

    Conversion happens in-place via lambda. Returns a sorted list of strings.
    """

    # Sort the date strings with a lambda
    date_list.sort(key = lambda date: datetime.strptime(date, "%Y-%m-%d %H:%M"))

    # Ascending order is the default, so just return the list
    if direction == 'asc':
        return date_list

    elif direction == 'des':
        date_list.reverse()
        return date_list

def sort_pages_by_date(page_list):
    """Sorts a list of page dicts by datetime and returns the sorted
    list.

    Arguments:
    page_list -- The list of page dictionaries to operate on

    Returns a list of sorted dictionaries.
    """
    page_dates = []
    new_list = []

    # NOTE: If for some reason the page does not have a 'date' attribute, it will be REMOVED from the page list!
    # Grab all date strings:
    for page in page_list:
        if 'date' in page:
            page_dates.append(page['date'])

        #else:
        #    print("Page {} DOES NOT HAVE A DATE!".format(page['title']))

    # NOTE: the date must be a string for sort_date_string_list() to work.
    #sorted_dates = sort_date_string_list(page_dates, 'des')
    sorted_dates = sort_date_obj_list(page_dates, 'des')

    # NOTE: For dates that are autogenerated, a bug can occur where the same
    # page may appear multiple times in the returned page list. Since it makes
    # sense for all pages to have a unique title, the final list is checked
    # against a de-duplicated list of titles.
    title_list = []

    # Generate a new list with the pages in the right order
    for date in page_dates:
        for page in page_list:
            if date == page['date']:

                # Make sure that a page is only added ONCE
                if page['title'] not in title_list:
                    title_list.append(page['title'])
                    new_list.append(page)


    # Return the new collection
    return new_list


def render_cmark(data):
    """ Renders a Markdown string of text with the CommonMark library.

    Arguments:
    data -- The data, in the form of a string, to be processed.

    Returns a string of HTML.
    """
    return commonmark.commonmark(data)


def split_yaml(data):
    """ Splits text from a page file into YAML and Content sections. The raw
    Content is added directly to the resulting dictionary as the value of the
    'content' key. The page date is processed to produce keys for 'year',
    'month', 'day', 'hour', and 'minute'.

    Arguments:
    data -- The page text to operate on

    Returns a dictionary object containing all data from the page contents and
    YAML frontmatter.
    """
    # Pages
    divided = data.split('---')
    #print(len(divided))
    #print(divided)
    y_data = yaml.safe_load(divided[1])
    #print(type(y_data))
    #print(y_data)

    # Some stub pages may not have content
    if divided[2]:
        y_data['content'] = divided[2]

    #parsed_yaml = yaml.load(y_data)

    # Run page summaries through commonmark?
    if 'summary' in y_data.keys():
        y_data['summary'] = commonmark.commonmark(y_data['summary'])

    # Also need to process datetime
    if 'date' in y_data.keys():

        # There is a strange behavior in YAML that converts dates to
        # <datetime> objects if there are no quotes around them.

        # Need to specify in docs that date strings in page frontmatter
        # SHOULD NOT BE QUOTED. Then the datetime conversion works
        # properly. Will NOT implement switching with
        # `type(y_data['date'])`.


        #print(type(y_data['date']))
        #print(y_data['title'])

        # NOTE: If datetime object generation is found to be
        # inconsistant, uncomment the line below to generate a datetime
        # object with a more rigid format
        #page_date = datetime.strptime(y_data['date'], "%Y-%m-%d %H:%M:%S")

        # And comment out this line
        page_date = y_data['date']

    else:

        # If page does not have a date, make one
        page_date = datetime.now()
        y_data['date'] = datetime.now()

    # Break up the datetime into its components for use in templates
    y_data['year'] = page_date.strftime("%Y")
    y_data['month'] = page_date.strftime("%m")
    y_data['day'] = page_date.strftime("%d")
    y_data['hour'] = page_date.strftime("%H")
    y_data['minute'] = page_date.strftime("%M")

    # Month and day names
    y_data['monthName'] = page_date.strftime("%B")
    y_data['monthNameShort'] = page_date.strftime("%b")
    y_data['dayName'] = page_date.strftime("%A")
    y_data['dayNameShort'] = page_date.strftime("%a")

    # If page has no template defined, use the default
    if 'template' not in y_data.keys():
        y_data['template'] = "default"

    # Make sure every page has a type key:
    if 'type' not in y_data.keys():
        y_data['type'] = "default"


    return y_data

def gen_page_types(page_list):
    """ Splits a list of pages into a dictionary with a key for each page.

    Arguments:
    page_list -- List pages to operate on

    Returns a dictionary with a key for each page type. Each page type has the value of a list.
    """

    # Start by grabbing a list of types
    p_types = []
    for p in page_list:
        p_types.append(p['type'])

    # De-dup
    p_types = list(set(p_types))

    # Add keys to the type dictionary
    p_type_dict = {}
    for t in p_types:
        #print(t)
        p_type_dict[t] = []

        for p in page_list:
            if p['type'] == t:
                p_type_dict[t].append(p)

        #print(len(p_type_dict[t]))

    #for p in p_type_dict['default']:
        #print(p['title'])

    # Return
    return p_type_dict


def read_page(in_file):
    """ Reads a page file and converts it into a dictionary with split_yaml().

    Arguments:
    in_file -- The file to read in.

    Returns a dictionary containing page data.
    """
    global SITE_VARS

    with open(in_file) as f:
        page_data = f.read()

    page_dict = split_yaml(page_data)

    # Combine the site vars with page vars
    #for k in site_vars:
    #   page_dict[k] = site_vars[k]
        #print("{0}: {1}".format(k, site_vars[k]))

    #print(page_dict)

    # Fix tags
    new_tags = []
    if 'tags' in page_dict.keys():
        for t in page_dict['tags']:
            n = {}
            n['name'] = t
            n['link'] = SITE_VARS['siteRoot'] + "tags/{}/index.html".format(t)
            new_tags.append(n)

    page_dict['tags'] = new_tags

    # Same song and dance for categories
    new_cats = []
    if 'categories' in page_dict.keys():
        for c in page_dict['categories']:
            d = {}
            d['name'] = c
            d['link'] = SITE_VARS['siteRoot'] + "categories/{}/index.html".format(c)
            new_cats.append(d)

    page_dict['categories'] = new_cats

    # Add keywords and description if they don't exist
    # The description is used for <meta> tags in the generated HTML
    if 'description' not in page_dict:
        # Try to use the summary
        if 'summary' in page_dict:
            page_dict['description'] = page_dict['summary']

        # Else, you the site-wide fallback
        else:
            page_dict['description'] = SITE_VARS['siteDescription']

    if 'keywords' not in page_dict:
        page_dict['keywords'] = SITE_VARS['siteDefaultKeywords']


    # We need to expose plain list items to Mustache.
    # List of reserve YAML fields
    reserved_fields = ['tags', 'categories', 'keywords']

    # Iterate over page_dict keys
    for key, value in page_dict.items():
        # If the key is NOT in the reserved_fields, check the value
        if key not in reserved_fields:
            if type(value) is list:
                new_list = []

                for i in value:
                    n = {}
                    n['name'] = i
                    new_list.append(n)

                page_dict[key] = new_list
                #print(page_dict)

    return page_dict


def write_page(page_data):
    """ Writes a page to page_data['output'] and creates the intermediate
    directories as necessary. Fails if specified template file does not exist
    in 'templates'. Page content is passed through Pystache and then Commonmark
    facilitates usage of Mustache variables within page content. Then the entire
    page is rendered with the Mustache template file.

    Arguments:
    page_data -- The data dictionary to process
    """
    global TEMPLATES
    global SITE_VARS
    tmpl_file_name = page_data['template'] + ".mustache"
    tmpl_path = os.path.join(TEMPLATES, tmpl_file_name)
    #print(tmpl_path)
    out_file = page_data['output']

    if os.access(tmpl_path, os.R_OK):
        #print("success")

        # Read the template file
        with open(tmpl_path) as t:
            template = t.read()

        # Combine site vars with page data
        for s in SITE_VARS:
            page_data[s] = SITE_VARS[s]

        # Pass content through Pystache first, and THEN Commonmark. This way,
        # Mustache style variables can be used INSIDE the Markdown files and
        # everything will render properly.

        # NOTE: Auto-generated pages like tags and categories usually don't
        # have content.

        if 'content' in page_data.keys():
            page_data['content'] = pystache.render(page_data['content'], page_data)
            page_data['content'] = render_cmark(page_data['content'])

        # Need to tell Pystache where to find partials
        myRender = pystache.Renderer(search_dirs=TEMPLATES)


        # Render the template
        output = myRender.render(template, page_data)

        # Create the path to the file if it doesn't exist
        os.makedirs(os.path.dirname(out_file), exist_ok=True)

        # Copy page assets directory
        if 'assets' in page_data.keys():
            copy_path(page_data['assets_src'], page_data['assets_dest'])

        # Write output to a file
        #print(output)
        with open(out_file, 'w') as f:
            f.write(output)

    else:
      print("Failure! Template file {} does not exist or can not be read.".format(tmpl_path))


def content_walker(content_dir):
    """ Walks through the content directory and assembles a list of dictionary
    objects.

    Arguments:
    content_directory -- The directory of Markdown files to operate on.

    Returns a list of dictionaries, one per page.
    """
    page_list = []

    if os.access(content_dir, os.R_OK):
        #print("success")
        for subdir, dirs, files in os.walk(content_dir):

            for f in files:

                # Only operate on MD files
                f_path = os.path.join(subdir, f)
                if str(f_path).endswith('.md'):
                    #print("f_path: {}".format(f_path))
                    #print("subdir: {}".format(subdir))
                    #print("f: {}".format(f))

                    # Slug is simply file name without extension.
                    slug = str(f).split('.md')[0]
                    #print(slug)

                    # Trim the subdir down to content + OS separator
                    stub = subdir[subdir.find('content'):]
                    stub = stub.replace('content', '')
                    stub = stub.replace(os.sep, '')
                    #print("second", stub)

                    # If stub is empty, make it a forward slash
                    if stub == '':
                        stub = "/"

                    #print("stub:", stub)
                    # Dirty partial URL
                    dirty_url = "{}{}/{}/".format(SITE_VARS['siteRoot'], stub, slug)

                    # Clean the triple slash
                    partial_url = dirty_url.replace("///", "/")


                    # Collect page data
                    page_dict = read_page(f_path)

                    # Add the slug
                    page_dict['slug'] = slug


                    # If there's and assets directory, collect it
                    assets = slug + "-assets"
                    assets_dir = os.path.join(subdir, assets)
                    #print(assets_dir)
                    #print(assets)
                    if os.access(assets_dir, os.R_OK):
                        #print("Print assets confirmed.")
                        page_dict['assets_src'] = assets_dir
                        #print("assets src: {}".format(assets_dir))

                        # Need to specify the output for assets
                        page_dict['assets_dest'] = str(os.path.join(subdir, slug, "assets")).replace('content', 'output')
                        #print("assets dest: {}".format(page_dict['assets_dest']))

                        # Also need to specify the assets link
                        asset_url = partial_url + "assets"
                        #print("assets url: {}".format(asset_url))
                        page_dict['assets'] = asset_url
                        #print(asset_url)


                    # Need to keep tack of output path
                    if str(f) == 'index.md':

                        # Need to make a small exception for the home page
                        output_path = str(os.path.join(subdir, "index.html"))
                    else:
                        output_path = str(os.path.join(subdir, slug, "index.html"))

                    # Need to replace 'content' with 'output'
                    output_path = output_path.replace('content', 'output')

                    #print("output: {}".format(output_path))
                    page_dict['output'] = output_path

                    # Assign the URL
                    page_dict['url'] = partial_url + "index.html"
                    #print("url:", page_dict['url'])

                    #print("page url: {}".format(page_dict['url']))

                    #print("Raw dump")
                    #print(page_dict)
                    #print("")
                    #print(page_dict.keys())

                    # Add the page data to array
                    page_list.append(page_dict)

        # Sort pages by date
        page_list = sort_pages_by_date(page_list)

        # Return the page list
        return page_list

    else:
        print("Unable to read content directory")
        sys.exit(0)


# Build article page archives
def archive_article_walker(page_list, site_vars):

    # Filter out everything that's NOT an article
    article_list = []

    for page in page_list:
        if page['type'] == 'article':
            article_list.append(page)

    # Start off by building a list of years as an anchor
    year_list = []

    for page in article_list:
        year_list.append(page['year'])

    # Strip duplicates
    year_list = list(set(year_list))

    # Prefix for page urls
    link_prefix = site_vars['siteRoot'] + "archive"

    # Start building the years list
    ar_dict = {}
    ar_dict['years'] = []
    for y in year_list:
        y_dict = {}
        y_dict['year'] = y
        y_dict['count'] = 0

        # Data for write_page()
        y_dict['title'] = "Archive {}".format(y)
        y_dict['url'] = "{0}/{1}/index.html".format(link_prefix, y)
        y_dict['output'] = os.path.join(OUTPUT, "archive", y, "index.html")
        y_dict['template'] = "archive-page"

        y_dict['pages'] = []

        month_list = []
        for page in article_list:
            if page['year'] == y:
                y_dict['count'] += 1
                month_list.append(page['month'])

                # Add to year pages
                y_dict['pages'].append(page)

        month_list = list(set(month_list))

        # Second level
        y_dict['months'] = []
        for m in month_list:
            monthTime = datetime.strptime("{} {} 01".format(y,m), "%Y %m %d")
            m_dict = {}
            m_dict['year'] = y
            m_dict['month'] = m
            m_dict['monthName'] = monthTime.strftime("%B")
            m_dict['days'] = []
            m_dict['pages'] = []

            # Data for write_page()
            m_dict['title'] = "Archive {0}/{1}".format(y, m)
            m_dict['url'] = "{0}/{1}/{2}/index.html".format(link_prefix, y, m)
            m_dict['output'] = os.path.join(OUTPUT, "archive", y, m, "index.html")
            m_dict['template'] = "archive-page"

            # Third level
            day_list = []
            for page in article_list:
                if page['year'] == y:
                    if page['month'] == m:
                        day_list.append(page['day'])
                        # Add to month pages
                        m_dict['pages'].append(page)

            day_list = list(set(day_list))
            for d in day_list:
                d_dict = {}
                d_dict['day'] = d
                d_dict['pages'] = []

                # Data for write_page()
                d_dict['title'] = "Archive {0}/{1}/{2}".format(y, m, d)
                d_dict['url'] = "{0}/{1}/{2}/{3}/index.html".format(link_prefix, y, m, d, "index.html")
                d_dict['output'] = os.path.join(OUTPUT, "archive", y, m, d)
                d_dict['template'] = "archive-page"

                # Append all dictionary items
                m_dict['days'].append(d_dict)

            y_dict['months'].append(m_dict)

        ar_dict['years'].append(y_dict)

#    print(ar_dict.keys())
#
#    for y in ar_dict['years']:
#        print(y.keys())
#        for m in y['months']:
#            print(m.keys())
#            for d in m['days']:
#                print(d.keys())


    # Add page data for index
    ar_dict['title'] = "Archive"
    ar_dict['url'] = "{0}/index.html".format(link_prefix)
    ar_dict['output'] = os.path.join(OUTPUT, "archive", "index.html")
    ar_dict['template'] = "archive-index"


    return ar_dict

def write_archive_pages(archive):
    """ Writes the archive pages
    """

    # First, the index page, which takes the root of the dict
    write_page(archive)

    # Now dive into the years
    for y in archive['years']:
        y['span'] = y

        write_page(y)
        for m in y['months']:
            m['span'] = m
            write_page(m)

            # I rarely do multiple posts per day
            #for d in m['days']
            #   write_page(d)



# Collect page categories
def cat_walker(page_list, site_vars):
    """ Builds a list of category dictionaries. Each dictionary contains a full
    list of pages that have that category.

    Arguments:
    page_list -- List of page data dictionaries to operate on.
    site_vars -- A dictionary of site variables to process.

    Returns list dictionaries for each category found.
    """

    cat_list = []

    for p in page_list:
        if 'categories' in p:
            for c in p['categories']:
                cat_list.append(c['name'])

    # Remove duplicates in the list
    no_dups = list(set(cat_list))
    #print(no_dups)

    # convert to a list of dictionaries
    cat_dict_list = []
    for n in no_dups:
        cat_dict = {}
        cat_dict['name'] = n
        cat_dict['count'] = 0
        cat_dict['pages'] = []

        # Get the tag link
        link = site_vars['siteRoot'] + "categories/" + n + "/index.html"

        cat_dict['url'] = link

        # Add information so that write_page() can render the page
        cat_dict['title'] = n
        cat_dict['output'] = os.path.join(OUTPUT, "categories", n, "index.html")
        cat_dict['template'] = 'cat-page'

        # Add to the list
        cat_dict_list.append(cat_dict)

    # Build up a list of dictionaries, one per category
    for c in cat_dict_list:
        for p in page_list:
            if 'categories' in p:
                for cat in p['categories']:
                    if cat['name'] == c['name']:
                        c['count'] += 1
                        c['pages'].append(p)

    # Alpha sort by default
    def sortFunc(e):
        return e['name']

    cat_dict_list.sort(key=sortFunc)

    # Sort the list of categories depending on config options.
    if site_vars['siteCategorySort'] == 'number':
        def sortFunc(e):
            return e['count']

        cat_dict_list.sort(reverse=True, key=sortFunc)

#    for c in cat_dict_list:
#        print("cat name: {}".format(c['name']))
#        print("cat count: {}".format(c['count']))
#        print("cat url: {}".format(c['url']))
#        print("cat pages: {}".format(len(c['pages'])))
#        print("")

    # Return the new category list
    return cat_dict_list


# Collect page tags
def tag_walker(page_list, site_vars):
    """ Builds a list of tag dictionaries. Each dictionary contains a full list
    of pages that have that tag.

    Arguments:
    page_list -- List of page data dictionaries to operate on.
    site_vars -- A dictionary of site variables to process.

    Returns list dictionaries for each tag found.
    """

    global OUTPUT

    tag_list = []

    for p in page_list:
        if 'tags' in p:
            #print("Found tags")
            #print(p['tags'])

            # First gather up all of the tags
            for t in p['tags']:
                tag_list.append(t['name'])

    # Remove duplicates in the list
    no_dups = list(set(tag_list))
    #print(no_dups)

    # convert to a list of dictionaries
    tag_dict_list = []
    for n in no_dups:
        tag_dict = {}
        tag_dict['name'] = n
        tag_dict['count'] = 0
        tag_dict['pages'] = []

        # Get the tag link
        link = site_vars['siteRoot'] + "tags/" + n + "/index.html"

        tag_dict['url'] = link

        # Set title, output, and template so the data can be passed to write_page()
        tag_dict['title'] = n
        tag_dict['output'] = os.path.join(OUTPUT, "tags", n, "index.html")
        tag_dict['template'] = 'tag-page'

        # Add to the list
        tag_dict_list.append(tag_dict)

    # Build up a list of dictionaries, one per tag
    for t in tag_dict_list:
        for p in page_list:
            if 'tags' in p:
                for tag in p['tags']:
                    if tag['name'] == t['name']:
                        t['pages'].append(p)
                        t['count'] = len(t['pages'])

    # Alpha sort by default
    def sortFunc(e):
        return e['name']

    tag_dict_list.sort(key=sortFunc)

    # Now sort the tag list depending on configuration options
    if site_vars['siteTagSort'] == 'number':
        def sortFunc(e):
            return e['count']

        tag_dict_list.sort(reverse=True, key=sortFunc)

#    for t in tag_dict_list:
#        print("tag name: {}".format(t['name']))
#        print("tag count: {}".format(t['count']))
#        print("tag url: {}".format(t['url']))
#        print("tag pages: {}".format(len(t['pages'])))
#        print("")

    # Return the new tag list
    return tag_dict_list


def gen_cat_index():
    """ Generates data for the main category page index. Gives write_page() the correct data to render the page.
    """

    global OUTPUT
    global SITE_VARS

    page_data = {}
    page_data['template'] = "cat-index"
    page_data['url'] = SITE_VARS['siteRoot'] + "categories/index.html"
    page_data['output'] = os.path.join(OUTPUT, "categories", "index.html")
    page_data['title'] = "Categories"

    return page_data

def gen_tag_index():
    """ Generates data for the main tag page index. Gives write_page() the correct data to render the page.
    """

    global OUTPUT
    global SITE_VARS

    page_data = {}
    page_data['template'] = "tag-index"
    page_data['url'] = SITE_VARS['siteRoot'] + "tags/index.html"
    page_data['output'] = os.path.join(OUTPUT, "tags", "index.html")
    page_data['title'] = "Tags"

    return page_data


def gen_tag_page():
    """ Generates data to use for each of the tag pages.
    """

    global OUTPUT
    global SITE_VARS

    page_data = {}
    page_data['template'] = "tag-page"
    page_data['url'] = SITE_VARS['siteRoot'] + "tags/index.html"
    page_data['output'] = os.path.join(OUTPUT, "tags", "index.html")
    page_data['title'] = "Tags"

    return page_data


def build_site():
    """ Build the website. Takes no arguments.
    """
    global SITE_VARS
    content_dir = CONTENT
    #out_file = sys.argv[2]

    #page_data = read_page(in_file, SITE_VARS)
    #write_page(page_data, out_file)

    # NOTE: Pages are sorted by date with sort_pages_by_date() in
    # content_walker(). Once the page list is sorted, it remains sorted
    # even after processing with tag_walker() and cat_walker().
    page_list = content_walker(content_dir)
    #for p in page_list:
    #   print(p['date'])

    tag_list = tag_walker(page_list, SITE_VARS)
#    for t in tag_list:
#        print(t['name'])
#        for p in t['pages']:
#            print(p['date'])
#
#        print("")


    category_list = cat_walker(page_list, SITE_VARS)

    ar_dict = archive_article_walker(page_list, SITE_VARS)

    # Add vars to SITE_VARS
    SITE_VARS['siteTags'] = tag_list
    SITE_VARS['siteCategories'] = category_list
    SITE_VARS['siteArticleArchive'] = ar_dict
    SITE_VARS['sitePages'] = gen_page_types(page_list)
    SITE_VARS['sitePages']['all'] = page_list

    # Remove the output directory if it exists. write_page() will recreate it.
    if os.path.exists(OUTPUT):
        shutil.rmtree(OUTPUT)

    # NOTE: Because of the way copy_path() works, this bit of code has to fire
    # first.

    # Copy template static files to output.
    src = os.path.join(TEMPLATES, 'static')
    if os.access(src, os.R_OK):
        print("Copying template assets '{}'...".format(src))
        copy_path(src, OUTPUT)


    print("Generating pages...")
    # Generate the pages
    for p in SITE_VARS['sitePages']['all']:
        #print(p['title'])
        #print(p['output'])
        write_page(p)

    if (SITE_VARS['siteGenLunrJson']):
        genLunrJson(SITE_VARS['sitePages']['all'])


    if len(SITE_VARS['siteTags']) > 0:
        # Write individual tag pages
        for t in SITE_VARS['siteTags']:
            write_page(t)

        # Write the tag index page
        write_page(gen_tag_index())


    # Only generate if there are categories to write.
    if len(SITE_VARS['siteCategories']) > 0:
        # Write the category pages
        for c in SITE_VARS['siteCategories']:
            write_page(c)

        # Category index page
        write_page(gen_cat_index())

    # Archive pages
    write_archive_pages(SITE_VARS['siteArticleArchive'])

    # Tell the user we're done
    print("Done!")
    print("Processed {} pages.".format(len(SITE_VARS['sitePages']['all'])))

def display_help():
    """ Prints a help message.
    """
    print("Valid commands are:")
    print("build -- Build the site in the current directory")
    print("version -- Print version information and exit")
    print("help  -- Show this message")


## Main
def main():
    global SITE_VARS
    # First check for config file
    if os.access(CONFIG, os.R_OK):
        with open(CONFIG) as f:
            contents = f.read()

        SITE_VARS = yaml.full_load(contents)

        # Check the tag and category sorting options for valid values.
        if SITE_VARS['siteTagSort'] != 'number' and SITE_VARS['siteTagSort'] != 'alpha':
            print("Config value 'siteTagSort' is not valid!")
            print("Please specify 'number' or 'alpha'")

        elif SITE_VARS['siteTagSort'] != 'number' and SITE_VARS['siteTagSort'] != 'alpha':
            print("Config value 'siteTagSort' is not valid!")
            print("Please specify 'number' or 'alpha'")

        else:
            # Then run the program.
            if len(sys.argv) > 1:
                if sys.argv[1] == 'build':
                    build_site()
                elif sys.argv[1] == 'help':
                    display_help()
                elif sys.argv[1] == 'version':
                    print(VERSION)
                else:
                    print("Invalid command")
                    print("Try 'help'")
            else:
                print("Must provide a command")
                print("Try 'help'")
                #in_file = sys.argv[1]

    else:
        print("Config file not found! Attempting to generate one.")
        with open(CONFIG, 'w') as f:
            f.write(DEFAULT_CONFIG)

if __name__ == "__main__":
    main()
