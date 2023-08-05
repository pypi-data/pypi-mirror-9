.. Copyright 2015 University of York
   Author: Aaron Ecay

=================================
 Weihnachtsgurke search language
=================================

This document describes the search language format for the
Weihnachtsgurke tool.

General considerations
======================

The conditions for a particular search are entered in a text file, which
can have any extension.  Whitespace at line beginnings is ignored; this
means that you can use indentation to logically structure the file.  Lines
beginning with ``#`` (optionally preceded by whitespace) are comments,
and are ignored completely.

.. _search-sections:

Searches
========

A Weihnachtsgurke file is divided into several searches.  The text
``==`` on a line by itself divides the different searches in a file.
The search’s name should be on the first non-blank line, followed by a
colon.  The name is followed by the search pattern, in the format
described below.  Here is an example: ::

    name1:
    <searchterms>
    ==
    name2:
    <searchterms>

A double-equals at the beginning or end of the file (on a line before
``name1`` or after the second search terms) is optional, and ignored.
For convenience, a file containing a single search need not have a name;
in this case the name ``default`` will be applied.

Search names
------------

Search names may consist (only) of uppercase and lowercase letters of
the English alphabet, and numerals 0-9.

Search terms
============

A Weihnachtsgurke search term consists of four parts: a tag matcher, a
word matcher, a repeater, and a name.  These together constitute a line
of text (terminated with a newline character).  Several lines of search
terms can be combined: this requires all of them to match sequentially.

Matchers
--------

Both of the matchers use `Python regular expression syntax
<https://docs.python.org/2/library/re.html#regular-expression-syntax>`_.
Either one or both of the matchers can be supplied.  Neither can contain
a space character.  Both matchers are anchored – they must match the
whole tag or word.  If you wish to match only a prefix, include the text
``.*`` at the end of the matcher (a regular expression snippet which
matches any number of characters).  Thus, the following line matches
only a singular common noun: ::

    N

The following line matches a singular or plural common or proper noun:
::

    N|NS|NPR|NPRS

The following line matches any tag beginning with ``N`` (``N``, ``NS``,
``NEG``, ...): ::

    N.*

The tag matcher comes at the beginning of the line, and will typically
use uppercase letters to match tags in the corpus’s tagset.  The word
matcher is appended to the tag matcher, and enclosed in curly bracket
characters ``{}``.  Thus, the following line matches the word “cat”: ::

    {cat}

The following line matches “cat” only when it is a singular common noun:
::

    N{cat}


Note that the matching is **case sensitive**.  In order to match
case-insensitively, it is necessary to enclose each character in a
regular expression character class: ``[Cc][Aa][Tt]`` will match the
word “cat” case-insensitively.

Repeater
--------

The repeater specifies whether and how a match can repeat.  These are
inspired by regular expression syntax, but **must** be separated from
the matcher(s) by a space character.  There are three options:

optional
    The character ``?`` indicates that the given term may match zero or
    one times.

repeat
    The character ``+`` indicates that the given term may match one or
    more times.

optional-repeat
    The character ``*`` indicates that the given term may match zero or
    more times.

Thus, the following matches an NP with a determiner, optionally a single
adjective, and the noun “cat”.  This includes “the cat,” “the fluffy
cat,” “a cat,” etc.: ::

    D
    ADJ ?
    N{cat}

The following requires there to be at least one adjective describing the
cat, and permits multiple adjectives: “a fluffy cat,” “the fluffy
orange cat,” etc.: ::

    D
    ADJ +
    N{cat}

Finally, the following matches a modal followed by any number of adverbs
(even 0) followed by an infinitive verb: ::

    MD
    ADV *
    VB

*Note:* it is important to include the space between the matchers and
the repeater.  If this is not included, the repeater will be interpreted
as part of the matcher instead.  ``ADV *`` matches optional adverbs, but
``ADV*`` matches the tags ``AD``, ``ADV``, ``ADVV``, ....

The repeat and optional-repeat matchers are incompatible with specifying
a name; see below.

.. _named-captures:

Name
----

The name is completely optional.  If it is specified, the tag and word
of the matching line will be saved in the output in columns named
``name_tag`` and ``name_word`` respectively.  The name is specified by
the string `` as `` appended to the search term, followed by the name.
A name can consist (only) of uppercase and lowercase English letters and
digits 0-9.  Thus, the following terms will match NPs referring to cats,
and will allow us to tabulate the kinds of adjectives used to describe
them (by examining the ``adj_word`` column in the output): ::

    D
    ADJ as adj
    N{cat}

Tips and tricks
===============

Negative matches
----------------

Python has a facility for negative assertions in regular expressions,
which verifies that a certain expression does not match.  This is
expressed by the syntax ``(?!`` regex ``)``.  Note that this
construction does not advance the match window.  Thus, in common usage,
it should be followed by ``.*`` outside of the negative assertion.  For
an example of matching any word but *only* (and spelling variants), see
the following section.

TODO
----

TODO: what else to include here?


Example
=======

Here is an example search file which allows us to search for negative
declarative sentences with a pronoun subject which wither have or lack
*do* support: ::

    do:

    PRO as subject
    ADV *
    DOD|DOP
    ADV *
    NEG
    ADV *
    VB as verb

    ==

    simple:

    PRO as subject
    ADV *
    VBP|VBD as verb
    ADV|PRO *
    NEG
    {(?!only|onely).*} as foll1
    .* as foll2

Adverbs are allowed to intervene freely; the ``simple`` case also
allows pronouns to intervene between the verb and the negation, as in
*I saw it not.* The output of this search allows the subject and verb
to be examined (for example to eliminate errors tagging errors where
the subject is not actually a nominative case pronoun.)  The regular
expression associated with ``foll1`` is a negative match, covered in
the preceding section.  It excludes cases like “I know not only Bob but
also his family.”

A complete use of this search would involve further filtering of ``foll1``
and ``foll2`` to eliminate cases like “He told me not to call after 8pm,”
which contains a string (“he told me not”) which without this filtering
would be counted as a failure of the *do* support rule to apply, whereas
it is clearly not.

..
  TODO: for further info, see the methods section of my dissertation (link)
