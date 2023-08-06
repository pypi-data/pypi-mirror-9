Contex - Contextual string manipulation
=======================================

Abstract
---------

This package provides ``contex.rules``, an interface which enables a very declarative form of string
manipulation, where you can manipulate a string "in one go" in sophisticated ways.

This library also provides two related abstractions, ``StringContext`` and ``MatchContext``, which
can be used for a more stateful manipulation of strings. I recommend using ``contex.rules`` as I
think that makes for more readable code. Nevertheless, those abstractions are well
documented and might usefully serve as building blocks. Indeed, ``contex.rules`` is implemented on
top of them.

The problem with our interfaces for string manipulation
-------------------------------------------------------

My motivation for creating this package was that I was assigned a task in which it was necessary to
change strings such as ``'1_Photo032-2008.jpg'`` into ``'1_Photo031-2008.jpg'``. All the numbers could vary
between filenames, and it seemed like I always had to do something inelegant to accomplish this task. Maybe
it was to match the various parts and stich them back together:

.. code-block:: python

   >>> match = re.fullmatch('(\d+)_Photo(\d+)-(\d+)\.jpg', '1_Photo032-2008.jpg')
   >>> '{}_Photo{}-{}.jpg'.format(match.group(1), '{:0>3}'.format(int(match.group(2))-1), match.group(3))
   '1_Photo031-2008.jpg'

Or using ``re.sub`` with non-consuming regex groups to match the correct area of the string:

.. code-block:: python

   >>> re.sub('(\d+)(?=-\d+\.jpg)', lambda m: '{:0>3}'.format(int(m.group(1))-1), '1_Photo032-2008.jpg')
   '1_Photo031-2008.jpg'

Shouldn't this be simpler? Describing that string with a regular expression is simple enough, and I'm
only changing one little part of the string, so why do I have to fiddle around with indices, and why do
I have to sacrifice readability? Most importantly, why do I have to experience this aesthetic pain deep
in my heart?

First attempt: stateful manipulation
------------------------------------

My first idea was that our abstractions aren't fit for this sort of problem. Strings are flat, they
have no sense of context, and if you pull out a substring then it requires special effort to stich it
back together. The solution? Just keep track of the ``before`` and the ``after``:

.. code-block:: python

   >>> view = contex.match('1_Photo032-2008.jpg', '\d+_Photo(?P<number>\d+)-\d+\.jpg')
   >>> view
   <MatchContext object; tup=('', '1_Photo032-2008.jpg', '')>
   >>> view.group('number')
   <MatchContext object; tup=('1_Photo', '032', '-2008.jpg')>
   >>> result = view.group('number').replace(lambda n: '{:0>3}'.format(int(n)-1))
   >>> result
   <MatchContext object; tup=('1_Photo', '031', '-2008.jpg')>
   >>> str(result)
   '1_Photo031-2008.jpg'
   >>> 

This way I can move around the "focus point" of the string with methods such as ``.group``, manipulate that space,
and when I'm done convert it back to a ``str``. I can even manipulate more than one area of the string:

.. code-block:: python

   >>> view = contex.match('1_Photo032-2008.jpg', '\d+_Photo(?P<number>\d+)-(?P<year>\d+)\.jpg')
   >>> view.group('number').replace('').group('year').replace(lambda y: y[-2:])
   <MatchContext object; tup=('1_Photo-', '08', '.jpg')>
   >>> 


``MatchContext`` keeps track of where the matched regular expression groups are: Even though I removed the
content of the "number" group, ``MatchContext`` knows where to find and replace the "year" group. It can also
deal with nested regex groups, 0-length matches etc.

.. note::

   Previously (v2.0.1 and earlier) I allowed arbitrary slicing on ``MatchContext`` objects to select the focus
   point in addition to the ``.group`` method. This was a mistake. When you're dealing with 0-length slices and
   adjacent regex groups that matched 0-length strings, there arises serious problems of semantics. I found out
   that the expected semantics is inextricably linked to which regex group you previously selected with ``.group``,
   and therefore had to disallow slicing for ``MatchContext`` objects.



Removing the state: Vive la Revolution
--------------------------------------

