"""nosy list based recipients finder

:organization: Logilab
:copyright: 2009-2010 LOGILAB S.A. (Paris, FRANCE), license is LGPL v2.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
:license: GNU Lesser General Public License, v2.1 - http://www.gnu.org/licenses
"""
__docformat__ = "restructuredtext en"
_ = unicode

from cubicweb.predicates import relation_possible
from cubicweb.sobjects.notification import RecipientsFinder

class NosyListRecipientsFinder(RecipientsFinder):
    # action=None to by pass security checking
    __select__ = relation_possible('nosy_list', 'subject', action=None)

    def recipients(self):
        """Returns users in the nosy list for the entity"""
        entity = self.cw_rset.get_entity(self.cw_row or 0, self.cw_col or 0)
        rset = self._cw.execute(
            'Any U,E,A WHERE X nosy_list U, X eid %(e)s, U in_state S, '
            'S name "activated", U primary_email E, E address A',
            {'e': entity.eid},)
        return list(rset.entities()) # we don't want an iterator but a list
