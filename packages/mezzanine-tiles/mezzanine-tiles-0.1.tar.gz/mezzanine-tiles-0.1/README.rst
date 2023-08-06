=====
Tiles
=====

Articles is mezzanine content module which provide tile and section content which
which allow manage boxes/snipets etc. in our mezzanine cms. For example main
header slider which has some slides read content of every slide from tiles of
selected branch or section. Mezzanine organize pages in tree structure. Sections
exted to use it as graph (for example, we can select content from different branches).

Detailed documentation is in the "docs" directory.

Quick start
-----------

1. Add "tiles" to your INSTALLED_APPS setting in mezzanine project
   like this::

    INSTALLED_APPS = (
        ...
        'tiles',
    )

2. Run `python manage.py migrate` to create the tiless models.

3. Start the development server and visit http://127.0.0.1:8000/admin/
   to create new tile.

4. Visit http://127.0.0.1:8000/ to check your work.
