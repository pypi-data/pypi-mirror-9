horseshit
=========

**horseshit** is an easy-to-use command line program that blocks
websites known to distract us from our work, which is forked from
`leftnode/get-shit-done <https://github.com/leftnode/get-shit-done>`__.

Available in Python 2.x/3.x, horseshit is also a PyPI package that can
be easily installed and updated via ``pip``.

Project homepage: http://www.soimort.org/horseshit

Installation
------------

1. Using the PyPI package:
~~~~~~~~~~~~~~~~~~~~~~~~~~

Install the PyPI package:

::

    $ [sudo] pip install horseshit

or:

::

    $ [sudo] easy_install horseshit

2. Using Git:
~~~~~~~~~~~~~

Clone the Git repository:

::

    $ git clone git://github.com/soimort/horseshit.git
    $ [sudo] python setup.py install

Usage
-----

1. Configuration
~~~~~~~~~~~~~~~~

``horseshits`` is a no-brainer plain text file contains a load of
horseshits that may distract you from work, line by line.

::

    twitter.com
    plus.google.com
    reddit.com

On \*nix systems, put your ``horseshits`` into:

::

    /etc/horseshits

Or: (recommended!)

::

    ~/.config/horseshits

On Windows, put it into your user directory:

::

    .config/horseshits

2. To get-shit-done
~~~~~~~~~~~~~~~~~~~

Execute it as root because it modifies your hosts file and restarts your
network daemon.

::

    $ sudo get-shit-done work

3. To no longer get-shit-done
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    $ sudo get-shit-done play

Additional Tips
---------------

You can, of course, use ``get-shit-done`` with your ``crontab``, to
control your work time and play time during the day. Whatever, I should
say self-control is always the best.

Acknowledgement
---------------

Thanks to Vic Cherubini, the original author of **get-shit-done**.
