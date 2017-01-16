Diap's Editing Toolbag (A calibre editor plugin)
============

Various tools for use in calibre's Edit Book Tool.

**Main Features of Diaps Editing Toolbag:**<br/>
(and yes, I realize there should be an apostrophe in "Diaps" but I can't bring myself to do it!)

1) Span Div Editor: conveniently remove, change the attributes of (and/or convert to different html elements) those pesky, nestable spans and divs (as well as a few others).

2) Smarten Punctuation (the sequel): gives slightly more granular control over the the smartening process. It preserves pre-existing entities and lets you choose what you want to smarten. So if you prefer three periods to the ellipse character/entity, you can keep them if you like. Also lets you supply a text file that defines apostrophe exception words like 'cept and 'tis in order to get the apostrophe right (instead of an opening single quote). I'm attaching a sample file for that, but basically it's one word per line WITHOUT any apostrophe characters. You can also choose to go with SmartyPants' default of using numeric entities instead of unicode characters if you like.

3) Convert CM to EM: this one was one I did for roger64. It simply parses CSS files looking for attributes that have cm dimensions and converts them to em (based on a preset factor).

Please scour the differences and make judicious use of the checkpoint system before trusting these tools on your babies!!

Links
=====

* The Diaps Editing Toolbag plugin support thread on MobileRead: <https://www.mobileread.com/forums/showthread.php?t=251365>


Building
========

First, clone the repo and cd into it:

    $ git clone https://github.com/dougmassay/toolbag-calibre-plugin.git
    $ cd ./toolbag-calibre-plugin


To create the plugin zip file, run the setup.py script (root of the repository tree) with Python

    $python setup.py

You can also add a -d (or --debug) option to setup.py.** If calibre is installed and on your
path and you add the '-d' option, setup.py will attempt to:

    1) close calibre if it's open
    2) install the plugin using calibre-customize
    3) relaunch calibre in debug-mode

If all goes well, the plugin can now be run and any debug print statements/errors should print
to the terminal. If you have a complex calibre setup (or it's not on your path), you may need to
install the plugin manually to debug.

** Note if you're not using the debug option with setup.py, you can use Python2 or Python3 to build the plugin. But if if you're using the -d option to install the plugin and launch calibre, you must use Python2.


Contributing / Modifying
============
From here on out, a proficiency with developing / creating calibre plugins is assumed.
If you need a crash-course, an introduction to creating calibre plugins is available at
<https://manual.calibre-ebook.com/creating_plugins.html>.


The core plugin files (this is where most contributors will spend their time) are:

    > __init__.py
    > dialogs.py
    > main.py
    > plugin-import-name-diaps_toolbag.txt
    > span_div_config.py
    > utilities.py


Files used for building/maintaining the plugin:

    > setup.py  -- this is used to build the plugin.
    > setup.cfg -- used for flake8 style and PEP checking. Use it to see if your code complies.
    (if my setup.cfg doesn't bark about it, then I don't care about it)

Feel free to fork the repository and submit pull requests (or just use it privately to experiment).



License Information
=======

###Diaps Editing Toolbag (a calibe plugin)

    Licensed under the GPLv3.


