# 2019-10-14 And so it begins

I have decided to do something incredibly stupid and time consuming by "sane person" standards, but something that will end up being useful nonetheless. I have a Hugo-powered blog I haven't updated in a few months. When I tried to update from version 0.55.6 to 0.58.3 and my home page template stopped working. I opened an issue on GitHub and **bep**, one of the developers working on Hugo, immediately closed it. His only message was to check the documentation, which I had already searched through. That's when I realized something.

Right now, as with most software, I rely on other people to write it. For desktop apps like Vim, Gimp, Inkscape, and desktop environments like XFCE, there is some semblance of leadership in the community and support from developers working on multiple distros. Such projects have been around for a long enough to gather some amount of stability. They don't just sprout new features over night, and they typically don't break things that affect a user's workflow or clash the user's chosen platform. As a result of steady but careful progress, these projects can frequently be found in the package repositories of a typical GNU/Linux distribution.

The same can not be said for most of the static site generators listed on the [StaticGen](https://www.staticgen.com) website. I actually switched away from Pelican a couple of years ago specifically because of template breakage between releases among other problems. Problems that it seems the rest of the people on Internet aren't keen on solving any time soon. Sometimes if you want something done right, you have to do it yourself. So I'm writing it right now in Python.

Why Python? Because it will be quicker to implement. There are a few minor problems with Python though. First, some of the functions are in odd places. The function to make a new directory is in the `os` module, but the function to copy files is in the `shutils` module. And then there are problems with speed. Fortunately, Cython and the `multiprocessing` module can help. I also discovered that there are ways to package Python apps for distribution. The question is, how many more warts like `shutils` vs `os` am I going to discover?

Regardless of the language used, this will be *my* program and it will eventually be distributed as a single binary like Hugo. Also, unlike Hugo, the default installation will already include a very basic working theme. I also want all of the documentation to be included with the binary. That way, I and future users can just run the `help` command and instantly launch a sort of pager in a terminal window, or launch the default web browser and serve it help pages. At least that's the plan.


# 2019-10-17 Progress

I can now collect all of the pages before rendering them! That means I can now have things like lists of posts on the home page! Good stuff. Soon I'll be ready to generate entire websites.


# 2019-10-18 Tag collection working

Started work on the `build_tag_pages()` function and finished the `collect_page_tags()` functions. I decided to make a new global variable called `PAGE_TAGS` to make tag page generation easier. I'm modifying the templates as I go. Right now, the `build_page()` function works as expected and the main content pages can be generated. Soon I will be able to generate lists of page links.


# 2019-10-23 Category page generation is working

And I also put in a check to make sure that there are tags and categories to process in the first place. Next step: sorting by date.


# 2019-10-24 List of pages on index.html!

I wrote a new function today called `collect_page_list_item()`. It pre-generates lists of pages assigns them to dynamically generated variables in `SITE_CONF` like `site_page_list_<target_key>_<target_val>` and `site_page_list_all`. Stick one of those between a couple of `<ul>` tags and watch the magic! I need to expand this function to allow setting a limit on the number of elements in a list. I think I can just put something like `site_page_list_limit` in `config.json` and use that.
