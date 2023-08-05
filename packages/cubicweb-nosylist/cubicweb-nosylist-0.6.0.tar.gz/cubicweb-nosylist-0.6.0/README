Summary
-------

This cube provides nosy-list "a la roundup" usable to notify users of events
they subscribed to such as content modification, state change, etc.

A nosy list is an ad-hoc mailing list for entities where to which user can
register, or be automatically registered on some action.

Usage
-----
to use this cube:

1. add to your schema::

     CWUser interested_in X
     X nosy_list CWUser

   where X are entity types considered as notification base, eg controlling
   who will be notified for events related to X.


2. configure on which relation the nosy list should be propagated

   .. sourcecode:: python

      from cubes.nosylist import hooks as nosylist_hooks

      # relations where the "main" entity (eg holding the reference nosy list, so
      # should be in one `X` types cited above) is the subject of the relation
      nosylist_hooks.S_RELS |= set(('documented_by', 'attachment', 'screenshot'))

      # relations where the "main" entity (eg holding the reference nosy list, so
      # should be in one `X` types cited above) is the object of the relation
      nosylist_hooks.O_RELS |= set(('for_version', 'comments'))

3. write hooks that add user to nosy list when desired (for instance, when a
   user is adding a comment to an entity, add him to the entity's nosy list)

4. define your notification views / hooks, which should rely on the default
   recipients finder mecanism to get notified users (automatic if you're using
   cubicweb base classes)
