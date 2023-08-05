========
imagebot
========

A web bot to scrape images from websites.

Features
========

* Supported platforms: Linux / Python 2.7.
* Uses scrapy web crawling framework.
* Maintains a database of all downloaded images to avoid duplicate downloads.
* Optionally, it can scrape only under a particular url, e.g. scraping "http://website.com/albums/new" with this option will only download from new album.
* You can specify minimum image size to be downloaded.
* Scrapes through javascript popup links.
* Live monitor window for displaying images as they are scraped.

Usage
=====

**crawl commands:**

* Scrape images from http://website.com::

	imagebot crawl http://website.com

* Scrape images from http://website.com while allowing images from a cdn such as amazonaws.com (add multiple domains with comma separated list)::

	imagebot crawl http://website.com -d amazonaws.com

* Specify image store location::

	imagebot crawl http://website.com -is /home/images

* Specify minimum size of image to be downloaded (width x height)::

	imagebot crawl http://website.com -s 300x300

* Stay under http://website.com/albums/new::

	imagebot crawl http://website.com/albums/new -u

* Launch monitor windows for live images::

	imagebot crawl http://website.com -m

* Set user-agent::

	imagebot crawl http://website.com -a "my_imagebot(http://mysite.com)"

* For more options, get help::

	imagebot crawl -h

**clear commands:**

* Clear cache::
	
	imagebot clear --cache

* Remove image metadata from database::

	imagebot clear --db website.com

* Get help::

	imagebot clear -h

Dependencies
============

#. python-gi (Python GObject Introspection API) (if using monitor UI)

	On Ubuntu::
	
		apt-get install python-gi

#. scrapy (a powerful web crawling framework)

	It will be automatically installed by pip.

#. Pillow (Python Imaging Library)

	It will be automatically installed by pip.

Download
========

* PyPI: http://pypi.python.org/pypi/imagebot/
* Source: https://bitbucket.org/amol9/imagebot/

