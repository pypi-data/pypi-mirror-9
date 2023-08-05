Basicstrap style theme for Sphinx. Using Twitter Bootstrap.

|travis| |coveralls| |downloads| |version| |license| |requires|

Features
========
* Provide ``basicstrap`` theme for render HTML document.
* Using `Twitter Bootstrap <http://twitter.github.com/bootstrap/>`_.
* Support Responsive Design.
* Change the layout flexibility.
* `Google Web Fonts <http://www.google.com/webfonts>`_ available.
* `Font Awesome <http://fortawesome.github.com/Font-Awesome/>`_ available.
* Easily change the design. by `Bootswatch <http://bootswatch.com/>`_.


Set up
======
Make environment with pip::

    $ pip install sphinxjp.themes.basicstrap

Convert Usage
=============
setup conf.py with::

    extensions += ['sphinxjp.themes.basicstrap']
    html_theme = 'basicstrap'

and run::

    $ make html

.. caution:: Caution when upgrading from 0.1.1 to 0.2.0

 * In version 0.1.1, the header color was black in the default, it has become white in 0.2.0.
 * If you like the black color header, please set to True the 'header_inverse' option.

Requirement
===========
* Python 2.6, 2.7, 3.3, 3.4 or later.
* Sphinx 1.2.x or later.

Using
===========
* Twitter Bootstrap 3.2.0 and 2.3.2
* jQuery 1.8.3
* Bootswatch
* Font Awesome 4.2.0

License
=======

* sphinxjp.themes.basicstrap Licensed under the `MIT license <http://www.opensource.org/licenses/mit-license.php>`_ .
* `Twitter Bootstrap is licensed under the Apache license <https://github.com/twitter/bootstrap/blob/master/LICENSE>`_.
* `Bootswatch is licensed under the Apache license <https://github.com/thomaspark/bootswatch/blob/gh-pages/LICENSE>`_.
* `Font Awesome is licensed under the license <https://github.com/FortAwesome/Font-Awesome>`_.
* `Geo is licensed under the license <https://github.com/divshot/geo-bootstrap>`_

See the LICENSE file for specific terms.

.. |travis| image:: https://travis-ci.org/tell-k/sphinxjp.themes.basicstrap.svg?branch=master
    :target: https://travis-ci.org/tell-k/sphinxjp.themes.basicstrap


.. |coveralls| image:: https://coveralls.io/repos/tell-k/sphinxjp.themes.basicstrap/badge.png
    :target: https://coveralls.io/r/tell-k/sphinxjp.themes.basicstrap
    :alt: coveralls.io

.. |downloads| image:: https://pypip.in/d/sphinxjp.themes.basicstrap/badge.png
    :target: http://pypi.python.org/pypi/sphinxjp.themes.basicstrap/
    :alt: downloads

.. |version| image:: https://pypip.in/v/sphinxjp.themes.basicstrap/badge.png
    :target: http://pypi.python.org/pypi/sphinxjp.themes.basicstrap/
    :alt: latest version

.. |license| image:: https://pypip.in/license/sphinxjp.themes.basicstrap/badge.png
    :target: http://pypi.python.org/pypi/sphinxjp.themes.basicstrap/
    :alt: license

.. |requires| image:: https://requires.io/github/tell-k/sphinxjp.themes.basicstrap/requirements.svg?branch=master
    :target: https://requires.io/github/tell-k/sphinxjp.themes.basicstrap/requirements/?branch=master
    :alt: requires.io

Authors
=======

Sphinx template, css, packaging
-------------------------------
* tell-k <ffk2005 at gmail.com>

Contributors
-------------------------------

Great thanks!

* pierre-rouanet
* westurner

History
=======

0.4.2(Feb 16, 2015)
---------------------