The ``MatchContext`` abstraction certainly is an improvement for these particular types of problems, but
there is one downside to it, and that is that it adds an additional layer of state to ordinary strings:
The programmer must remember which part of the string is in "focus", or, in other words, which state the
string is in.

So my next challenge was to eliminate the state. What I found out was that only in rare cases is the state
needed or useful, and this lead me to believe that the fundamental problem isn't really the abstractions we
use for representing strings, but rather the interfaces we have for manipulating them. Thus, pardon the pun,
enter ``contex.rules``:

.. code-block:: python

   >>> contex.rules('\d+_Photo(?P<number>\d+)-(?P<year>\d+)\.jpg', {
   ...     'number': lambda n: '{:0>3}'.format(int(n) - 1),
   ...     'year':   lambda y: y[-2:]
   ... }).apply('1_Photo032-2008.jpg')
   '1_Photo031-08.jpg'

Or maybe I want to change the layout of the filename completely:

.. code-block:: python


   >>> contex.rules('(\d+)_Photo(?P<number>\d+)-(?P<year>\d+)\.jpg', {
   ...     'number': lambda n: int(n) - 1,
   ...     'year':   lambda y: y[-2:]
   ... }).expand('1_Photo032-2008.jpg', 'Photo_{1}_{number:0>3}-{year}.jpeg')
   'Photo_1_031-08.jpeg'


The string manipulation is done in one go. The programmer doesn't need to remember where the focus point is
right now, or specify which order to do the replacements in. This is a much more *declarative* interface: you
tell it what the string looks like, what changes you want made, and it figures out the rest. You don't need to
stich the pieces back together, and can create more readable regular expressions as well because of that.

Nested regex groups are also allowed: the nested one will be replaced first (which will make a difference if
the replacement for the outer group is a callable).

More advanced example
^^^^^^^^^^^^^^^^^^^^^

Here's an example using ``re.search`` (as opposed to ``re.fullmatch``, which is the default):

.. code-block:: python

   >>> contex.rules('(?P<millennium>\d)\d{3}', {
   ...      'millennium': lambda s: int(s)+1,
   ...      0:            lambda y: '<span class="year">{}</span>'.format(y)
   ... }, method=re.search).apply('Current year: 2015')
   'Current year: <span class="year">3015</span>'

Notice that the ``'millennium'`` group is replaced before the ``0`` group.

``contex.rules`` is explained in more detail in its very long docstring.

Doubtful stability
------------------

In order to retrieve certain information about the regular expressions to resolve ambiguities related to 0-length
matches and so on, I've seen it necessary to use ``sre_parse.parse`` to parse the regular expressions. This is
an "internal support module" or something like that, and the stability of this library becomes doubtful as a result.
My judgement was that it would take a lot of time and effort to create my own parser for python regular expressions,
and I could easily create some bugs in that parser too.

Conclusion
----------

I hope that the examples of ``contex.rules`` I have given are sufficiently intuitive so that any programmer can look
at them and infer pretty accurately what they do, because the whole point of this endeavor is to increase readability.

Furthermore, I'd be interested to see if other people can take this idea ``^\w{7}``

Using Contex
------------

The ``contex`` package contains 5 functions:

-  ``rules(regex, rule_dict, method=re.fullmatch, flags=0)`` for declarative string manipulation.
-  ``T(string)`` for converting a string into a ``StringContext`` object.
-  ``search(string, pattern, flags=0)`` and
-  ``match(string, pattern, flags=0)`` for regex searches (with the same semantic difference as in the ``re`` module).
   They both return a ``MatchContext`` object.
-  ``find(string, substring, right_side=False)`` for finding a substring, returns a ``StringContext`` object.

``contex`` also contains the ``StringContext`` and ``MatchContext`` classes.

Installing
----------

``contex`` should work in both Python 2.7 and 3. 

Install with ``$ pip install contex``. If you want to install for Python 3 you might want to replace ``pip`` with ``pip3``, depending on how your system is configured.


Developing
----------

Contex is documented and tested. Run ``$ nosetests`` or
``$ python3 setup.py test`` to run the tests. The code is hosted at https://notabug.org/Uglemat/Contex

License
-------

The library is licensed under the GNU General Public License 3 or later.
This README file is public domain.


