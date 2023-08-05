parse\_this
===========

|PyPI latest version badge| |Code health|

Makes it easy to parse command line arguments for any function, method
or classmethod.

You just finished writing an awesome piece of code and now comes the
boring part: adding the command line parsing to actually use it ...

So now you need to use the awesome, but very verbose, ``argparse``
module. For each argument of your entry point method you need to add a
name, a help message and/or a default value. But wait... Your parameters
are correctly named right!? And you have an awesome docstring for that
method. There is probably a way of creating the ``ArgumentParser``
easily right?

Yes and it's called ``parse_this``!

Usage
-----

Decorator
~~~~~~~~~

As a decorator that will create an argument parser for the decorated
function. A ``parser`` attribute will be added to the method and can be
used to parse the command line argument.

.. code:: python

    from __future__ import print_function
    from parse_this import create_parser


    @create_parser(str, int)
    def concatenate_str(one, two=2):
        """Concatenates a string with itself a given number of times.

        Args:
            one: string to be concatenated with itself
            two: number of times the string is concatenated, defaults to 2
        """
        return one * two


    if __name__ == "__main__":
        parser = concatenate_str.parser
        # This parser expect two arguments 'one' and 'two'
        namespace_args = parser.parse_args()
        print(concatenate_str(namespace_args.one, namespace_args.two))

Calling this script from the command line as follow:

.. code:: bash

    python script.py yes 2

will return ``'yesyes'`` as expected and all the parsing have been done
for you.

Note that the function can still be called as any other function. Also
it is not possible to stack ``create_parser`` with any decorator that
would modify the signature of the decorated function e.g. using
``functools.wraps``.

Function
~~~~~~~~

As a function that will handle the command line arguments directly.

.. code:: python

    from __future__ import print_function
    from parse_this import parse_this


    def concatenate_str(one, two=2):
        """Concatenates a string with itself a given number of times.

        Args:
            one: string to be concatenated with itself
            two: number of times the string is concatenated, defaults to 2
        """
        return one * two


    if __name__ == "__main__":
        print(parse_this(concatenate_str, [str, int]))

Calling this script with the same command line arguments ``yes 2`` will
also return ``'yesyes'`` as expected.

Arguments and types
-------------------

Both ``parse_this`` and ``create_parser`` need a list of types to which
arguments will be converted to. Any Python type can be used, two special
values are used for the ``self`` and ``cls`` respectively ``Self`` and
``Class``. There is no need to provide a type for keyword agurment since
it is infered from the default value of the argument.

If this is the containt of ``test.py``:

.. code:: python

    from __future__ import print_function
    from parse_this import create_parser, Self


    class INeedParsing(object):
        """A class that clearly needs argument parsing!"""

        def __init__(self, an_argument):
            self._an_arg = an_argument

        @create_parser(Self, int, str, params_delim="--")
        def parse_me_if_you_can(self, an_int, a_string, default=12):
            """I dare you to parse me !!!

            Args:
                an_int -- int are pretty cool
                a_string -- string aren't that nice
                default -- guess what I got a default value
            """
            return a_string * an_int, default * self._an_arg


    if __name__ == "__main__":
        need_parsing = INeedParsing(2)
        parser = need_parsing.parse_me_if_you_can.parser
        namespace_args = parser.parse_args()
        print(need_parsing.parse_me_if_you_can(namespace_args.an_int,
                                               namespace_args.a_string,
                                               namespace_args.default))

The following would be the output of the command line
``python test.py --help``:

.. code:: bash

    usage: test.py [-h] [--default DEFAULT] an_int a_string

    I dare you to parse me !!!

    positional arguments:
      an_int             int are pretty cool
      a_string           string aren't that nice

    optional arguments:
      -h, --help         show this help message and exit
      --default DEFAULT  guess what I got a default value

The following would be the output of the command line
``python test.py 2 yes --default 4``:

.. code:: bash

    ('yesyes', 8)

The first line argument ``2`` is used as the ``an_int`` argument for the
method, the second ``yes`` is the string that will be concatenated ``2``
times. And finally the optional argument specified by ``--default`` is
multiplied by the construtor arg i.e. ``8``.

