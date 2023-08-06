strgen
======

Generate randomized strings of characters using a template.

This Python module enables a user to generate test data, unique ids,
passwords, vouchers or other randomized data very quickly using a
template language. The template language is superficially similar to
regular expressions but instead of defining how to match or capture
strings, it defines how to generate randomized strings.

An example template for generating a strong password:

::

     [\w\p\d]{20}

will generate something like the following:

::

     P{:45Ec5$3)2!I68x`{6

Usage:

::

    from strgen import StringGenerator
    StringGenerator(<template>).render()

or to produce a list of unique strings:

::

    from strgen import StringGenerator
    StringGenerator(<template>).render_list(10,unique=True)

Example:

::

    >>> from strgen import StringGenerator
    >>> StringGenerator('[\l\d]{4:18}&[\d]&[\p]').render()
    u'Cde90uC{X6lWbOueT'

The ``template`` is a string that is a sequence of one or more of the
following:

-  *Literal text* (for example: ``UID``)
-  *Character class* (for example: ``[a-z\s]``)
-  *Group*, a combination of literals and character classes, possibly
   separated by operators and using parenthesis where appropriate (for
   example: ``(UID[\d]{4}&[\w]{4})``)

In more detail:

Literal: <any string>
---------------------

Any literal string.

Example:

::

    orderno

Special characters need to be escaped with backslash ``\``.

Character class: [<class specification>]
----------------------------------------

Much like in regular expressions, it uses strings of characters and
hyphen for defining a class of characters.

Example:

::

    [a-zA-Z0-9_]

The generator will randomly choose characters from the set of lower case
letters, digits and the underscore. The number of characters generated
will be exactly one in this case. For more, use a quantifier:

::

    [a-zA-Z0-9_]{8}

As a shortcut for commonly used character sets, a character set code may
be used. The following will render in exactly the same way:

::

    [\w]{8}

Character Set Codes
-------------------

-  ``\W``: whitespace + punctuation
-  ``\a``: ascii\_letters
-  ``\c``: lowercase
-  ``\d``: digits
-  ``\h``: hexdigits
-  ``\l``: letters
-  ``\o``: octdigits
-  ``\p``: punctuation
-  ``\r``: printable
-  ``\s``: whitespace
-  ``\u``: uppercase
-  ``\w``: ``_`` + letters + digits

Quantifier: {x:y}
-----------------

Where x is lower bound and y is upper bound. This construct must always
follow immediately a class with no intervening whitespace. It is
possible to write {:y} as a shorthand for {0:y} or {y} to indicate a
fixed length.

Example:

::

    [a-z]{0:8}

Generates a string from zero to 8 in length composed of lower case
alphabetic characters.

::

    [a-z]{4}|[0-9]{4}

Generates a string with either four lower case alphabetic characters or
a string of digits that is four in length.

Using a character class and no quantifier will result in a quantifier of
1. Thus:

::

      [abc]

will result always in either ``a``, ``b``, or ``c``.

Group: (<group specification>)
------------------------------

A group specification is a collection of literals, character classes or
other groups divided by the OR operator ``|`` or the shuffle operator
``&``.

OR Operator
-----------

The binary ``|`` operator can be used in a group to cause one of the
operands to be returned and the other to be ignored with an even chance.

Shuffle Operator
----------------

The binary ``&`` operator causes its operands to be combined and
shuffled. This addresses the use case for many password requirements,
such as, "at least 6 characters where 2 or more are digits". For
instance:

::

    [\l]{6:10}&[\d]{2}

If a literal or a group is an operand of the shuffle operator, it will
have its character sequence shuffled with the other operand.

::

    foo&bar

will produce strings like:

::

    orbfao

Concatenation and Operators
---------------------------

Classes, literals and groups in sequence are concatenated in the order
they occur. Use of the ``|`` or ``&`` operators always binds the
operands immediately to the left and right:

::

    [\d]{8}xxx&yyy

produces something like:

::

     00488926xyyxxy

In otherwords, the digits occur first in sequence as expected. This is
equivalent to this:

::

    [\d]{8}(xxx&yyy)

Special Characters, Escaping and Errors
---------------------------------------

There are fewer special characters than regular expressions:

::

    [](){}|&-$

They can be used as literals by escaping with backslash. All other
characters are treated as literals. The hyphen is only special in a
character class, when it appears within square brackets. The template
parser tries to raise exceptions when syntax errors are made, but not
every error will be caught, like having space between a class and
quantifier.

Spaces
------

Do not use any spaces in the template unless you intend to use them as
characters in the output:

::

    >>> SG('(zzz & yyy)').render()
    u'zzyz y y'

Character Classes and Quantifiers
---------------------------------

Use a colon in the curly braces to indicate a range. There are sensible
defaults:

