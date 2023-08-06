ps.releaser
===========

``ps.releaser`` provides several plugins for `zest.releaser`_.
The plugins are registered globally and can be activated if needed.


Available Plugins
=================


Exportig Diazo Themes as ZIP files
----------------------------------

Plone allows us to upload diazo themes as zip files.
This can be used when we don't have the permission to install our theme on the server as a python package (e.g. within a shared hosting environment).
``ps.releaser`` provides a hook which is run after the release has been done.
Use the following options in your ``setup.cfg`` to enable the ZIP file export::

    [ps.releaser]
    diazo_export.enabled = 1
    diazo_export.path = src/my/package/diazo_resources
    diazo_export.adjust_title = 1

diazo_export.enabled
    Activate or deactivate the export.

diazo_export.path
    Path relative from the package root to the folder containing the diazo resource files.

diazo_export.adjust_title
    Append the version number of the package to the title in the zipped ``manifest.cfg`` file.


Installation
============

Use in a buildout
-----------------

::

    [buildout]
    parts += releaser

    [releaser]
    recipe = z3c.recipe.scripts
    dependent-scripts = true
    eggs =
        ps.releaser
        my.package

If you want to use the latest development version from GitHub, add ``ps.releaser`` to your ``mr.developer`` source section::

    [buildout]
    extensions += mr.developer

    [sources]
    ps.releaser = git git@github.com:propertyshelf/ps.releaser.git


This creates the ``zest.releaser`` executabled in your bin-directory.
Create a release as you're used to::

    $ ./bin/fullrelease


Installation in a virtualenv
----------------------------

You can also install ``ps.releaser`` in a virtualenv.::

    $ pip install ps.releaser

You can also install the latest version of ``ps.releaser`` directly from GitHub::

    $ pip install -e git@github.com:propertyshelf/ps.releaser.git#egg=ps.releaser

Now you can use it like this (when releasing your package)::

    $ fullrelease


.. _`zest.releaser`: http://zestreleaser.readthedocs.org/en/latest/
