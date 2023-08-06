lrparsing
=========

  lrparsing is an LR(1) parser whose grammar rules
  are Python expressions.

  There is extensive documentation shipped as reStructured
  text.  The build system renders this in the standard Python
  HTML documentation style.

  All documentation is readable online at the home page:
    http://lrparsing.sourceforge.net/


Dependencies
------------

  Python2 >= 2.7, http://www.python.org
  or Python3, http://www.python.org


Building and Installing
-----------------------

  Packages are available for Debian style distributions
  at the home page, and the module is available on pypi and
  can be installed using pip.  If you install using one of
  these methods you can skip this section.

  Building is optional.  There is only one source file and
  it can be used directly.

  The build dependencies are:
    - Python2 and/or Python3 development system,
      http://www.python.org
    - A POSIX system (make, unix shell, sed, etc).

  Unit testing requires the following additional dependencies:
    - pep8, http://pypi.python.org/pypi/pep8
    - python-coverage, http://nedbatchelder.com/code/coverage

  To build the re-distributable, in the directory containing
  this file run:
    make

  To install, in the directory containing this file run:
    make install

  To run the test suite, in the directory containing this file run:
    make test


License
-------

  Copyright (c) 2013-2014,2015 Russell Stuart.

  This program is free software: you can redistribute it and/or modify
  it under the terms of the GNU Affero General Public License as published
  by the Free Software Foundation, either version 3 of the License, or (at
  your option) any later version.
 
  The copyright holders grant you an additional permission under Section 7
  of the GNU Affero General Public License, version 3, exempting you from
  the requirement in Section 6 of the GNU General Public License, version 3,
  to accompany Corresponding Source with Installation Information for the
  Program or any work based on the Program. You are still required to
  comply with all other Section 6 requirements to provide Corresponding
  Source.
 
  This program is distributed in the hope that it will be useful, but
  WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
  Affero General Public License for more details.


--
Russell Stuart
2014-Jun-06
