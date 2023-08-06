Orochi – 8tracks.com client
===========================

**Warning: Beta quality!**

.. image:: https://secure.travis-ci.org/dbrgn/orochi.png?branch=master
    :alt: Build status
    :target: http://travis-ci.org/dbrgn/orochi

Orochi is a command line client for `8tracks.com <http://8tracks.com/>`__
written in Python.

Yamata no Orochi (八岐の大蛇) is a legendary 8-headed and 8-tailed Japanese
dragon. The name translates to "8-branched giant snake". I chose the name
because it both refers to the number eight (as in 8tracks) and to snakes (as in
Python).

.. figure:: http://i.imgur.com/UdiIM8k.png
    :alt: Illustration of Yamata no Orochi

    *Image courtesy of Gustavo Araujo*

If you like this project, I'm happy for support via Flattr or Gittip!

.. image:: http://api.flattr.com/button/flattr-badge-large.png
    :alt: Flattr this repo
    :target: https://flattr.com/submit/auto?user_id=danilo&url=https://github.com/dbrgn/orochi&title=orochi&tags=github,8tracks,music,python&category=software 

.. image:: https://dbrgn.ch/gittip-badge.png
    :alt: Gittip this repo
    :target: https://www.gittip.com/dbrgn/


Usage
-----

Prerequisites:

- Python 2.7+ (compatibility for 3.2+ will probably follow in the future)
- mplayer (at least r27665, released in 1.0rc3)

Install::

    $ pip install -U orochi

Start::

    $ orochi

Available commands (main menu)::

    search:
        Syntax: search <searchterm>
        Search for a mix by keyword.
        You can then play a mix with the "play" command.
        Press enter to show next page results.
    search_tags:
        Syntax: search <tag1>, <tag2>
        Search for a mix by tag(s), separated by comma.
        You can then play a mix with the "play" command.
        Press Enter to show next page results.
    search_user:
        Syntax: search <username>
        Search for a mix by user.
        You can then play a mix with the "play" command.
        Press Enter to show next page results.
    search_user_liked:
        Syntax: search <username>
        Search for a mix liked by user.
        You can then play a mix with the "play" command.
        Press Enter to show next page results.
    set:
        Syntax: set <setting> <param>
        Configure settings.
        Available settings: 
        - autologin yes|no
          Toggle autologin on start (no by default)
          WARNING: password will be saved in plain text.
        - sorting recent|popular|hot (hot by default)
          Configure search results sorting order.
        - results_per_page <n>
          Set number of results per page showed.
        To get help for each setting, press Enter with no <param>.
    play:
        Syntax: play <mix>
        Play the nth mix from the last search results.
        The <mix> argument can also be a mix ID or an URL.
    exit:
        Exit the interpreter.
        You can also use the Ctrl-D shortcut.
    login:
        Syntax: login <username>
        Log in to your 8tracks account.
    liked_mixes:
        List liked mixes (login required).
        Press Enter to show next page results.


Available commands (play mode menu)::

    pause / p:
        Pause or resume the playback.
    stop:
        Stop the playback and exit play mode.
    next_song / n:
        Skip to next song.
    next_mix:
        Skip to next mix.
    status / s:
        Show the status of the currently playing song.
    mix_info:
        Show information about the currently playing mix.
    volume / v:
        Syntax: volume <amount>
        Change playback volume. The argument must be a number between 0 and 100.
    like_mix / l:
        Like the currently playing mix (login required).
    unlike_mix / ul:
        Un-like the currently playing mix (login required).
    fav_track / f:
        Favorite the currently playing track (login required).
    unfav_track / uf:
        Un-favorite the currently playing track (login required).


Configuration
-------------

The first time Orochi is started, it creates the ``config.json`` configfile in
the ``~/.config/orochi/`` directory. The following configurations can be
changed::

    mplayer_extra_args:
        Extra arguments that are passed on to the mplayer instance.

Example configuration::

    {
        "mplayer_extra_args": "-ao alsa:device=hw=1.0"
    }


Development
-----------

Install ``requirements.txt`` (with ``pip install -r``). Then start orochi the
following way::

    $ python -m orochi.client

For development and testing purposes, you can also pass in the ``--pdb``
argument. Then a debug session should be started if orochi crashes.


Coding Guidelines
-----------------

`PEP8 <http://www.python.org/dev/peps/pep-0008/>`__ via `flake8
<https://pypi.python.org/pypi/flake8>`_ with max-line-width set to 99 and
E126-E128 ignored.


Testing
-------

Install ``requirements-dev.txt``, then run ``py.test`` in the main directory.
Violations of the coding guidelines above will be counted as test fails.


Contributing
------------

Please refer to the `Contributors Guidelines
<https://github.com/dbrgn/orochi/blob/master/CONTRIBUTING.md>`__. Thanks!


License
-------

Copyright (C) 2013–2015 Danilo Bargen and contributors

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
