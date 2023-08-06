========
Articles
========

Articles is mezzanine content module which provide article content which
integrate together richtextopage, gallery, add link to other pages utility
and sections extension (for improve styling, grouping, etc.). Mezzanine 
organize pages in tree structure. Sections  exted to use it as graph 
(for example, we can select content from different branches).

Detailed documentation is in the "docs" directory.

Quick start
-----------

1. Add "articles" to your INSTALLED_APPS setting in mezzanine project
   like this::

    INSTALLED_APPS = (
        ...
        'articles',
    )

2. Run `python manage.py migrate` to create the articles models.

3. Start the development server and visit http://127.0.0.1:8000/admin/
   to create new article.

4. Visit http://127.0.0.1:8000/ to check your work.
