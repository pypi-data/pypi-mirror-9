# copyright 2014 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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
"""cubicweb-datacat workflows"""

_ = unicode


def define_dataprocess_workflow(add_workflow):
    """Define workflow for data process entity types"""
    etypes = 'DataTransformationProcess', 'DataValidationProcess'
    wf = add_workflow(u'Data processing workflow', etypes)
    # States
    initialized = wf.add_state(_('wfs_dataprocess_initialized'), initial=True)
    in_progress = wf.add_state(_('wfs_dataprocess_in_progress'))
    error = wf.add_state(_('wfs_dataprocess_error'))
    completed = wf.add_state(_('wfs_dataprocess_completed'))
    # Transitions
    wf.add_transition(_('wft_dataprocess_start'),
                      (initialized, ), in_progress,
                      requiredgroups=('managers', 'users'))
    wf.add_transition(_('wft_dataprocess_error'),
                      (in_progress, ), error,
                      requiredgroups=())
    wf.add_transition(_('wft_dataprocess_complete'),
                      (in_progress, ), completed,
                      requiredgroups=())
    return wf
