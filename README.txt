# Site Damnit!

Got Python 3, will build site.


## Project goal

The goal of this project is build a basic static site generator with as few dependencies as possible. Just Python 3 and [Pystache](https://github.com/defunkt/pystache). Here are some of the guiding principals:

2. Screw so-called "lightweight markup languages"
3. "Embedded frontmatter" is trash
5. Order and simplicity or die


## Why?

Over the past ten years, I've used various static site generators to throw together small sites and blogs. The same issues kept popping up over and over:

* Dependency X can't be installed.
* Fragmentation among various lightweight markup language implementations sometimes led to strange bugs.
* Embedded "shortcut codes" made migrating content difficult.
* Manual resource and outbound link checking was not fun. It sometimes took 15+ minutes to figure out where an image on a page came from.
* Themes with templates that included other templates that included other templates that included other templates that included....
* Templates with embedded logic that created more bugs to fix.
* Plugin/extension/theme developers that did not update their stuff to work with the latest stable release of XYZ.
* Deceptively simple installation and setup instructions. "Just run `npm install xyz`, and instant website!" Uh, no. That's not how works. That's *NEVER* how it really works.


Just about every static site generator I've tried has had these problems, and I've been thinking about how best to solve them for a long time. I finally decided to learn enough Python to write it myself. It was hard and frustrating work, but it was also very rewarding.


## How to write content

All "pages" in the source directory each get their own directory. A page directory contains the files `page.html` and `meta.json`. A page directory may optionally contain a directory called `resources`. All resources specific to that page (images, videos, etc) should be placed in the `resources` directory. The `page.html` file contains the entire contents of the page. The `meta.json` file contains things like the title, category, date, tags, and other metadata in JSON format. If you don't want to write your content in straight HTML, you can always copy markup generated with an external tool.


### JSON example

{
  "title": "My amazing page",
  "category": "Daily Tech",
  "tags": ["Web", "JavaScript", "ES6"],
  "date": "2019-10-01",
  "author": "John Doe",
  "custom_attribute", "define extra attributes as required"
}



## How templates work

Templates in Site Damnit are written with Mustache, but there are a few differences. For example, **I disabled template inheritance** and implemented *infinite loop* detection. 
