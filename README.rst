
Lisp2SCS
========

**Lisp2SCS** is a community-created plugin for `Linux Show Player`_.

This plugin adds the ability to import and export show files compatible with
`Show Cue Systems`_ (SCS).


Usage
-----

Once the plugin has been installed and enabled, you can import and export
SCS showfiles via the Import/Export submenus of the File Menu.


Dependencies
------------

This plugin depends on Linux Show Player 0.6, and will most likely also
depend on an XML-parsing library, though which one is still to be determined.


Installation
------------

To use, navigate to ``$XDG_DATA_HOME/LinuxShowPlayer/$LiSP_Version/plugins/``
(on most Linux systems ``$XDG_DATA_HOME`` is ``~/.local/share``), and create a
subfolder named ``lisp2scs``.

Place the files comprising this plugin into this new folder.

When you next start **Linux Show Player**, the program should load the plugin
automatically.

.. _Linux Show Player: https://github.com/FrancescoCeruti/linux-show-player
.. _Show Cue Systems: https://www.showcuesystems.com/
