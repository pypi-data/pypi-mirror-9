=====================
pydidit for iDoneThis
=====================

`pydidit` is a command line tool to post to iDoneThis service

------------
Installation
------------

to install just run::

    sudo pip install pydidit

This will install didit script to your path.

-----
Usage
-----

pydidit uses environment variables to configure the default behaviour.

+----------------------+------------------------+---------------------------------+
| Environment variable | Command line parameter | Description                     |
+======================+========================+=================================+
| ``DIDIT_TEAM``       | ``--team``             | iDoneThis team to post to       |
+----------------------+------------------------+---------------------------------+
| ``DIDIT_API_TOKEN``  | ``--api-token``        | API token to use                |
+----------------------+------------------------+---------------------------------+

You can add the following lines to your ``.bashrc`` or ``.zshrc`` shell initialization scripts::

    export DIDIT_API_TOKEN=<my_idonethis_api_tag>
    export DIDIT_TEAM=<my_team>

To post your progress you have several options:

* putting your progress as an argument like::

      didit I can now post progress using a simple command line tool

  or like::

      didit 'I can now post progress! With simple command line tool!'

* running ``didit`` without parameters will open an editor where you can enter your progress. This has an advantage, that it makes it much easier to enter multiline texts

----
TODO
----

* Enable showing and/or editing the last post
* Enable adding more then one progress point in one edit session
* Allow getting a progress from STDIN