::

    [\w]       # randomly choose a single word character
    [\w]{0:8}  # generate word characters from 0-8 in length 
    [\w]{:8}   # a synonym for the above
    [\w]{8}    # generate word characters of exactly 8 in length
    [a-z0-9]   # generate a-z and digits, just one as there is no quantifier
    [a-z0-9_!@]  # you can combine ranges with individual characters

Here's an example of generating a syntactically valid but, hopefully,
spurious email address:

::

    [\c]{10}(.|_)[\c]{5:10}@[\c]{3:12}.(com|net|org)

The first name will be exactly 10 lower case characters; the last name
will be 5-10 characters of lower case letters, each separated by either
a dot or underscore. The domain name without domain class will be 3 - 12
lower case characters and the domain type will be one of
'.com','.net','.org'.

The following will produce strings that tend to have more letters,
because the set of letters (52) is larger than the set of digits (10):

::

    [\l\d]

Using multiple character set codes repeatedly will increase the
probability of a character from that set occuring in the result string:

::

    [\l\d\d\d\d]

This will provide a string that is three times more likely to contain a
digit than the previous example:

::

    [\l\d]

Uniqueness
----------

When using the ``unique=True`` flag, it's possible the generator cannot
possibly produce the required number of unique strings. For instance:

::

     StringGenerator("[0-1]").render_list(100,unique=True)

This will generate an exception but not before attempting to generate
the strings.

The number of times the generator needs to render new strings to satisfy
the list length and uniqueness is not determined at parse time. The
maximum number of times it will try is by default n x 10 where n is the
requested length of the list. Therefore, taking the above example, the
generator will attempt to generate the unique list of 0's and 1's 100 x
10 = 1000 times before giving up.

Unicode
-------

Unicode is supported for both the template and output.

Character Sets
--------------

Character sets used for backslashed character codes are exactly the
Python character sets from the string package. While the module is
designed to work on pre- Python 3, we use only those member variables
from string that are present in Python 3. This avoids the
locale-dependent sets of characters.

Randomness Methods
------------------

The generator tries to use ``random.SystemRandom()`` for ``randint``,
``shuffle``, etc. It falls back to ``random.randint`` and associated
methods if it can't use ``SystemRandom``.

Debugging
---------

Call the dump() method on the class instance to get useful information:

-  Version of strgen module
-  Version of Python
-  The class name used for random methods
-  The parse tree
-  The output from one invocation of the render() method

The output looks something like the following:

::

    >>> SG('[\w]{8}&xyz|(zzz&yyy)').dump()
    StringGenerator version: 1.1.2
    Python version: 2.7.3 |EPD_free 7.3-2 (32-bit)| (default, Apr 12 2012, 11:28:34)
    [GCC 4.0.1 (Apple Inc. build 5493)]
    Random method provider class: SystemRandom
    sequence:
    OR
         AND
             -1:8:_abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789
             xyz
        sequence:
             AND
                  zzz
                  yyy
    u'zMXGPwyxE9a'
                                                                                                                    

Rationale and Design Goals
--------------------------

In Python, the need to generate random strings comes up frequently and
is accomplished usually (though not always) via something like the
following code snippet:

::

      import random
      import string
      mykey = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(10))

This generates a string that is 10 characters made of uppercase letters
and digits. Unfortunately, this solution becomes cumbersome when
real-world requirements are added. Take for example, the typical
requirement to generate a password: "a password shall have 6 - 20
characters of which at least one must be a digit and at least one must
be a special character". The above solution then becomes much more
complicated and changing the requirements is an error-prone and
unnecessarily complex task.

The equivalent using the strgen package is the following:

::

    from strgen import StringGenerator as sg
    sg('[\u\d]{10}').render()

strgen is far more compact, flexible and feature-rich than using the
standard solution:

-  It tries to use a better entropy mechanism and falls back gracefully
   if this is not available on the host OS.

-  The user can easily modify the specification (template) with minimal
   effort without the fear of introducing hard-to-test code paths.

-  Modifications to the template are simpler and far less error prone
   than writing all the code necessary to implement changes in a random
   string specification

-  It covers a broader set of use cases: unique ids, persistent unique
   filenames, test data, etc.

-  The template syntax is very easy to learn for anyone familiar with
   regular expressions while being much simpler.

-  It supports unicode.

-  It works on Python 2.6, 2.7 and 3.

-  It proposes a standard way of expressing common requirements, like "a
   password shall have 6 - 20 characters of which at least one must be a
   digit and at least one must be a special character":

   ::

        [\l\d]{4:18}&[\d]&[\p]

This package is designed with the following goals in mind:

-  Provide an abstract template language that does not depend on a
   specific implementation language.

-  Reduce dependencies on other packages.

-  Keep syntax as simple as possible while being useful.

-  Provide an implementation design with associated behaviour that
   strikes the right balance between ease-of-implementation and
   ease-of-use.

-  Superficially similar to regular expressions to enable developers to
   quickly pick up the template syntax.

-  Support non-ASCII languages (unicode).

License
-------

Released under the BSD license.

Original Author: paul.wolf@yewleaf.com
