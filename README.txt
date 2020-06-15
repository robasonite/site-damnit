# Site Damnit!

Got Python, will build site.


## Project goal

The goal of this project was to build a basic static site generator with as few dependencies as possible. Just Python 3, [PyYAML](https://pyyaml.org/wiki/PyYAMLDocumentation), [Commonmark](https://pypi.org/project/commonmark/), and [Pystache](https://github.com/defunkt/pystache).


## Why?

I've used various static site generators to throw together small sites and blogs. The same issues kept popping up over and over:

* Dependency X can't be installed.
* Embedded "shortcut codes" make migrating content difficult.
* "It's not a bug, it's a feature! RTFM man!" say community members and/or developers.
* Themes with templates that include other templates that include other templates that include other templates that include....
* Plugin/extension/theme developers that don't update their stuff to work with the latest stable release of XYZ.
* Deceptively simple installation and setup instructions. "Just run `npm install xyz`, and instant website!"
* Support for either all of the features I don't need, or none of the ones I do.


Just about every static site generator I've tried has had these problems (and many more), so I just wrote my own.


## No *proper* documentation yet

There isn't any proper documentation available at the moment, but it's only about 1000 lines long. Look at the included example site (*content* and *templates* directories) and you should catch on pretty quick. For configuration, look at the `SITE_VARS` section towards the top of `damnit.py`.


## This is NOT a complete solution!

Site Damnit only builds out the HTML files of your site. If you want to pre-process JavaScript or CSS files, you'll have to install additional tools and write your own custom build script. The included build script, `server.sh`, should provide a decent example to build on. Terser and Sass have to be installed to make the script work as-is.
