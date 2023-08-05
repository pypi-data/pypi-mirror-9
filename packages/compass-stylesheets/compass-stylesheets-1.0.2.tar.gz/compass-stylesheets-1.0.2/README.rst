This repository is automatically updated from https://github.com/Compass/compass

=======
Compass
=======


Compass is a Stylesheet Authoring Environment that makes your website design simpler to implement and easier to maintain.

http://compass-style.org


Installation
============

To get going with Compass python module you can install it from `PyPi package`_:

.. _PyPi package: https://pypi.python.org/pypi/compass-stylesheets

.. sourcecode:: sh

   pip install compass-stylesheets

Documentation
=============

Compass documentation pages are available at http://compass-style.org/

Python package
==============

After installation you can use *pkg_resource* module to access assets:

.. sourcecode:: python

   import pkg_resources
   
   as_string = pkg_resources.resource_string("compass_stylesheets", "stylesheets/_compass.scss")
   full_path_to_file = pkg_resources.resource_filename("compass_stylesheets", "stylesheets/_compass.scss")
   file_like = pkg_resources.resource_stream("compass_stylesheets", "stylesheets/_compass.scss")


Package consists of *scss* files.
