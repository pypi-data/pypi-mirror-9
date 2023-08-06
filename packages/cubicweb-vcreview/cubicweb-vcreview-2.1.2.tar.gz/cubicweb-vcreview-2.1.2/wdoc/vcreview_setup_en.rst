
The idea is that you have a mercurial repository with `evolve`_
extension activated. In this repository, `draft`_ changesets will be
considered as work in progress that may require to be reviewed before
being integrated in the main code history.

You'll have to have this repository modeled as a CubicWeb entity using
vcsfile's `Repository` entity type.

.. Important:: You **must** select the option "import revision
   content" of the `Repository` otherwise you won't see any patch,
   and consequently won't have any review process.

A background process will then import the repository content and will:

- create a `Patch` entity for any new draft changeset,

- update an existing `Patch` when a draft changeset is updated,

- properly manage chagesets that are `folded`_, split or `pruned`_,

- if using the `trackervcs`_ cube and if the `Repository` is related
  to a `Project`, it will also look for patterns (regular
  expressions) in the commit message to link the `Patch` to a
  `Ticket` (see the `tracker`_ cube for more details on tickets and
  `trackervcs`_ for more details on `Repository` and `Project`
  integration),

- set the `Patch` as `applied` when the phase of the changeset is
  moved from `draft` to `public`,

A `Patch` entity can have the following workflow states:

- `in progress`: the patch is in progress, no code review has been
  asked by the author of the changeset, or a reviewer has asked for changes

- `pending review`: someone (usually the author of the changeset) asked for review,

- `reviewed`: someone (usually the designated reviewer) accepted the
  patch as ready for integration

- `applied`: the changeset linked with the `Patch` is `public`;
  usually, it is the responsibility of the integrator of the project
  to 'integrate' changesets (somehow the equivalent of merging a pull
  request) by changing their phase to `public`

- `rejected`: the changeset has been `pruned`,

- `folded`: the changeset has been `folded` with another changeset,

- `outdated`: the changeset has been obsoleted (i.e. replaced by a new
  version of the changeset), but the new version of the changeset is
  not (yet) available; if it (later) becomes available, the
  `Patch` will the be in the `in progress` state.


When a `Patch` is created in response to a new draft changeset being
imported by cubicweb, it will by default remain in the `in progress`
workflow state. This behavior can be modified as a user preference
(the `vcreview.autoreview` preference), so any new `Patch` entity is
directly in the `pending-review` state. The ownership of the `Patch` is
based on the mercurial changeset's `author` metadata (which is normally
something like `Firstname Lastname <user@somewehere>`). The user
preference used to select the workflow state of a newly created `Patch`
is the one matching the email address of the `author` of the changeset.


.. _`evolve`: http://mercurial.selenic.com/wiki/EvolveExtension
.. _`draft`: http://mercurial.selenic.com/wiki/Phases#Available_Phases
.. _`tracker`: http://www.cubicweb.org/project/cubicweb-tracker
.. _`trackervcs`: http://www.cubicweb.org/project/cubicweb-trackervcs
.. _`folded`: http://evolution.experimentalworks.net/doc/user-guide.html#id10
.. _`pruned`: http://evolution.experimentalworks.net/doc/user-guide.html#id8
