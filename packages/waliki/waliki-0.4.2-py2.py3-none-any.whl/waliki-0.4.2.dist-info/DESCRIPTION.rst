**Waliki** is an extensible wiki app for Django with a Git backend.


.. attention:: It's in an early development stage. I'll appreciate your feedback and help.


.. image:: https://badge.fury.io/py/waliki.png
    :target: https://badge.fury.io/py/waliki

.. image:: https://travis-ci.org/mgaitan/waliki.png?branch=master
    :target: https://travis-ci.org/mgaitan/waliki

.. image:: https://coveralls.io/repos/mgaitan/waliki/badge.png?branch=master
    :target: https://coveralls.io/r/mgaitan/waliki?branch=master

.. image:: https://readthedocs.org/projects/waliki/badge/?version=latest
   :target: https://readthedocs.org/projects/waliki/?badge=latest
   :alt: Documentation Status

.. image:: https://pypip.in/wheel/waliki/badge.svg
    :target: https://pypi.python.org/pypi/waliki/
    :alt: Wheel Status

:home: https://github.com/mgaitan/waliki/
:demo: http://waliki.pythonanywhere.com
:documentation: http://waliki.rtfd.org
:twitter: `@Waliki_ <http://twitter.com/Waliki_>`_ // `@tin_nqn_ <http://twitter.com/tin_nqn_>`_
:group: https://groups.google.com/forum/#!forum/waliki-devs
:license: `BSD <https://github.com/mgaitan/waliki/blob/master/LICENSE>`_

At a glance, Waliki has these features:

- File based content storage.
- UI based on Bootstrap 3 and CodeMirror
- Version control and concurrent edition for your content using Git
- Extensible architecture with plugins
- Markdown or reStructuredText support (and it's easy to add extensions)
- A simple ACL system
- Per page attachments
- Realtime collaborative edition via togetherJS
- Wiki content embeddable in any django template
- Works with Python 2.7, 3.3, 3.4 or PyPy in Django 1.5 or newer (including 1.8b1)

How to start
------------

Install it with pip::

    $ pip install waliki[all]

Or the development version::

    $ pip install https://github.com/mgaitan/waliki/tarball/master


Add ``waliki`` and the optionals plugins to your INSTALLED_APPS::

    INSTALLED_APPS = (
        ...
        'waliki',
        'waliki.git',           # optional but recommended
        'waliki.attachments',   # optional but recommended
        'waliki.pdf',           # optional
        'waliki.slides',        # optional
        'waliki.togetherjs',    # optional
        ...
    )

Include ``waliki.urls`` in your project's ``urls.py``. For example::

    urlpatterns = patterns('',
        ...
        url(r'^wiki/', include('waliki.urls')),
        ...
    )

Sync your database::

    $ python manage.py migrate   # syncdb in django < 1.7


.. tip::

   Already have content? Put it in your ``WALIKI_DATA_DIR`` and run::

        $ python manage.py sync_waliki


Why *Waliki* ?
----------------

**Waliki** is an `Aymara <http://en.wikipedia.org/wiki/Aymara_language>`_ word that means *all right*, *fine*.

It sounds a bit like *wiki*, has a meaningful sense and also plays with the idea of using a non-mainstream language [1]_ .

And last but most important, it's a humble tribute to the bolivian president `Evo Morales <http://en.wikipedia.org/wiki/Evo_Morales>`_.

.. [1] *wiki* itself is a hawaiian word




Changelog
---------

0.4.2 (2015-03-31)
++++++++++++++++++

- Fixed conflict with a broken dependecy


0.4.1 (2015-03-31)
++++++++++++++++++

- Marked the release as beta (instead of alpha)
- Improves on setup.py and the README

0.4 (2015-03-31)
++++++++++++++++

**Implemented enhancements:**

- Implemented views to add a new, move and delete pages
- Implemented real-time collaborative editing via together.js
  (`#33 <https://github.com/mgaitan/waliki/issues/33>`__)
- Added pagination in *what changed* page
- Added a way to extend waliki's docutils with directives and transformation for
- A deep docs proofreading by `chuna <https://github.com/chuna>`__

**Closed issues:**

- Edit view redirect to detail if the page doesn't exist
  (`#37 <https://github.com/mgaitan/waliki/issues/37>`__)
-  waliki\_box fails with missing slug
   `#40 <https://github.com/mgaitan/waliki/issues/40>`__
-  can't view diffs on LMDE
   `#60 <https://github.com/mgaitan/waliki/issues/60>`__

-  fix typos in tutorial
   `#76 <https://github.com/mgaitan/waliki/pull/76>`__
   (`martenson <https://github.com/martenson>`__)

-  Fix build with Markups 0.6.
   `#63 <https://github.com/mgaitan/waliki/pull/63>`__
   (`loganchien <https://github.com/loganchien>`__)

-  fixed roundoff error for whatchanged pagination
   `#61 <https://github.com/mgaitan/waliki/pull/61>`__
   (`aszepieniec <https://github.com/aszepieniec>`__)

-  Enhance slides `#59 <https://github.com/mgaitan/waliki/pull/59>`__
   (`loganchien <https://github.com/loganchien>`__)

-  Fix UnicodeDecodeError in waliki.git.view.
   `#58 <https://github.com/mgaitan/waliki/pull/58>`__
   (`loganchien <https://github.com/loganchien>`__)



0.3.3 (2014-11-24)
++++++++++++++++++

- Tracking page redirections
- fix bugs related to attachments in `sync_waliki`
- The edition form uses crispy forms if it's installed
- many small improvements to help the integration/customization


0.3.2 (2014-11-17)
++++++++++++++++++

- Url pattern is configurable now. By default allow uppercase and underscores
- Added ``moin_migration_cleanup``, a tool to cleanup the result of a moin2git_ import
- Improve git parsers for *page history* and *what changed*

.. _moin2git: https://github.com/mgaitan/moin2git


0.3.1 (2014-11-11)
++++++++++++++++++

- Plugin *attachments*
- Implemented *per namespace* ACL rules
- Added the ``waliki_box`` templatetag: use waliki content in any app
- Added ``entry_point`` to extend templates from plugins
- Added a webhook to pull and sync change from a remote repository (Git)
- Fixed a bug in git that left the repo unclean

0.2 (2014-09-29)
++++++++++++++++

- Support concurrent edition
- Added a simple ACL system
- ``i18n`` support (and locales for ``es``)
- Editor based in Codemirror
- Migrated templates to Bootstrap 3
- Added the management command ``waliki_sync``
- Added a basic test suite and setup Travis CI.
- Added "What changed" page (from Git)
- Plugins can register links in the nabvar (``{% navbar_links %}``)

0.1.2 / 0.1.3 (2014-10-02)
++++++++++++++++++++++++++

* "Get as PDF" plugin
* rst2html5 fixes

0.1.1 (2014-10-02)
++++++++++++++++++

* Many Python 2/3 compatibility fixes

0.1.0 (2014-10-01)
++++++++++++++++++

* First release on PyPI.

