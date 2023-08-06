================================
Notes and handouts in rst2beamer
================================

Usage
-----

The LaTeX source for the corresponding Beamer example without notes can be produced::

    rst2beamer notes.rst notes.tex

Notes will be included (on the right) via::

    rst2beamer --shownotes true notes.rst notes_shownotes_true.tex

A presentation with only the notes can be produced::

        rst2beamer --shownotes only notes.rst notes_shownotes_only.tex



Showing notes
-------------

Beamer (and rst2beamer) support the inclusion of notes in a presentation. By default, these won't show up in the generated presentation unless requested. The appearance of notes is set with the commandline argument ``--shownotes``. For example::

   rst2beamer --shownotes <option> mypresentation.rst

where ``option`` can be:

    false
        don't show any notes (the default)

    true
        show notes as per ``right``

    only
        show only the notes, not the presentation

    left, right, top, bottom
        show the notes in the given position to the presentation


The note directive
------------------

Notes can be included with the ``beamer-note`` directive.

.. beamer-note::

    This is an example.

Multiple notes can be included in one slide.

.. beamer-note::

    This is an example of that.

Slides without any notes will produce an empty note slide.

.. beamer-note::

    Look at the previous slide for an example of that.


Notes as containers
-------------------

The custom r2b directives won't be recognised by any writer other than
rst2beamer. Therefore, we allow certain containers (which most other
writers should recognise and at worst ignore) to act like notes.

.. container:: beamer-note

   Compatibility is important

Any container with the name 'beamer-note' or 'beamer-note' will
be handled like the notes directive.

.. container:: beamer-note

   Important: I must find out why the container names are being munged.
