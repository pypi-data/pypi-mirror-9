from cubicweb import ValidationError
from cubicweb.server import hook
from cubicweb.predicates import relation_possible

class INotificationBaseAddedHook(hook.Hook):
    """automatically register the user creating a ticket as interested by it
    """
    __regid__ = 'notification_base_added_hook'
    # action=None to by pass security checking
    __select__ = hook.Hook.__select__ & relation_possible('interested_in', 'object', 'CWUser',
                                                          action=None)
    events = ('after_add_entity',)

    def __call__(self):
        session = self._cw
        if not session.is_internal_session:
            session.execute('SET U interested_in X WHERE X eid %(x)s, U eid %(u)s',
                            {'x': self.entity.eid, 'u': session.user.eid})


class InterestedInAddHook(hook.Hook):
    """adds relation nosy_list corresponding to relation interested_in
    """
    __regid__ = 'add_interested_in_hook'
    __select__ = hook.Hook.__select__ & hook.match_rtype('interested_in')
    events = ('after_add_relation',)

    def __call__(self):
        self._cw.execute('SET X nosy_list U WHERE X eid %(x)s, U eid %(u)s, '
                         'NOT X nosy_list U',
                         {'x': self.eidto, 'u': self.eidfrom})


class InterestedInDelHook(hook.Hook):
    """deletes relation nosy_list corresponding to relation interested_in
    """
    __regid__ = 'deleted_interested_in_hook'
    __select__ = hook.Hook.__select__ & hook.match_rtype('interested_in')
    events = ('after_delete_relation',)

    def __call__(self):
        self._cw.execute('DELETE X nosy_list U WHERE X eid %(x)s, U eid %(u)s',
                         {'x': self.eidto, 'u': self.eidfrom})


# relations where the "main" entity is the subject
S_RELS = set()
# relations where the "main" entity is the object
O_RELS = set()

class NosyListPropagationHook(hook.PropagateRelationHook):
    """propagate permissions when new entity are added"""
    __regid__ = 'nosy_list_propagation_hook'
    __select__ = hook.Hook.__select__ & hook.match_rtype_sets(S_RELS, O_RELS)

    main_rtype = 'nosy_list'
    subject_relations = S_RELS
    object_relations = O_RELS

# relations where the "main" entity is the subject/object that should be skipped
# when propagating to entities linked through some particular relation
SKIP_S_RELS = set()
SKIP_O_RELS = set()

class NosyListAddPropagationHook(hook.PropagateRelationAddHook):
    """propagate permissions when new entity are added"""
    __regid__ = 'nosy_list_add_propagation_hook'
    __select__ = hook.Hook.__select__ & hook.match_rtype('nosy_list')

    subject_relations = S_RELS
    object_relations = O_RELS
    skip_subject_relations = SKIP_S_RELS
    skip_object_relations = SKIP_O_RELS


class NosyListDelPropagationHook(hook.PropagateRelationDelHook):
    __regid__ = 'nosy_list_del_propagation_hook'
    __select__ = hook.Hook.__select__ & hook.match_rtype('nosy_list')

    subject_relations = S_RELS
    object_relations = O_RELS
    skip_subject_relations = SKIP_S_RELS
    skip_object_relations = SKIP_O_RELS


def registration_callback(vreg):
    vreg.register_all(globals().values(), __name__)

    import os
    if os.environ.get('NOSYLIST_INSTRUMENT'):
        from cubicweb.devtools.instrument import CubeTracerSet
        global S_RELS, O_RELS
        S_RELS = CubeTracerSet(vreg, S_RELS)
        O_RELS = CubeTracerSet(vreg, O_RELS)
