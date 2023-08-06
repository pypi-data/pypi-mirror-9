===================
Guzzle Sphinx Theme
===================

Sphinx theme used by Guzzle: http://guzzlephp.org

Installation
============

Install via pip::

    $ pip install guzzle_sphinx_theme

or if you have the code checked out locally::

    $ python setup.py install

Configuration
=============

Add the following to your conf.py:

.. code-block:: python

    import guzzle_sphinx_theme

    # Adds an HTML table visitor to apply Bootstrap table classes
    html_translator_class = 'guzzle_sphinx_theme.HTMLTranslator'
    html_theme_path = guzzle_sphinx_theme.html_theme_path()
    html_theme = 'guzzle_sphinx_theme'

    # Register the theme as an extension to generate a sitemap.xml
    extensions.append("guzzle_sphinx_theme")

    # Guzzle theme options (see theme.conf for more information)
    html_theme_options = {

        # Set the name of the project to appear in the nav menu
        "project_nav_name": "Project Name",

    }

There are a lot more ways to customize this theme, as this more comprehensive example shows:

.. code-block:: python

    import guzzle_sphinx_theme

    # Adds an HTML table visitor to apply Bootstrap table classes
    html_translator_class = 'guzzle_sphinx_theme.HTMLTranslator'
    html_theme_path = guzzle_sphinx_theme.html_theme_path()
    html_theme = 'guzzle_sphinx_theme'

    # Register the theme as an extension to generate a sitemap.xml
    extensions.append("guzzle_sphinx_theme")

    # Guzzle theme options (see theme.conf for more information)
    html_theme_options = {

        # Set the path to a special layout to include for the homepage
        "index_template": "special_index.html",

        # Set the name of the project to appear in the nav menu
        "project_nav_name": "Project Name",

        # Set your GitHub user and repo to enable GitHub stars links
        "github_user": "my_github_user",
        "github_repo": "my_github_repo",

        # Set your Disqus short name to enable comments
        "disqus_comments_shortname": "my_disqus_comments_short_name",

        # Set you GA account ID to enable tracking
        "google_analytics_account": "my_ga_account",

        # Set a custom class to add to the navbar (e.g. navbar-inverse)
        "navbar_class": "",

        # Path to a touch icon
        "touch_icon": "",

        # Specify a base_url used to generate sitemap.xml links. If not
        # specified, then no sitemap will be built.
        "base_url": ""

        # Allow a separate homepage from the master_doc
        homepage = index

        # Allow the "Table of Contents" page to be defined separately from "master_doc"
        tocpage = Contents

        # Allow the project link to be overriden to a custom URL.
        projectlink = http://myproject.url

        # Accept a list of URLs for the nav bar.
        "navlinks": {
            "Blog": "http://blog.myproject.url”
        },

    }

Customizing the layout
======================

You need to customize the navigation links of "layout.html" using a theme
customization. "layout.html" contains several blocks that can be
overridden or extended.

Place a "layout.html" file in your project's "/_templates" directory.

.. code-block:: bash

    mkdir source/_templates
    touch source/_templates/layout.html

Then, configure your "conf.py":

.. code-block:: python

    templates_path = ['_templates']

Finally, edit your override file "source/_templates/layout.html":

::

    {# Import the theme's layout. #}
    {% extends "!layout.html" %}

    {# Customize the links in the main nav menu #}
    {%- block nav_links %}
    <li><a href="{{ pathto(master_doc) }}">Home</a></li>
    <li><a href="{{ pathto('docs') }}">Docs</a></li>
    <!-- etc... -->
    {%- endblock %}

If you are using Readthedocs, then you might run into an issue where they don't
currently allow you to extend layout.html. If you only need to add links to the
menu, then you can just create a nav_links.html file in your _templates
directory that includes li nodes. The contents of this file will be included
when building the docs.