* `#18 Header search box. <https://github.com/tell-k/sphinxjp.themes.basicstrap/issues/18>`_
* `#16 Drop Python-3.2 support. <https://github.com/tell-k/sphinxjp.themes.basicstrap/issues/16>`_
* `#15 UBY: optimize for responsive xs. <https://github.com/tell-k/sphinxjp.themes.basicstrap/issues/15>`_ Thanks to westurner.
* Fixed bug `#17 Switching of the inner theme is too slow. <https://github.com/tell-k/sphinxjp.themes.basicstrap/pull/17>`_
* Fixed bug `#14 Typo. <https://github.com/tell-k/sphinxjp.themes.basicstrap/pull/14>`_ Thanks to mhor.
* Fixed bug `#13 Invalid body css. <https://github.com/tell-k/sphinxjp.themes.basicstrap/pull/13>`_ Thanks to 3rdarm.
* Support wheel format.

0.4.1(Sep 29, 2014)
---------------------

* Fixed bug `#11 Font Icon does not appear.  <https://github.com/tell-k/sphinxjp.themes.basicstrap/issues/11>`_.

0.4.0(Sep 29, 2014)
---------------------

* `#8 Navbar hides initial content when jumping to in-page anchor <https://github.com/tell-k/sphinxjp.themes.basicstrap/pull/8>`_.
* `#7 Added WAI-ARIA roles and optional navbar-fixed-top setting <https://github.com/tell-k/sphinxjp.themes.basicstrap/pull/7>`_.
* New Support Twitter Bootstrap ver3.2.0
* New Support Bootswatch Theme for Twitter Bootstrap ver3.2.0
* Add new Innner Theme `bootswatch-darkly <http://bootswatch.com/darkly/>`_ from Bootswatch.
* Add new Innner Theme `bootswatch-yeti <http://bootswatch.com/darkly/>`_ from Bootswatch.
* Add new Innner Theme `bootswatch-paper <http://bootswatch.com/paper/>`_ from Bootswatch.
* Add new Innner Theme `bootswatch-sandstone <http://bootswatch.com/sandstone/>`_ from Bootswatch.
* Add new Innner Theme `bootswatch-lumen <http://bootswatch.com/lumen/>`_ from Bootswatch.
* Improve menu for smartphone.
* Update Font Awesome ver4.2.0
* Remove bootstrap.py and buildout.cfg
* Starting Travis CI and Coveralls.

0.3.2(Dec 31, 2013)
---------------------

* Add tox test.
* Python3 support.

0.3.1(Nov 4, 2013)
---------------------
* Update stylesheet for 'h1_size' - 'h6_size' options.
* Changed. When you visit in the smartphone, GoogleWeb fonts to not used.

0.3.0(Jun 28, 2013)
---------------------
* Fixed bug `#5 "Goolgle Web Font" is not reflected <https://github.com/tell-k/sphinxjp.themes.basicstrap/issues/5>`_.
* Update Twitter Bootstrap ver2.3.2
* Update Bootswatch Theme for Twitter Bootstrap ver2.3.2
* Update Font Awesome ver3.2.1
* Add new Innner Theme `bootswatch-flatly <http://bootswatch.com/flatly/>`_ from Bootswatch.
* Add new Innner Theme `geo-bootstrap <http://divshot.github.io/geo-bootstrap/>`_.
* Add new option of html_theme_optios. 'h1_size' - 'h6_size'.

0.2.0(Feb 11, 2013)
---------------------
* Fixed bug `#1 "Quick Search" in the table of contents is missing <https://github.com/tell-k/sphinxjp.themes.basicstrap/issues/1>`_.
* `#2 adding "navbar-inverse" option <https://github.com/tell-k/sphinxjp.themes.basicstrap/issues/4>`_.
* Integrated Bootswatch
* Integrated Font Awesome ver3.0

0.1.1 (Dec 26, 2012)
---------------------
* Adjust css
* Update Twitter Bootstrap ver2.2.2
* Update jQuery ver1.8.3

0.1.0 (Dec 23, 2012)
---------------------
* First release


