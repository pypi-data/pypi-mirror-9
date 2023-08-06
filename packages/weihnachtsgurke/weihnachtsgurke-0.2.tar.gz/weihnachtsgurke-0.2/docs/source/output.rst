.. Copyright 2015 University of York
   Author: Aaron Ecay

=======================
 Weihnachtsgurke output
=======================

Weinachtsgurke gives its output as a csv file, suitable for import into
R, Python, or other data analysis tools.  The file contains the
following columns:

``file``
    The name of the file in which the match was found, up to the first
    period character in the file name.

``rule``
    The :ref:`name of the search <search-sections>` which matched this
    data row.

named captures
    The word and tag for any search terms which have been :ref:`captured
    by name <named-captures>`.

``match``
    The string which matches the indicated search query

``sentence``
    The entire sentence in which the match is embedded.  Weihnachtsgurke
    will return only one match per sentence (specifically the first one)
    even if a sentence contains multiple matches.  (TODO: lift that
    restriction).
