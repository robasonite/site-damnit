# Template variable rules

1. All variables starting with `site_` are site-wide variables. They are available to all pages

2. All variables starting with `page_` are page-specific.

3. All variables starting with `env_` are environmental settings, such as which editor to use.


## Current `env_`:

* `env_editor`: Which text editor to use


## Current `site_`

* `site_pages`: A list of all the pages on the site. Each dictionary item includes:
  + `page_type`: Specify what type of page it is. Common values include "article", "page", "slideshow", etc.
  + `page_template`: The name of the page template to use, minus the file extension.
  + `page_title`: The title of the page.
  + `page_datetime`: The date and time the page was written.
  + `page_category`: The category of the page.
  + `page_tags`: A list of tags that apply to the page.

* `site_tags`: A list of tags used across all pages.
* `site_tag_<tag_name>`: Includes values for `<tag_name>`:
  + `<tag_name>`: Includes the unmodified tag name as it appears in `vars.json` for a given page.
  + `<tag_link>`: Link to the tag page using the stripped name, all spaces and special characters removed.
  + `<tag_count>`: The total number of pages site-wide that have the tag.

* `site_categories`: A list of categories used across all pages.
* `site_category_<category_name>`: Includes values for `<category_name>`:
  + `<category_name>`: Includes the unmodified category name as it appears in `vars.json` for a given page.
  + `<category_link>`: Link to the category page using the stripped name, all spaces and special characters removed.
  + `<category_count>`: The total number of pages site-wide that have the category.


## Current `page_`

* `page_type`: Specify what type of page it is. Common values include "article", "page", "slideshow", etc.
* `page_template`: The name of the page template to use, minus the file extension.
* `page_title`: The title of the page.
* `page_datetime`: The date and time the page was written.
* `page_category`: The category of the page.
* `page_tags`: A list of tags that apply to the page.

