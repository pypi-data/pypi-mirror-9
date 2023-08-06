===========================
 Installation instructions
===========================

In order to install this program, you need to have the ``pip`` python
package manager installed.  Check if this is the case by issuing the
following command in a terminal: ::

    which pip

If you see a file path printed, you have the program installed.  If not,
you should `install it <https://pip.pypa.io/en/latest/installing.html>`_.

Once pip is installed, install Weihnachtsgurke by running: ::

    pip install weihnachtsgurke

You will probably need to use the ``sudo`` command to assume
administrator privileges for the purpose of the install (otherwise you
will get an error message about insufficient permissions).  If you do
not have root privileges, you can install using this command: ::

    pip install --user weihnachtsgurke

You will then need to add the directory ``~yourusername/.local/bin``
to your shell’s ``$PATH``.  Here are `instructions for doing this
<http://askubuntu.com/questions/60218/how-to-add-a-directory-to-my-path>`_.

The corpus files that this program works with are currently in
preparation for public release.  When they are available, this space
will be updated with instructions on how to obtain them.

..
  TODO

Postscript: for Windows users
=============================

These installation instructions are designed for Unix systems, such as
Linux and Mac OS X.  It assumes familiarity with the command line.  If
you use Windows on a daily basis, you will be well-served by gaining
access to a Unix system for your research.  (This program is the merest
tip of the iceberg of corpus programs which work best on Unix).  With
modern hardware it is possible to run Linux in a virtual machine on
Windows, using entirely Free software.  Virtual private servers which
run Linux can also be rented for a few dollars per month.
