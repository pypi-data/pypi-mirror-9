=============
Flatten List
=============

Given a list of nested lists/tuples, returns all the elements in a single list.
Typical usage::

    #!/usr/bin/env python

    from flatten.flatten import flattenlist
    
    the_list = [[1,2,3],[4,5,6], [7], [8,9]]
    flattenlist(the_list)
    [1, 2, 3, 4, 5, 6, 7, 8, 9]
    


Short Intro
------------

There are already many implementations of this problem, given below.


- Enthought Matplotlib. If you have matplotlib installed or Enthought Canopy.The flatten module using::

    from matplotlib.cbook import flatten

- The main recipie for above code given here:

http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/121294

- An attempt using this module is made in this stackoverflow problem:

http://stackoverflow.com/questions/406121/flattening-a-shallow-list-in-python/20400584#20400584


FlattenList is a vanilla python attempt to get the same result without any external module overhead.