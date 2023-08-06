# Detektor

A library for finding similarities in code.


## Motivation

Created to find similarities of a set of code files. Used to compare a set of
hand-ins in programming education courses, and can report if similarity of code
in files are high based on a couple of techniques described below.

## Install

    $ pip install detektor

## Examples?
See the demos/ directory.

## Details

Detektor is implemented in Python, and it is designed for easy adding of
functionality. Currently, it only finds similarities in programs written in the
Python and Perl programming languages, but adding support for new languages
should be straightforward. It should also work for assembler
languages and 'home-made' languages especially developed for education purposes.

To find similarities, the only thing that is kept from a program is the keywords
and the operators. Everything else is stripped away. The finding of similarities
is done by comparing:

* The number of each keyword and operator used 
* The whole string of keywords and operators
* Parts of a string build of these keywords and operators

A code supplied as a file handler opened for reading is given a tuple of values
as a "fingerprint". These are:

* Total number of keywords
* A string representing the number of each keyword used in the code
* Total number of operators
* A string representing the number of each keyword used in the code
* The hashvalue of the string of all keywords
* A hash for each function in the program

Each comparison of two programs is given scores, and if the scores of a
comparison is higher than 20 percent (or which ever limit is supplied as
argument) average it is reported.


## Develop detektor

Install:

    $ git clone git@github.com:apparator/detektor.git
    $ mkvirtualenv detektor
    $ python setup.py develop

Run tests:

    $ python setup.py test


Update the pypi package (requires admin rights for the pypi package):

    $ python setup.py sdist upload
