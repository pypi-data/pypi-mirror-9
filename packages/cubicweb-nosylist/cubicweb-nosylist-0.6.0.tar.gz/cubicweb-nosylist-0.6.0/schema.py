"""schema for nosy list handling

:organization: Logilab
:copyright: 2001-2010 LOGILAB S.A. (Paris, FRANCE), license is LGPL v2.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
:license: GNU Lesser General Public License, v2.1 - http://www.gnu.org/licenses
"""

from yams.buildobjs import RelationType
from cubicweb.schema import RRQLExpression

class interested_in(RelationType):
    """relation to explicitly note interest about something"""
    __permissions__ = {
        'read':   ('managers', 'users'),
        'add':    ('managers', RRQLExpression('U has_update_permission S', 'S'),),
        'delete': ('managers', RRQLExpression('U has_update_permission S', 'S'),),
        }
    subject = 'CWUser'

class nosy_list(RelationType):
    """relation handled internaly to control who will be notified"""
    __permissions__ = {
        'read':   ('managers', 'users'),
        'add':    ('managers',),
        # we need to delete it from the ui (for instance to unregister from a
        # ticket when user is interested in a project)
        'delete': ('managers', RRQLExpression('U has_update_permission O', 'O')),
        }
    object = 'CWUser'
