cloudmesh_base 
==============

A set of simple functions that are used in cloudmesh but also could be used by other projects.

You can install it in one of two ways. 

Installation with explicit calls
--------------------------------

::

  pip install -r requirements.txt
  python setup.py install
  
Install with custom install commands
------------------------------------

The above is also available as integrated command::

  python setup.py all
  
It will in addition to the install also install the requirements

Provided Functionality
----------------------------------------------------------------------

* ConfigDict -- an ordered dictionary to read configurations frm YAML
  files
* Shell -- a convenient wrapper to python sh so that pylint does not
  complain all the time when importing commands from sh
* dotdict -- a simple dict with dot notation
* gitinfo -- get some information about authors and their statistics
  for a git repository
* menu -- a simple ascii menu so we can chose easily from options
* ping -- a simple ping (see also Shell)
* ssh_config -- a simple tool to read ./ssh/config into a dict
* stopwatch -- a simple stopwatch to measure times
* tables -- a simple table printer that prins dicts in a uniform table
* util -- a number of useful functions including yn_choice, banner,
  path_expand, introspecting and printing the method name at runtime,
  copy files, replace dict values in a string similar but less
  complicated to .format, read a file to a string, write a string to a file
 
  

Source Code
----------------------------------------------------------------------

* https://github.com/cloudmesh/base
