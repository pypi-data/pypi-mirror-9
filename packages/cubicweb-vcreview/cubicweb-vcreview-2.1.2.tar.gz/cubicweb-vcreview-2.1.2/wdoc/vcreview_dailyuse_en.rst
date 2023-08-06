
Patches
~~~~~~~

A `Patch` is the entity in `vcreview`_ 's schema that represents a
mercurial changeset. `vcreview`_ has been designed for `evolve`_,
thus **one changeset** may have itself several versions. A `Patch`
is meant to keep track of this changeset evolution.

When a new draft changeset is detected, a new `Patch` entity is
created. The name of the `Patch` (its title) is the short
description of the changeset (first line of the commit message).

It is also possible to add "magic words" in the commit message to
automatically link a `Patch` with a `Ticket` (when `vcreview`_ is
used with the `trackervcs`_ cube)

.. _`vcreview`: https://www.cubicweb.org/project/cubicweb-vcreview
.. _`trackervcs`: https://www.cubicweb.org/project/cubicweb-trackervcs


Patches workflow
~~~~~~~~~~~~~~~~

When a patch is being constructed, the related `Patch` entity may be
in one of `in-progress`, `pending-review` or `reviewed` states.

Finished `Patch` objects are in one of `applied`, `rejected` or
`folded` states.

Submit a patch for review
+++++++++++++++++++++++++

By default, a new `Patch` (ie. a new draft changeset) is in the
`in-progress` state.  It can be moved to the `pending-review` state
either from the web interface or using the mercurial extension
provided in `logilab-devtools`_.

Note that the matching between the author of a changeset and a
``CWUser`` in the Cubicweb application is done using the email
address.

Reviewing a patch
+++++++++++++++++

When a `Patch` enters the `pending-review` state, a reviewer is
designated for this patch, and he is notified by email.

He can then either accept the patch, ask for modifications (normally
with comments, explanations and tasks that should be addressed before
resubmitting an amended changeset), or reject it.

Accepting a patch
+++++++++++++++++

When a patch has been reviewed, it may be integrated. The integration
is just a matter of changing the phase of the changeset.  When the
(draft) changeset linked to a `Patch` is set `public` (its phase is
changed from `draft` to `public`), this later `Patch` is
automatically set as `applied` state.


Folding a patch
+++++++++++++++

When a changeset is folded in another one, the corresponding `Patch`
is also put in the `folded` state.


Notification
~~~~~~~~~~~~

To be notified about `Patch` activity, you should mark yourself as
`interested in` each desired `Repository`.


Mercurial integration
~~~~~~~~~~~~~~~~~~~~~

We provide a Mercurial extension to easily interact with a vcreview
based forge from the mercurial's ``hg`` command. See the `hgext/jpl`_
mercurial extension from the `logilab-devtools`_ project.


It allows you to do things like:

.. code-block:: bash
		
   ~/hg/cubes/vcreview$ hg ask-review -r "draft() and ::."
   ~/hg/cubes/vcreview$ hg tasks
   [hooks] add a user preference to let user choose if a new patch must be in review (closes #4591842) https://www.cubicweb.org/4596209 (in-progress)

   [TODO] s/autocommit/autoreview (https://www.cubicweb.org/4873200)

   ~/hg/cubes/vcreview$ hg show-review -r "draft()"
   https://www.cubicweb.org/4894142        [pending-review]        stregouet
   [hooks] Only consider the most recent ancestor for patch comparison during rebase detection

   https://www.cubicweb.org/4881286        [pending-review]        celsoflores
   Replace user callback with ajaxfunc to mark task as done

   https://www.cubicweb.org/4861527        [pending-review]        arichardson
   [sobjects] Add a notification view for new patches

   https://www.cubicweb.org/4862301        [pending-review]        jroy
   [facets] add a facet to filter patches with tasks in 'todo' state

   https://www.cubicweb.org/4752934        [pending-review]        ddouard
   [hooks] Add author of a task or of a comment on a task to patch nosylist

   https://www.cubicweb.org/4835676        [pending-review]        arichardson
   [sobjects] Notify users interested in a Repository upon Patches activity


.. _`logilab-devtools`: http://www.logilab.org/902
.. _`hgext/jpl`: http://hg.logilab.org/review/logilab/devtools/file/tip/hgext/jpl/__init__.py
.. _`evolve`: http://mercurial.selenic.com/wiki/EvolveExtension

