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

"""cubicweb-datacat specific hooks and operations"""

import os

from cubicweb import ValidationError
from cubicweb.predicates import (on_fire_transition, score_entity,
                                 is_instance, objectify_predicate, adaptable,
                                 has_related_entities)
from cubicweb.server import hook
from cubicweb.server.sources import storages


class ServerStartupHook(hook.Hook):
    __regid__ = 'datacat.serverstartup'
    events = ('server_startup', 'server_maintenance')

    def __call__(self):
        bfssdir = os.path.join(self.repo.config.appdatahome, 'bfss')
        if not os.path.exists(bfssdir):
            os.makedirs(bfssdir)
            print 'created', bfssdir
        storage = storages.BytesFileSystemStorage(bfssdir)
        storages.set_attribute_storage(self.repo, 'File', 'data', storage)


@objectify_predicate
def process_missing_dependency(cls, req, rset=None, eidfrom=None,
                               eidto=None, **kwargs):
    """Return 1 if the process has a dependency"""
    if not eidfrom:
        return 0
    if req.entity_metas(eidfrom)['type'] != 'DataTransformationProcess':
        return 0
    if req.execute('Any X WHERE EXISTS(X process_depends_on Y),'
                   '            X eid %(eid)s', {'eid': eidfrom}):
        return 1
    return 0


class AutoStartDataProcessHook(hook.Hook):
    """Automatically starts a data process when an input file is added."""
    __regid__ = 'datacat.dataprocess-start-when-inputfile-added'
    __select__ = (hook.Hook.__select__ &
                  hook.match_rtype('process_input_file') &
                  ~process_missing_dependency())

    events = ('after_add_relation', )
    category = 'workflow'

    def __call__(self):
        StartDataProcessOp.get_instance(self._cw).add_data(self.eidfrom)


def trinfo_concerns_a_dependency_process(trinfo):
    """Return 1 if the TrInfo concerns a data process which is a dependency of
    another.
    """
    process = trinfo.for_entity
    if process.cw_etype != 'DataValidationProcess':
        return 0
    return 1 if process.reverse_process_depends_on else 0


class StartDataProcessWithDependencyHook(hook.Hook):
    """Starts a data process when its dependency terminated successfully."""
    __regid__ = 'datacat.dataprocess-start-when-dependency-terminated'
    __select__ = (hook.Hook.__select__ &
                  on_fire_transition('DataValidationProcess',
                                     'wft_dataprocess_complete') &
                  score_entity(trinfo_concerns_a_dependency_process))

    events = ('after_add_entity', )
    category = 'workflow'

    def __call__(self):
        vprocess = self.entity.for_entity
        tprocess = vprocess.reverse_process_depends_on[0]
        StartDataProcessOp.get_instance(self._cw).add_data(tprocess.eid)


class StartDataProcessOp(hook.DataOperationMixIn, hook.LateOperation):
    """Trigger "start" transition for a data process.

    Use a LateOperation to ensure the workflow transition is fired after
    entity has a state.
    """

    def precommit_event(self):
        for eid in self.get_data():
            process = self.cnx.entity_from_eid(eid)
            iprocess = process.cw_adapt_to('IDataProcess')
            iprocess.fire_workflow_transition('start')


class StartDataProcessHook(hook.Hook):
    __regid__ = 'datacat.dataprocess-start'
    __select__ = (hook.Hook.__select__ &
                  (on_fire_transition('DataTransformationProcess',
                                      'wft_dataprocess_start') |
                   on_fire_transition('DataValidationProcess',
                                      'wft_dataprocess_start')))

    events = ('after_add_entity', )
    category = 'workflow'

    def __call__(self):
        process = self.entity.for_entity
        AddScriptExecutionOp.get_instance(self._cw).add_data(process.eid)


class AddScriptExecutionOp(hook.DataOperationMixIn, hook.Operation):
    """Run a subprocess for each input file of the data process using its
    script.
    """

    def precommit_event(self):
        for peid in self.get_data():
            process = self.cnx.entity_from_eid(peid)
            iprocess = process.cw_adapt_to('IDataProcess')
            if not process.process_input_file:
                msg = u'no input file'
            else:
                msg = u'all input files processed'
                inputfile = process.process_input_file[0]
                returncode, stderr = iprocess.execute_script(inputfile)
                if returncode:
                    msg = u'\n'.join(
                        ['error transforming input file #%d' % inputfile.eid,
                         'subprocess exited with status %d' % returncode,
                         'stderr: %s' % stderr])
                    iprocess.fire_workflow_transition('error', comment=msg)
                    return
            iprocess.fire_workflow_transition('complete', comment=msg)


class SetValidatedByHook(hook.Hook):
    """Set the `validated_by` relation update completion of the data
    validation process.
    """
    __regid__ = 'datacat.datavalidationprocess-completed-inputfile-validated_by'
    __select__ = (hook.Hook.__select__ &
                  on_fire_transition('DataValidationProcess',
                                     'wft_dataprocess_complete'))

    events = ('after_add_entity', )
    category = 'workflow'

    def __call__(self):
        process = self.entity.for_entity
        self._cw.execute(
            'SET F validated_by S WHERE F eid %(input)s, S eid %(script)s,'
            '                           NOT F validated_by S',
            {'script': process.process_script[0].eid,
             'input': process.process_input_file[0].eid})


class LinkFeedResourceToDataset(hook.Hook):
    """Add the `resources` relation to files produced by a transformation
    script when the latter is attached to a ResourceFeed (which is in turns
    related to a Dataset).
    """
    __regid__ = 'datacat.link-feedresource-to-dataset'
    __select__ = hook.Hook.__select__ & hook.match_rtype('produced_by')
    events = ('after_add_relation', )

    def __call__(self):
        # TODO: Would be nice to build a selector for this.
        rset = self._cw.execute(
            'Any R,D WHERE EXISTS(R transformation_script SC,'
            '                     R resource_feed_of D),'
            '              NOT EXISTS(F resource_of D),'
            '              SC eid %(eid)s, F eid %(feid)s',
            {'eid': self.eidto, 'feid': self.eidfrom})
        if rset:
            self._cw.execute(
                'SET F resource_of D WHERE D eid %(d)s, F eid %(f)s',
                {'d': rset[0][1], 'f': self.eidfrom})


class AddCWSourceForResourceFeedHook(hook.Hook):
    """Add a CWSource for ResourceFeed entities."""
    __regid__ = 'datacat.add_cwsource_for_resourcefeed'
    __select__ = hook.Hook.__select__ & is_instance('ResourceFeed')
    events = ('after_add_entity', )

    def __call__(self):
        uri = self.entity.cw_edited['uri'].strip()
        rset = self._cw.find('CWSource', name=uri, url=uri)
        if rset:
            source = rset.one()
        else:
            source = self._cw.create_entity(
                'CWSource', name=uri, url=uri, type=u'datafeed',
                config=u'use-cwuri-as-url=no',
                parser=u'datacat.resourcefeed-parser')
        self.entity.cw_set(resource_feed_source=source.eid)


class UpdateCWSourceForResourceFeedHook(hook.Hook):
    """Update ResourceFeed's CWSource when its uri changes."""
    __regid__ = 'datacat.update_resourcefeed_cwsource'
    __select__ = hook.Hook.__select__ & is_instance('ResourceFeed')
    events = ('after_update_entity', )

    def __call__(self):
        if 'uri' in self.entity.cw_edited:
            uri = self.entity.cw_edited['uri']
            source = self.entity.resource_feed_source[0]
            source.cw_set(url=uri, name=uri)
