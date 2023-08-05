===========
WS Recorder
===========

Changelog
=========

* 0.0.4:
    * Added a new function for lowering text (Mathieu Leduc-Hamel).

* 0.0.3:
    * Defined default prefix 'xp2f'.

* 0.0.2:
    * Changed default namespace.

* 0.0.1:
    * Added function: string-join.

Support
==========

* Environments: Python 2.6, Python 2.7, Python 3.2, Python 3.3, Python 3.4, PyPy


Description
===========

Set of Xpath2 functions which you can register in lxml. User register all or chosen functions
and use them in own xpaths. Xpaths are accessible under default namespace:
http://kjw.pt/xpath2-functions or empty namespace if needed.


Usage
=====

Example::

    from lxml import etree
    import xpath2_functions

    # registering all available functions in default namespace
    xpath2_functions.register_functions(etree)

    # registering chosen functions in the empty namespace
    xpath2_functions.register_functions(etree, ns=None, functions=['string-join'])


Functions
=========

* **string-join** (arg1 as `xs:string`, arg2 as `xs:string`) - returns an arg1
  created by concatenating the members of the $arg1 sequence using $arg2 as
  a separator. If the value of $arg2 is the zero-length string, then the members
  of $arg1 are concatenated without a separator.
* **lower-case** (arg1 as `xs:string`) - returns an arg1 converted to lower-cased
  string.


Contributors
============

* Kamil Kujawinski
* Mathieu Leduc-Hamel (xpath functions: lower-case)
