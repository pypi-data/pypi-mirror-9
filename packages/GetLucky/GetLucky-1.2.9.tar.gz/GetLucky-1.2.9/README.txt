=====
Intro
=====

Ever get your SO/ hot date/ that bartender that kinda looks like Ryan
Gosling back to your place and when you go to put on some sweet jams have
the mood dampened by the how long it takes to open your browser,
find a playlist and then click play? 
Enter Get Lucky, a command line interface that uses Songza to quickly set the mood.

============
Installation
============

Get Lucky can be installed via pip.
On Linux/OSX::

    sudo pip install GetLucky

On Windows::

    pip install GetLucky


Or

First install setuptools and then::

   git clone git://github.com/TannerBaldus/getlucky.git
   cd getlucky/GetLucky
   python setup.py install   



=====
Usage
=====

Help Message
-------------
To view the help documentation you enter the command ``gl`` or the option ``-h / --help`` after any command


Getting Lucky
--------------
Whether you  just enjoy some background music run the command: ::

    gl lucky

This will play a random Songza playlist for getting lucky.

You can also pick an option that best describes how you like to get down:: 
                                        
  -s, --smooth           
  -f, --fiesty                             
  -x, --extreme   

Example Calls::

    gl lucky -f
    gl lucky --smooth


Not Getting Lucky
-----------------

Get Lucky is great for even when you're not rocking the cabash. You can quickly play Songza playlists
by activity, genre, or mood. These commands take the following form where ```< >``` denotes an argument::

   gl mood <mood>  
   gl genre <genre> 
   gl activity <activity>

The arguments must be a `valid <http://foo.com>`_ Songza `mood <http://songza.com/discover/moods>`_, `activity <http://songza.com/discover/activity>`_, or `genre <http://songza.com/discover/genre>`_. Also if the argument is more than one word you must put it in quotes.

Example Calls::


 gl activity 'ballroom dancing'
 gl genre metal


=========================
Pick a specific playlists
=========================

If you want pick a specific playlist from a genre, mood, and activity simply add the option ``-l`` to list the available playlists to pick from, then enter the number corresponding to the playlist you want to play.

For example to play the playlist "Harvest Moon":

Call::

 gl mood earthy

Output::

    1: Today's Americana
    2: Harvest Moon
    3: Today's Indie Folk & Americana
    4: Sweater Weather
    5: Eye-Opening Americana
    6: A Rustic Ramble
    7: Hippies, Hillbillies & Soul Stirrers
    8: Cosmic Americana
    9: Indie Roots Rock
    10: Easygoing Alt-Country
    ...
    Select a playlist. 

Enter 2::

    1: Today's Americana
    2: Harvest Moon
    3: Today's Indie Folk & Americana
    4: Sweater Weather
    5: Eye-Opening Americana
    6: A Rustic Ramble
    7: Hippies, Hillbillies & Soul Stirrers
    8: Cosmic Americana
    9: Indie Roots Rock
    10: Easygoing Alt-Country
    ...
    Select a playlist. 2
