==========
 Cavatina 
==========

Cavatina is a font for writing music. This homonymous library contains the parser and translator for the Cavatina syntax. Refer to http://cavatinafont.com/howto for the syntax specification.

Common commands::

    $ python rtf2xml.py [path] [format]

    $ python translateToMusic21.py [string] [format]

Output path is current working directory. ``path`` should be a rich text file or a text file. Possible values for ``format`` are musicxml (default) and midi.


Installation
============

Double click on ``installer.command`` or do

    $ python setup.py install

Dependencies
------------

* music21

Services
--------

The ``services`` folder contains right-click menu shortcuts for the translator. There are installation instructions inside the folders within.


