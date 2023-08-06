pmath
*****

Bringing the math tools of Python to the command-line
-----------------------------------------------------

Doing math on the command-line is hard. Integer math can be done with BASH, but the only utility around for floating-point math is ``bc``, and that can be confusing with its ``scale`` and ``precision``. What if you want the power of Python's math, perhaps programmatically? Enter: ``pmath``.


Examples
--------

Basic input::

  $ pmath '3 + 4'
  7
  $ echo '3+4' | pmath
  7
  $ pmath <<< 3+4
  7
  $ pmath 'x=3;x+2'
  5

You can set the output format with a ``-f`` switch::

  $ pmath -f .4f <<< pow(2000, 1/3)
  12.5992
  $ pmath -f .4f <<< sin(pi/2)
  1.0000

Enabling complex math operations is straightforward with ``-c``::

  $ pmath -c <<< exp(1j*pi).real
  -1.0
  $ pmath -f.2f -c 'ang=3*pi/4; exp(1j*ang)'
  -0.71+0.71j

Installation
------------

Running ``pip install pmath`` will install the command-line utility.