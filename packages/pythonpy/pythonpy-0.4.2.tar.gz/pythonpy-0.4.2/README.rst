Installation
------------

::

  sudo pip install pythonpy
  # restart your shell for tab completion to take effect 

::

py 'expression' ≅ python -c 'print(expression)'
-----------------------------------------------

Float Arithmetic
~~~~~~~~~~~~~~~~

::

  $ py '3 * 1.5' 
  4.5

::

Import any module automatically
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

  $ py 'math.exp(1)'
  2.71828182846

  $ py 'random.random()'
  0.103173957713
  
  $ py 'datetime.datetime.now?'
  Help on built-in function now:

  now(...)
        [tz] -> new datetime with tz's local day and time.


::

Lists are printed row by row
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

  $ py 'range(3)'
  0
  1
  2

  $ py '[range(3)]'
  [0, 1, 2]

::

py -x 'foo(x)' will apply foo to each line of input
---------------------------------------------------

Multiply each line of input by 7.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

  $ py 'range(3)' | py -x 'int(x)*7'
  0
  7
  14

::

Append ".txt" to each line of input
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

  $ py 'range(3)' | py -x 'x + ".txt"'
  0.txt
  1.txt
  2.txt

::

Append ".txt" to every file in the directory
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

  $ ls | py -x '"mv `%s` `%s.txt`" % (x,x)' | sh 
  # sharp quotes are swapped out for single quotes
  # single quotes handle spaces in filenames

::

Get only even numbers
~~~~~~~~~~~~~~~~~~~~~

::

  $ py 'range(8)' | py -x 'x if int(x)%2 == 0 else None'
  0
  2
  4
  6

::

py -l will set l = list(sys.stdin)
-------------------------------------------

Reverse the input
~~~~~~~~~~~~~~~~~

::

  $ py 'range(3)' | py -l 'l[::-1]'
  2
  1
  0

::

Sum the input
~~~~~~~~~~~~~

::

  $ py 'range(3)' | py -l 'sum(int(x) for x in l)'
  3

::

Count the lines of input
~~~~~~~~~~~~~~~~~~~~~~~~

::

  $ py 'range(17)' | py -l 'len(l)'
  17

::

Count words beginning with each letter
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

  $ cat /usr/share/dict/words | py -x 'x[0].lower()' | py -l 'collections.Counter(l).most_common(5)'
  ('s', 11327)
  ('c', 9521)
  ('p', 7659)
  ('b', 6068)
  ('m', 5922)

::

If you haven't had enough yet, check out the `wiki <http://github.com/Russell91/pythonpy/wiki>`__
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
