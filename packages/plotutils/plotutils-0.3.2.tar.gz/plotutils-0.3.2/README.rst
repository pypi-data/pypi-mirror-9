plotutils
=====

This is where I keep matplotlib-related plotting utility functions I have found useful.

Installation
------
To install::

  pip install plotutils


Usage
------

How to use `setfig`:

This will create a new figure (same as plt.figure() call in
matplotlib)::

  >>> from plotutils import setfig
  >>> setfig(None) #or setfig()

You can also set the current figure to be a given figure number, clear it, and start over, e.g.: `setfig(3)`.

`setfig(0)` will do nothing, implying you want to overplot on the currently active figure.

I use the `setfig` function in every function that I write that makes
a plot, almost always as follows:

.. code-block:: python

  import matplotlib.pyplot as plt
  def my_plot(x,y,fig=None,**kwargs):
    setfig(fig)
    plt.plot(x,y,**kwargs)


