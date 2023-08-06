Wikia
=========

**Wikia** is a Python library that makes it easy to access and parse
data from any `wikia website <https://www.wikia.com>`

Search a wikia, get article summaries, get data like links and images
from a page, and more. Wikipedia wraps the `Wikia API
<http://api.wikia.com/wiki/Wikia_API_Wiki>`__ so you can focus on using
wikia data, not getting it.



.. code:: python

  >>> import wikia
  >>> wikia.set_wiki("Runescape")
  >>> print wikia.summary("Banshee")
  # Banshees are Slayer monsters that require level 15 Slayer to kill. They frequently drop 13 noted pure essence, making them an alternative source of essence. Additionally, banshees tend to frequently drop many different types of herbs. Mighty banshees are a higher-levelled alternative, if this is given as your Slayer assignment.

  >>> wikia.search("Forest")
  # [u'Forest', u'Forester', u'Freaky Forester', u'Forester\'s Arms', u'Talking Forest', u'Jungle Forester', u'Dense forest', u'Forester hat', u'Ogre forester hat', u'Forester (Burgh de Rott Ramble)']

  >>> drakan = wikia.page("Castle Drakan")
  >>> drakan.title
  # u'Castle Drakan'
  >>> drakan.url
  # u'http://runescape.wikia.com/wiki/Castle_Drakan'
  >>> drakan.content
  # u'Castle Drakan is the home of Lord Drakan, the vampyre lord of Morytania. Found just north of Meiyerditch, it looms over the Sanguinesti region'...

  >>> wikia.set_lang("nl") # Dutch
  >>> wikia.summary("Runes", sentences=1)
  # Runes, of Magische runes zijn kleine gewichtloze steentjes waarmee spelers een spreuk kunnen uitvoeren.

Note: this library was designed for ease of use and simplicity, not for advanced use.

Installation
------------

To install Wikia, simply run:

::

  $ pip install wikia

Wikia is compatible with Python 2.6+ (2.7+ to run unittest discover) and Python 3.3+.

Documentation
-------------

Read the docs at http://api.wikia.com/wiki/Wikia_API_Wiki.

-  `Quickstart http://api.wikia.com/wiki/Quick_Start`__
-  `Full API http://www.wikia.com/api/v1/`__

To run tests, clone the `respository on GitHub <https://github.com/timidger/Wikia>`__, then run:

::

  $ pip install -r requirements.txt
  $ bash runtests  # will run tests for python and python3
  $ python -m unittest discover wikia/tests/ '*test.py'  # manual style

in the root project directory.

To build the documentation yourself, after installing requirements.txt, run:

::

  $ pip install sphinx
  $ cd docs/
  $ make html

License
-------

MIT licensed. See the `LICENSE
file <https://github.com/Timidger/Wikiaa/blob/master/LICENSE>`__ for
full details.

Credits
-------

-  `wiki-api <https://github.com/richardasaurus/wiki-api>`__ by
   @richardasaurus for inspiration
-  @nmoroze and @themichaelyang for feedback and suggestions
-  The `Wikimedia
   Foundation <http://wikimediafoundation.org/wiki/Home>`__ for giving
   the world free access to data
-  @goldsmith for making such a fantastic library to fork
-  /u/captainmeta4 for giving the idea for a reddit bot to post game wiki info
   like auto-wiki bot

