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

"""cubicweb-datacat views/forms/actions/components for web ui"""

from cubicweb.predicates import adaptable, has_related_entities, is_instance
from cubicweb.web import component
from cubicweb.web.views import uicfg, ibreadcrumbs

from cubes.datacat.entities import process_type_from_etype


abaa = uicfg.actionbox_appearsin_addmenu
afs = uicfg.autoform_section
affk = uicfg.autoform_field_kwargs
pvds = uicfg.primaryview_display_ctrl
pvs = uicfg.primaryview_section

# File
pvs.tag_subject_of(('File', 'resource_of', '*'), 'attributes')
afs.tag_subject_of(('File', 'resource_of', '*'), 'main', 'hidden')
afs.tag_object_of(('*', 'process_input_file', 'File'), 'main', 'hidden')


class ScriptImplementationBreadCrumbsAdapter(ibreadcrumbs.IBreadCrumbsAdapter):
    """Define Script / <Implementation> breadcrumbs"""
    __select__ = (ibreadcrumbs.IBreadCrumbsAdapter.__select__ &
                  has_related_entities('implemented_by', role='object') &
                  # Prevent select ambiguity ad File can be object of both
                  # `implemented_by` and `resources` relations.
                  ~has_related_entities('resource_of', role='subject'))

    def parent_entity(self):
        """The Script"""
        return self.entity.reverse_implemented_by[0]


# Dataset
pvs.tag_object_of(('*', 'resource_of', 'Dataset'), 'hidden')
afs.tag_subject_of(('Dataset', 'dataset_publisher', '*'), 'main', 'inlined')
afs.tag_subject_of(('Dataset', 'dataset_distribution', '*'), 'main', 'inlined')
afs.tag_subject_of(('Dataset', 'dataset_contact_point', '*'), 'main', 'inlined')


class ResourceBreadCrumbsAdapter(ibreadcrumbs.IBreadCrumbsAdapter):
    """Define Dataset / <Resource> breadcrumbs"""
    __select__ = (ibreadcrumbs.IBreadCrumbsAdapter.__select__ &
                  has_related_entities('resource_of', role='subject'))

    def parent_entity(self):
        """The Dataset"""
        return self.entity.resource_of[0]


class ResourcesCtxComponent(component.EntityCtxComponent):
    """Display resource files in Dataset primary view"""
    __regid__ = 'datacat.dataset-resources'
    __select__ = (component.EntityCtxComponent.__select__ &
                  is_instance('Dataset') &
                  has_related_entities('resource_of', role='object'))
    title = _('Resources')
    context = 'navcontentbottom'

    def render_body(self, w):
        rset = self._cw.execute(
            'Any F,O,S,CD WHERE F resource_of X, F produced_by S?, '
            'F produced_from O?, F creation_date CD, X eid %(eid)s',
            {'eid': self.entity.eid})
        w(self._cw.view('table', rset=rset))


# ResourceFeed
for rtype in ('transformation_script', 'validation_script'):
    pvs.tag_subject_of(('ResourceFeed', rtype, '*'), 'attributes')
pvs.tag_object_of(('*', 'process_for_resourcefeed', 'ResourceFeed'), 'hidden')
afs.tag_subject_of(('ResourceFeed', 'resource_feed_source', '*'),
                   'main', 'hidden')
for rtype in ('transformation_script', 'validation_script'):
    afs.tag_subject_of(('ResourceFeed', rtype, '*'),
                       'main', 'attributes')
    abaa.tag_subject_of(('ResourceFeed', rtype, '*'), True)
abaa.tag_object_of(('*', 'process_for_resourcefeed', 'ResourceFeed'), False)


class ResourceFeedBreadCrumbsAdapter(ibreadcrumbs.IBreadCrumbsAdapter):
    """Define Dataset / ResourceFeed breadcrumbs"""
    __select__ = (ibreadcrumbs.IBreadCrumbsAdapter.__select__ &
                  has_related_entities('resource_feed_of', role='subject'))

    def parent_entity(self):
        """The Dataset"""
        return self.entity.resource_feed_of[0]


class DataProcessInResourceFeedCtxComponent(component.EntityCtxComponent):
    """Display data processes in ResourceFeed primary view"""
    __regid__ = 'datacat.resourcefeed-dataprocess'
    __select__ = (component.EntityCtxComponent.__select__ &
                  is_instance('ResourceFeed') &
                  has_related_entities('process_for_resourcefeed',
                                       role='object'))
    title = _('Data processes')
    context = 'navcontentbottom'

    def render_body(self, w):
        rset = self._cw.execute(
            'Any P,I,S,D WHERE P process_for_resourcefeed X,'
            '                  P process_input_file I,'
            '                  P in_state ST, ST name S,'
            '                  D? process_depends_on P,'
            '                  X eid %(eid)s',
            {'eid': self.entity.eid})
        if rset:
            w(self._cw.view('table', rset=rset))
        rset = self._cw.execute(
            'Any P,I,S,D WHERE P process_for_resourcefeed X,'
            '                  P process_input_file I,'
            '                  P in_state ST, ST name S,'
            '                  P process_depends_on D?,'
            '                  X eid %(eid)s',
            {'eid': self.entity.eid})
        if rset:
            w(self._cw.view('table', rset=rset))


# Script
afs.tag_object_of(('*', 'process_script', 'Script'),
                   'main', 'hidden')
afs.tag_subject_of(('Script', 'implemented_by', '*'), 'main', 'inlined')
pvs.tag_attribute(('Script', 'name'), 'hidden')


# DataTransformationProcess, DataValidationProcess
for etype in ('DataTransformationProcess', 'DataValidationProcess'):
    afs.tag_subject_of((etype, 'process_input_file', '*'),
                       'main', 'attributes')
    pvs.tag_subject_of((etype, 'process_input_file', '*'), 'attributes')
    affk.set_fields_order(etype, ('name', 'description',
                                  ('process_input_file', 'subject')))
