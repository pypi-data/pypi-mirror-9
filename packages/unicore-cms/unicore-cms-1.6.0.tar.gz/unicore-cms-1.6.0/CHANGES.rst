CHANGELOG
=========

1.6.0
-----
- Add branded 404 page
- Allow reading of `es.host` from config

1.5.2
-----
- Refactor Search templates

1.5.1
-----
- Ensure list of languages in change page is sorted

1.5.0
-----
- Change language selector to allow featured languages

1.4.2
-----
- Allow querystring-less locale url

1.4.1
-----
- Fix tests breaking because of latest elasticsearch

1.4.0
-----
- Add support for Google Analytics tracking
- Add backend support for search.

1.3.1
-----
- Ensure localisation is fastforwarded

1.3.0
-----
- Add localisation support to schema

1.2.2
-----
- Change order of get_image_url params

1.2.1
-----
- Use `image_host` from json

1.2.0
-----
- Add image support to view

1.1.1
-----
- Use custom locale negotiator

1.1.0
-----
- Added image field to model
- Add fallback for Swahili and English UK

1.0.13
-----
- Use not_analyzed for language field

1.0.12
-----
- Ensure `get_page` returns None instead of 404

1.0.11
-----
- Ensure sensible default for ordering pages (default: position)

1.0.10
-----
- Ensure featured pages in category on homepage are ordered by position (ascending)

1.0.9
-----
- Ensure featured pages in category on homepage are ordered by position

1.0.8
-----
- Autodeployment with travis - attempt 2

1.0.7
-----
- Autodeployment with travis - attempt 1

1.0.6
-----
- Enforce ordering for pages and categories using `position`

1.0.5
-----
- Added date formatting helper

0.6.3
-----
- Redirect to homepage after changing language

0.6.2
-----

- Better wrapper around repos & workspaces to make moving away from
  pygit2 easier.

0.6.1
-----

- Fix for workspace caching

0.6.0
-----

- Cache workspace to reduce number of open files

0.5.0
-----

- Views now return actual objects instead of dictionaries
  to the template contexts.

0.4.3
-----
-  Fixed bug when filtering multiple language pages by slug

0.4.2
-----
-  Pages now render markdown

0.4.1
-----
-  Change default cache duration to 10mins

0.4.0
-----
-  Allow content to be featured on homepage

0.3.2
-----
-  Ensure setting locale always redirects

0.3.1
-----
-  Fix error when checking language for cached category/page

0.3.0
-----
-  Allow content to be filtered by language selection

0.2.8
-----
-  Add support for flat pages

0.2.7
-----
-  Add caching to `get_featured_category_pages`

0.2.6
-----
-  Added sensible default for available_languages

0.2.5
-----
-  Added support for translations

0.2.4
-----
-  Allow top nav to be global variable

0.2.2
-----
-  Use `utils.get_workspace()` to avoid duplication

0.2.2
-----
-  Fix development.ini file

0.2.1
-----
-  Bump required version for praekelt-python-gitmodel

0.2
---
-  Added `git.content_repo_url` for cloning when app starts

0.1
---
-  Initial version
