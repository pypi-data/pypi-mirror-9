Command Line News
=================
	A command line rss news feed reader.


Version
=======
	``0.3.1``


Installation
============
1. Download the package from <https://pypi.python.org/packages/source/c/clnews/clnews-0.2.1.tar.gz>
2. Extract the contents of the file:
        ``tar -xvfz clnews-0.2.1.tar.gz``


Configuration
=============
All you need to do is to add your RSS urls into the ``config.py`` under the ``CHANNELS`` dictionary as following::

	"nbc": {
	    "name": "NBC",
	    "url": "http://feeds.nbcnews.com/feeds/topstories"
	}



Usage
=====
Run the script:
    ``python clnews.py``


Options
=======
When the scripts starts running a command prompt will appear: 
    ``news>``

The available commands that you can use are the following:

* ``news> .help`` 
	displays the help message and exit

* ``news> .list`` 
	lists all the available channels

* ``news> .get`` 
	retrieves the news of a given channel, e.g.: .get cnn

License
=======
	MIT
