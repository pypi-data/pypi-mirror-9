.. _release:

====================================
 Doing a Total Open Station release
====================================

Translations
============

When the release is approaching and the source strings are not going
to change, declare string freeze. Source messages should be updated
with one of ``xgettext``, ``pygettext`` or Babel_ (with the
``extract_messages`` command), producing ``totalopenstation.pot``.

If there is an existing translation, ``msgmerge`` or Babel
``update_catalog`` should be used to update.

Translators should be invited to submit new translations, either via
``.po`` files or Transifex_.

When the translation period is over, pull the updated ``.po`` files
from Transifex with::

    tx pull -r totalopenstation.totalopenstation-app -a

and check that the files are updated. Commit new files separately from updates.

.. _Babel: http://babel.edgewall.org/wiki/Documentation/0.9/setup.html
.. _Transifex: https://www.transifex.com/projects/p/totalopenstation/resource/totalopenstation-app/

If using Babel, compile the translated messages with::

    python setup.py compile_catalog -d locale

Documentation
=============

The documentation is included in the source tree, and is published
online at <http://totalopenstation.readthedocs.org/>_.

Manual pages for the three scripts provided with TOPS are not
available at the moment.

Release
=======

The version number is declared in ``totalopenstation/__init__.py`` and
is propagated in other places from there, including ``setup.py`` and
the “About” dialog.

A *source distribution* is made using::

  python setup.py sdist

A *built distribution* is made using (e.g. for Windows installer)::

  python setup.py bdist --formats wininst


