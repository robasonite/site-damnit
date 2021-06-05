# Site Damnit!

Got Python, will build site.


## Features

- Per-page asset directories and easy asset linking
- Markdown or HTML for writing content
- Mustache for templates
- YAML for frontmatter and configuration
- Embeddable per-page custom frontmatter



## Latest update

### 2021-06-05:

Version bump to 0.0.4. Added a "Getting Started" section to the README. Added a new variable to `config.yaml` to enable or diable blog mode. Setting `blogMode: false` disables the generation of tag, category, and archive pages.



## Project goal

The goal of this project was to build a basic static site generator with as few dependencies as possible. Just Python 3, [PyYAML](https://pyyaml.org/wiki/PyYAMLDocumentation), [Commonmark](https://pypi.org/project/commonmark/), and [Pystache](https://github.com/defunkt/pystache).


## Why?

I've used various static site generators to throw together small sites and blogs. The same issues kept popping up over and over:

* Dependency X can't be installed.
* Embedded "shortcut codes" made migrating content difficult.
* "It's not a bug, it's a feature! RTFM man!" said community members and/or developers.
* Themes with templates that included other templates that included other templates that included other templates that included....
* Plugin/extension/theme developers that didn't update their stuff to work with the latest stable release of XYZ.
* Deceptively simple installation and setup instructions. *"Just run `npm install xyz`, and instant website!"* Sound familiar?
* Silent failures and missing output directories.


Just about every static site generator I've tried has had these problems (and many more), so I just wrote my own.

## This is NOT a complete solution!

Site Damnit only builds out the HTML files of your site and copies a few asset directories. That's *all* it will ever do. If you want to pre-process JavaScript or CSS files, you'll have to install additional tools and write your own custom build script. The included build script, `server.sh`, should provide a decent example to build on. The example site is set up to use [Bulma](https://bulma.io/) and [Font Awesome Free](https://github.com/FortAwesome/Font-Awesome) via Terser and Sass.


## Getting started:

### Step 1: Installation

**NOTE:** Only tested on Linux systems with Python 3.7x.

First, clone this repository and rename the directory:

``` shell
git clone https://github.com/robasonite/site-damnit
mv site-damnit <your_site_name_here>
```

Then install the dependencies with one of the following methods:

Install packages to $HOME (Linux only):

``` shell
cd <your_site_name_here>
pip install --user -r requirements.txt
```

Install packages into a `virtualenv`:

``` shell
python -m virtualenv env_name
. env_name/bin/activate
cd <your_site_name_here>
pip install -r requirements.txt
```


#### Optional: Install Sass and Terser

The example `server.sh` file uses Sass to pre-process and compress CSS, and Terser to compress and mangle JavaScript. These programs are *not required* to use Site Damnit, so the lines that call them can be safely commented out. The `server.sh` file is merely an example build script that runs Site Damnit and starts the local HTTP server module (`http.server`) that Python ships with. You are expected to modify `server.sh` (or replace it entirely) to meet your needs.


#### Optional: Set up version control

Before you change the default configuration, build script, templates, and other stuff, it would be a good idea set up *version control*. That way, you can always return to a known working state when something goes wrong. Version control can be set up in one of two ways:

1. Create a new branch for your site:

``` shell
cd <your_site_name_here>
git branch my_site
git checkout my_site
```

2. Create a new version control repository for your site:

``` shell
cd <your_site_name_here>
rm -rf .git

# You don't have to use Git. This is just an example.
git init
```


### Step 2: Configuration

Edit `config.yaml`, which should be self explanatory. Change the default values to whatever you want. One thing to keep in mind is that *you are not limited to the default set of variables*. Any piece of information you want to use in your site templates can be specified here:

``` yaml
variableName: value
siteMyCustomVariable: Your text here
siteMyListLimit: 5
siteMyFavorites:
- Movie I like
- Car I Like
- etc
```

If you need a primer on YAML, go here: <https://yaml.org/spec/1.1/#id857168>

Once you specify a variable in `config.yaml`, it becomes available to your Mustache templates. You'll find those files under `templates/`. Depending on what you want to build, some of them can be deleted. Here is a list of the essential "hard coded" ones:

``` shell
base_head
base_tail
default
archive-index
archive-page
cat-index
cat-page
tag-index
tag-page
```

By default, Site Damnit is blog-aware because that's what I made it for. If you don't want a blog, you can turn it off in `config.yaml`.


### Step 3: Edit templates to suit your needs

Basically, I chose Mustache as a template language because I didn't need anything beyond the ability to replace chunks of text. For a nice primer, go to <https://mustache.github.io/> and read the manual. As for integrating custom variables from `config.yaml` into your templates, look at these code samples:

``` mustache
<!-- base_head.mustache -->
<a class="navbar-item" href="{{{siteRoot}}}">
	{{siteName}}
</a>
...
```

``` yaml
# config.yaml
siteName: Name of your site
siteRoot: /
...
```

Not all of the available variables come from `config.yaml`. Site Damnit creates several internal variables when it runs and makes those variables available to templates. For examples of what's possible, read the default template files.

Promiment internal variables include:

- `siteTags`: A list of every *blog tag* found on the site. Every tag has a list of all the pages marked with that tag.
- `siteCategories`: The same thing for *blog categories*.
- `siteArticleArchive`: Blog archive for articles/posts. The order is *Year -> Month -> Day*, where every year, month, and day contains a full list of the pages that belong to it.
- `sitePages`: A list of every page on the site, and a list of pages belonging to every *page type* found on the site.


### Step 4: Start adding and editing content

All of the pages for your site are stored in `content/`. The most important file in that directory is `home.md`, which is the home page of your site. Page files consist of two parts: *Frontmatter* and *Content*. Here is an example:

```
---
title: About
date: 2020-08-19 01:01:01
---

This is the About page of your site! Put whatever you want in here.
```

The frontmatter section is written in YAML, which sits in a block separated from the content by a pair of 3-dash lines (`---`). Here's a list of important frontmatter variables:

``` yaml
title: The title of the page
date: YYYY-MM-DD HH:mm:ss
template: my-template
type: article
tags:
 - list
 - of
 - blog
 - tags
categories:
 - page
 - categories
 - here
```

At the bare minimum, all pages should have a `title` and a `date`. Any page that does not specify a `template` in the frontmatter will use the `default` template. Likewise, pages without a `type` will be assigned `default`. Beyond that, you can specify any custom variables you want to use on your page.

After the second 3-dash line is where you type your content, which can be either Markdown, HTML, or a mix of the two. Because all pages are processed with Mustache, it's possible to use site-wide and page-wide variables in your content.

As for how pages are generated, the page path is based on the *filename*, not the title. The title and URL of each page can be used individually in Mustache templates.


**A note on page assets**

Site Damnit supports per-page asset management. That means every page can have its own `*-assets` directory. Let's say you make a file called `all-about-cats.md` and you want that page to have a bunch of cat pictures. The cat pictures won't be used anywhere else on the site. If you make a directory called `all-about-cats-assets` and put it in the same directory as the Markdown file, you'll be able to easily link your cat pictures like this:

```
![white kitten]({{assets}}/white_kitten.png)
```

The special `{{assets}}` variable allows easier access to page assets without having to type the full file path.


**A note on page types and templates**

Page *types* are how Site Damnit separates pages into internal lists. The blog-aware features rely on the type `article` when generating category, tag, and archive pages. The `base_head.mustache` file is an example of how one of these internal lists can be used to auto-generate a menu. Pages of the same type can use different templates for more flexibility.


### Step 5: Generate

Once you get done adding content, modifying/adding/removing templates, and customizing your CSS, run `python damnit.py build`. Site Damnit will generate an output directory that you can copy to a server any way you see fit. **Do not store ANYTHING in the output directory**! Site Damnit erases the contents of this directory every time it runs the `build` command. There is no cache or database.


## No *proper* documentation yet

There isn't any proper documentation available at the moment, but it's only about 1000 lines long. Look at the included example site (*content* and *templates* directories) and you should catch on pretty quick. For configuration, look at `config.yaml`. Anything you add to that file can be used in your template and content files, as long as it's valid YAML.


