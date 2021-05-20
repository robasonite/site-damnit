# Site Damnit!

Got Python, will build site.


## Features

- Per-page asset directories and easy asset linking
- Markdown or HTML for writing content
- Mustache for templates
- YAML for frontmatter and configuration
- Embeddable per-page custom frontmatter



## Latest updates

### 2021-05-19 RSS is here. Well, sort of.

Added another execption to page processing for `rss.md`. A template and example "stub page" have been added. This is an easy "poor man's" way of generating RSS feeds without touching the existing code. Also renamed `index.md` to `home.md`. If more RSS feeds are required, the section to change starts at line #580. I'm looking into a way to incorporate "page processing exceptions" into the YAML config file.



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


## No *proper* documentation yet

There isn't any proper documentation available at the moment, but it's only about 1000 lines long. Look at the included example site (*content* and *templates* directories) and you should catch on pretty quick. For configuration, look at `config.yaml`. Anything you add to that file can be used in your template and content files, as long as it's valid YAML.


## This is NOT a complete solution!

Site Damnit only builds out the HTML files of your site. That's *all* it will ever do. If you want to pre-process JavaScript or CSS files, you'll have to install additional tools and write your own custom build script. The included build script, `server.sh`, should provide a decent example to build on. The example site is set up to use [Bulma](https://bulma.io/) and [Font Awesome Free](https://github.com/FortAwesome/Font-Awesome) via Terser and Sass.