Note: both ``parse_this`` and ``create_parser`` need your docstring to
be in a specific format. The description of the argument parser is taken
from the docstring and contains all the text until the first blank line.
Arguments help message are taken from the following pattern:

``<argument_name><delimiter_chars><argument_help>``

-  argument\_name must be the same as the argument of the method
-  delimiter\_chars is one or more chars that separate the argument from
   its help message
-  argument\_help is everything behind the delimiter\_chars until the
   next argument, **a blank line** or the end of the docstring

The ``delimiter_chars`` can be passed to both ``parse_this`` and
``create_parser`` as the keywords argument ``params_delim``. It defaults
to ``:`` since this is the convention I most often use.

In a similar fashion you can parse line arguments for classmethods:

.. code:: python

    ...
        @classmethod
        @create_parser(Class, int, str, params_delim="--")
        def parse_me_if_you_can(cls, an_int, a_string, default=12):
            """I dare you to parse me !!!

            Args:
                an_int -- int are pretty cool
                a_string -- string aren't that nice
                default -- guess what I got a default value
            """
            return a_string * an_int, default * default

The output will be the same as above.

**Note**: The ``classmethod`` decorator is placed **on top** of the
``create_parser`` decorator in order for the method to still be a
considered a class method.

``parse_this`` contains a simple way to create a command line interface
from an entire class. For that you will need to use the ``parse_class``
class decorator.

.. code:: python

    from __future__ import print_function
    from parse_this import Self, create_parser, parse_class


    @parse_class()
    class ParseMePlease(object):
        """This will be the description of the parser."""

        @create_parser(Self, int)
        def __init__(self, foo):
            self._foo = foo

        @create_parser(Self, int)
        def do_stuff(self, bar):
            return self._foo * bar


    if __name__ == "__main__":
        parser = ParseMePlease.parser
        namespace = parser.parse_args()
        parse_me_please = ParseMePlease(namespace.foo)
        if namespace.method == "do-stuff":
            print(parse_me_please.do_stuff(namespace.bar))

``parse_class`` will create a command line argument parser that is able
to handle your whole class!!

How does it work?

-  If the ``__init__`` method is decorated it will be considered the
   first, or top-level, parser this means that all arguments in your
   ``__init__`` will be arguments pass right after invoking you script
   i.e. ``python script.py init_arg_1 init_arg_2 etc...``
-  The description of the top-level parser is taken from the class's
   docstring or overwritten by the keyword argument ``description`` of
   ``parse_class``.
-  Each method decorated by ``create_parser`` will become a subparser of
   its own. The command name of the subparser is the same as the method
   name with ``_`` replaced by ``-``. 'Private' methods, whose name
   start with an ``_``, do not have a subparser by default, as this
   would expose them to the outside. However if you want to expose them
   you can set the keyword argument ``parse_private=True`` to
   ``parse_class``. If exposed their command name will need contain the
   leading ``-`` as this would be confusing for command parsing
-  When calling ``python script.py --help`` the help message for
   **every** parser will be displayed making easier to find what you are
   looking for
-  To know which subcommand has been called by the command line you need
   to access the ``method`` attribute of the object returned by
   ``parser.parse_args()`` it will contain the name of the invoked
   command, hence you know which method to call on your object and are
   guaranteed the arguments for this method have been correctly parsed

If the previous decorated class ``ParseMePlease`` is in a ``script.py``
file we can execute the following commands:

.. code:: bash

    python script.py --help # Print the help for every parser
    python script.py 12 do-stuff 2 # Outputs 24 as expected

INSTALLING PARSE\_THIS
----------------------

``parse_this`` can be installed using the following command:

.. code:: bash

    pip install parse_this

RUNNING TESTS
-------------

To check that everything is running fine you can run the following
command:

.. code:: bash

    python setup.py nosetests

TODO
----

-  Handle vargs and kwargs
-  Make a class decorator for a argparser with multiple subcommand for
   each of its decorated method

.. |PyPI latest version badge| image:: https://badge.fury.io/py/parse_this.svg
   :target: https://pypi.python.org/pypi/parse_this
.. |Code health| image:: https://landscape.io/github/bertrandvidal/parse_this/master/landscape.png
   :target: https://landscape.io/github/bertrandvidal/parse_this/master
