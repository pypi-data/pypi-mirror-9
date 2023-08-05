# copyright 2013 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.
"""cubicweb-ctl plugin providing the check-nosylist command"""

__docformat__ = "restructuredtext en"

import os

from cubicweb.toolsutils import Command
from cubicweb.cwctl import CWCTL
try:
    from cubicweb.devtools.instrument import PropagationAnalyzer, warn
    register_command = True
except ImportError:
    # either devtools (development package) or instrument (insufficient
    # version) is uninstalled, skip the command
    register_command = False
else:

    class NosyListPropagationAnalyzer(PropagationAnalyzer):
        prop_rel = 'nosy_list'
        def is_root(self, eschema):
            return 'interested_in' in eschema.objrels


class CheckNosyListCommand(Command):
    """Analyse nosylist configuration.

    It will load the given cube schema and hooks, analyze nosy list propagation
    rules to print on the standart output warnings about detected problems.
    """
    name = 'check-nosylist'
    arguments = '<cube>'
    min_args = max_args = 1
    options = (
        ('graph',
         {'short': 'g', 'type': 'string', 'metavar': '<file>',
          'default': None,
          'help': 'draw propagation graph in the given file. Require pygraphviz installed',
          }),
        )

    def run(self, args):
        """run the command with its specific arguments"""
        cube = args[0]
        # instrumentalize cube's hooks S_RELS / O_RELS (has to be done before
        # vreg init)
        os.environ['NOSYLIST_INSTRUMENT'] = '1'
        # get config, schema and vreg
        analyzer = NosyListPropagationAnalyzer()
        vreg, eschemas = analyzer.init(cube)
        if not eschemas:
            warn('nothing to analyze')
            return
        # get propagation rules
        from cubes.nosylist.hooks import S_RELS, O_RELS # local import necessary
        edges = analyzer.prop_edges(S_RELS, O_RELS, eschemas)
        # detect pbs
        problematic = analyzer.detect_problems(eschemas, edges)
        # build graph if asked
        if self.config.graph:
            graph = analyzer.init_graph(eschemas, edges, problematic)
            analyzer.add_colors_legend(graph)
            graph.layout(prog='dot')
            graph.draw(self.config.graph)

if register_command:
    CWCTL.register(CheckNosyListCommand)
