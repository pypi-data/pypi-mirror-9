# README #

Take any two dimensional list like object that supports indexing as input and output a circular clockwise shrinking
spiral of elements from the input beginning at the top left most corner (ie: input[0][0]) until all the input is
exhausted.

This will work on lists of any size in either dimension.

[ ![Codeship Status for sys-git/spirol](https://codeship.com/projects/b8f6bef0-5132-0132-d6d9-0ea8256ccae9/status)](https://codeship.com/projects/48263)
[![Build Status](https://api.shippable.com/projects/54afbe1ad46935d5fbc1e904/badge?branchName=master)](https://app.shippable.com/projects/54afbe1ad46935d5fbc1e904/builds/latest)

* Version 1.0.3

### How do I get set up? ###

* **python setup.py install**
* Dependencies:  **shifty (v0.0.3)**
* How to run tests:  **./runtests.sh**
* Deployment instructions:  **pip install spirol**

### What about test coverage? ###
There is a full suite of unit-tests.

### Contribution guidelines ###
I accept pull requests.

### Who do I talk to? ###
* Francis Horsman:  **francis.horsman@gmail.com**

### Example ###

```
>>> from spirol import spirol

>>> a = spirol([[1,2,3], [4,5,6], [7,8,9]], (3, 3))

>>> a
spirol(3, 3, clockwise from tl)

>>> [i for i in a]
[1, 2, 3, 6, 9, 8, 7, 4, 5]

>>> print(a)
spirol(3, 3, clockwise from tl): [1, 2, 3, 6, 9, 8, 7, 4, 5]

>>> len(a)
9

>>> a = spirol([[1,2,3], [4,5,6], [7,8,9]], (3, 3), corner='br', direction='counterclock')

>>> a
spirol(3, 3, counterclock from br)

>>> [i for i in a]
[9, 6, 3, 2, 1, 4, 7, 8, 5]
```
