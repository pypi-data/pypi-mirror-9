=====
Kotti
=====

|pypi|_
|downloads_month|_
|license|_
|build status stable|_

.. |pypi| image:: https://img.shields.io/pypi/v/Kotti.svg?style=flat-square
.. _pypi: https://pypi.python.org/pypi/Kotti/

.. |downloads_month| image:: https://img.shields.io/pypi/dm/Kotti.svg?style=flat-square
.. _downloads_month: https://pypi.python.org/pypi/Kotti/

.. |license| image:: https://img.shields.io/pypi/l/Kotti.svg?style=flat-square
.. _license: http://www.repoze.org/LICENSE.txt

.. |build status stable| image:: https://img.shields.io/travis/Kotti/Kotti/stable.svg?style=flat-square
.. _build status stable: http://travis-ci.org/Kotti/Kotti

Kotti is a high-level, Pythonic web application framework based on Pyramid_ and SQLAlchemy_.
It includes an extensible Content Management System called the Kotti CMS (see below).

Kotti is most useful when you are developing applications that

- have complex security requirements,
- use workflows, and/or
- work with hierarchical data.

Built on top of a number of *best-of-breed* software components,
most notably Pyramid_ and SQLAlchemy_,
Kotti introduces only a few concepts of its own,
thus hopefully keeping the learning curve flat for the developer.


.. _Pyramid: http://docs.pylonsproject.org/projects/pyramid/dev/
.. _SQLAlchemy: http://www.sqlalchemy.org/

Kotti CMS
=========

You can **try out the Kotti CMS** on `Kotti's demo page`_.

Kotti CMS is a content management system that's heavily inspired by Plone_.
Its **main features** are:

- **User-friendliness**: editors can edit content where it appears;
  thus the edit interface is contextual and intuitive

- **WYSIWYG editor**: includes a rich text editor

- **Responsive design**: Kotti builds on `Bootstrap`_, which
  looks good both on desktop and mobile

- **Templating**: you can extend the CMS with your own look & feel
  with almost no programming required

- **Add-ons**: install a variety of add-ons and customize them as well
  as many aspects of the built-in CMS by use of an INI configuration
  file

- **Security**: the advanced user and permissions management is
  intuitive and scales to fit the requirements of large organizations

- **Internationalized**: the user interface is fully translatable,
  Unicode is used everywhere to store data

.. _Kotti's demo page: http://kottidemo.danielnouri.org/
.. _Plone: http://plone.org/
.. _Bootstrap: http://getbootstrap.com/

License
=======

Kotti is offered under the BSD-derived `Repoze Public License <http://repoze.org/license.html>`_.

Install
=======

See `installation instructions`_.

.. _installation instructions: http://kotti.readthedocs.org/en/latest/first_steps/installation.html

Support and Documentation
=========================

Read Kotti's extensive `documentation <http://kotti.readthedocs.org/>`_ on `Read the Docs <https://readthedocs.org/>`_.

If you have questions or need help, you can post on our `mailing list / forum <http://groups.google.com/group/kotti>`_ or join us on IRC: `#kotti on irc.freenode.net <irc://irc.freenode.net/#kotti>`_.

If you think you found a bug, open an issue on or `Github bugtracker <https://github.com/Kotti/Kotti/issues>`_.

Development
===========

|build status master|_
|coveralls|_
|codacy|_

.. requirements need to be upgraded before we shoff off
   |requires.io|_

|gh_forks|_
|gh_stars|_

Kotti is actively developed and maintained.
We adhere to `high quality coding standards`_, have an extensive test suite with `high coverage`_ and use `continuous integration`_.

Contributions are always welcome, read our `contribution guidelines`_ and visit our `Github repository`_.

.. |build status master| image:: https://img.shields.io/travis/Kotti/Kotti/master.svg?style=flat-square
.. _build status master: http://travis-ci.org/Kotti/Kotti
.. _continuous integration: http://travis-ci.org/Kotti/Kotti

.. |requires.io| image:: https://img.shields.io/requires/github/Kotti/Kotti.svg?style=flat-square
.. _requires.io: https://requires.io/github/Kotti/Kotti/requirements/?branch=master

.. |gh_forks| image:: https://img.shields.io/github/forks/Kotti/Kotti.svg?style=flat-square
.. _gh_forks: https://github.com/Kotti/Kotti/network

.. |gh_stars| image:: https://img.shields.io/github/stars/Kotti/Kotti.svg?style=flat-square
.. _gh_stars: https://github.com/Kotti/Kotti/stargazers

.. |coveralls| image:: https://img.shields.io/coveralls/Kotti/Kotti.svg?style=flat-square
.. _coveralls: https://coveralls.io/r/Kotti/Kotti
.. _high coverage: https://coveralls.io/r/Kotti/Kotti

.. |codacy| image:: https://img.shields.io/codacy/ad44331fcd904d338c074f2ca3e6a810.svg?style=flat-square
.. _codacy: https://www.codacy.com/public/disko/Kotti
.. _high quality coding standards: https://www.codacy.com/public/disko/Kotti

.. _contribution guidelines: http://kotti.readthedocs.org/en/latest/contributing.html
.. _Github repository: https://github.com/Kotti/Kotti
