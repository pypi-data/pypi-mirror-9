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

"""cubicweb-datacat schema"""

from yams.buildobjs import EntityType, RelationDefinition, String, RichString
from cubicweb.schema import (RRQLExpression, ERQLExpression,
                             WorkflowableEntityType, RQLConstraint,
                             RQLVocabularyConstraint)

from cubes.file.schema import File


_ = unicode


class Agent(EntityType):
    name = String(required=True, unique=True, fulltextindexed=True)
    email = String()
    description = _(
        'An agent (eg. person, group, software or physical artifact).')


class Dataset(EntityType):
    # DCAT attributes.
    identifier = String(required=True, fulltextindexed=True)
    title = String(fulltextindexed=True)
    description = RichString(fulltextindexed=True)
    theme = String(fulltextindexed=True, description=_('category of the Dataset'))
    keyword = String(fulltextindexed=True,
        description=_('keyword or tag describing the Dataset'))
    landing_page = String(
        description=_('a web page that provides access to the dataset, its '
                      'distributions and/or additional information.'))
    frequency = String(
        description=_('the frequency at which dataset is updated (e.g. weekly, '
                      'monthly)'))
    spatial_coverage = String(
        description=_('geographic region that is covered by the Dataset (e.g. '
                      'a city or a state)'))
    provenance = String(fulltextindexed=True)  # Not in DCAT-AP spec.


# DCAT relations and additional entity types.

class dataset_distribution(RelationDefinition):
    subject = 'Dataset'
    object = 'Distribution'
    cardinality = '?*'
    description = _('relate a Dataset to an available Distribution')


class dataset_contact_point(RelationDefinition):
    subject = 'Dataset'
    object = 'Agent'
    cardinality = '?*'
    description = _('contact information that can be used for flagging '
                    'errors in the Dataset or sending comments')


class dataset_publisher(RelationDefinition):
    subject = 'Dataset'
    object = 'Agent'
    cardinality = '?*'
    description = _('relate an entity (organization) responsible for making '
                    'the Dataset available')


class dataset_contributors(RelationDefinition):
    subject = 'Dataset'
    object = 'Agent'
    cardinality = '**'
    description = _('relate an entity (organization) responsible for making '
                    'contributions to the dataset')


class Distribution(EntityType):
    access_url = String(
        required=True,
        description=_('A URL that gives access to a Distribution of the '
                      'Dataset. The resource at the access URL may contain '
                      'information about how to get the Dataset.')
    )
    description = RichString(fulltextindexed=True)
    format = String(
        description=_('the file format of the Distribution'))
    licence = String(
        description=_('the licence under which the Distribution is made '
                      'available'))


class resource_of(RelationDefinition):
    __permissions__ = {
        'read': ('managers', 'users', 'guests'),
        'add': (RRQLExpression('U has_update_permission O'), ),
        'delete': (RRQLExpression('U has_update_permission O, '
                                  'NOT EXISTS(S produced_from R)'), ),
    }
    subject = 'File'
    object = 'Dataset'
    cardinality = '?*'
    inlined = True
    composite = 'object'
    constraints = [
        RQLVocabularyConstraint('NOT EXISTS(SC implemented_by S)'),
    ]


class ResourceFeed(EntityType):
    __permissions__ = {
        'read': ('managers', 'users', 'guests'),
        'update': (
            'managers',
            ERQLExpression('X resource_feed_of D, U has_update_permission D')),
        'delete': (
            'managers',
            ERQLExpression('X resource_feed_of D, U has_update_permission D')),
        'add': ('managers', 'users')
    }
    uri = String(required=True)
    data_format = String(
        required=True, maxsize=128, default='text/plain',
        description=_('MIME type of files served by the resource feed.'))
    __unique_toguether__ = [('uri', 'resource_feed_of')]


class resource_feed_of(RelationDefinition):
    __permissions__ = {
        'read': ('managers', 'users', 'guests'),
        'add': ('managers', RRQLExpression('U has_update_permission O')),
        'delete': ('managers', RRQLExpression('U has_update_permission O')),
    }
    subject = 'ResourceFeed'
    object = 'Dataset'
    cardinality = '1*'
    composite = 'object'
    inlined = True


class resource_feed_source(RelationDefinition):
    __permissions__ = {
        'read': ('managers', 'users', 'guests'),
        'add': (),
        'delete': (),
    }
    subject = 'ResourceFeed'
    object = 'CWSource'
    cardinality = '1*'
    inlined = True
    # TODO a constraint checking compatibility of data_format between resource
    # feeds sharing the same CWSource.


SCRIPT_UPDATE_PERMS_RQLEXPR = (
    'NOT EXISTS(P1 process_script X) OR '
    'EXISTS(P2 process_script X, P2 in_state S,'
    '       S name "wfs_dataprocess_initialized")')


class Script(EntityType):
    __permissions__ = {
        'read': ('managers', 'users', 'guests'),
        'update': ('managers', ERQLExpression(SCRIPT_UPDATE_PERMS_RQLEXPR)),
        'delete': ('managers', ERQLExpression(SCRIPT_UPDATE_PERMS_RQLEXPR)),
        'add': ('managers', 'users')
    }
    name = String(required=True, fulltextindexed=True)
    accepted_format = String(
        required=True, default='text/plain', maxsize=128,
        description=_('the MIME type of input files that this script accepts'),
    )


class implemented_by(RelationDefinition):
    __permissions__ = {
        'read': ('managers', 'users', 'guests'),
        'add': (RRQLExpression('U has_update_permission S'), ),
        'delete': (RRQLExpression('U has_update_permission S'), ),
    }
    subject = 'Script'
    object = 'File'
    cardinality = '1?'
    inlined = True
    composite = 'subject'
    description = _('the resource (file) implementing a script')
    constraints = [
        RQLVocabularyConstraint('NOT EXISTS(O resource_of D)'),
    ]


DATAPROCESS_UPDATE_PERMS_RQLEXPR = (
    'X in_state S, S name "wfs_dataprocess_initialized"')


class _DataProcess(WorkflowableEntityType):
    __abstract__ = True
    __permissions__ = {
        'read': ('managers', 'users', 'guests'),
        'update': ('managers',
                   ERQLExpression(DATAPROCESS_UPDATE_PERMS_RQLEXPR)),
        'delete': ('managers',
                   ERQLExpression(DATAPROCESS_UPDATE_PERMS_RQLEXPR)),
        'add': ('managers', 'users')
    }
    description = RichString(fulltextindexed=True)


class DataTransformationProcess(_DataProcess):
    """Data transformation process"""


class DataValidationProcess(_DataProcess):
    """Data validation process"""


class process_for_resourcefeed(RelationDefinition):
    __permissions__ = {
        'read': ('managers', 'users', 'guests'),
        'add': ('managers', RRQLExpression('U has_update_permission O')),
        'delete': ('managers', RRQLExpression('U has_update_permission O')),
    }
    subject = ('DataTransformationProcess', 'DataValidationProcess')
    object = 'ResourceFeed'
    cardinality = '?*'
    composite = 'object'


PROCESS_DEPENDS_ON_UPDATE_PERMS = (
    'managers', RRQLExpression(
        'NOT EXISTS(S process_for_resourcefeed RF1) '
        'OR (S process_for_resourcefeed RF, U has_update_permission RF)')
)


class process_depends_on(RelationDefinition):
    __permissions__ = {
        'read': ('managers', 'users', 'guests'),
        'add': PROCESS_DEPENDS_ON_UPDATE_PERMS,
        'delete': PROCESS_DEPENDS_ON_UPDATE_PERMS,
    }
    subject = 'DataTransformationProcess'
    object = 'DataValidationProcess'
    cardinality = '??'
    constraints = [
        RQLConstraint(
            'NOT EXISTS(S process_for_resourcefeed RF1,'
            '           S process_for_resourcefeed RF2) '
            'OR EXISTS(S process_for_resourcefeed RF,'
            '          O process_for_resourcefeed RF)',
            msg=_('dependency between data process must be within the same '
                  'resource feed')),
    ]


class process_input_file(RelationDefinition):
    __permissions__ = {
        'read': ('managers', 'users', 'guests'),
        'add': ('managers', RRQLExpression(
            'S in_state ST, ST name "wfs_dataprocess_initialized"')),
        'delete': ('managers', RRQLExpression('U has_update_permission S'))}
    subject = ('DataTransformationProcess', 'DataValidationProcess')
    object = 'File'
    cardinality = '?*'
    description = _('input file of the data process')
    constraints = [
        RQLConstraint('S process_script SC, SC accepted_format MT, '
                      'O data_format MT',
                      msg=_('the MIME type of input files must be accepted by '
                            'process script')),
    ]


class validated_by(RelationDefinition):
    """A File may be validated by a Script"""
    __permissions__ = {'read': ('managers', 'users', 'guests'),
                       'add': (),
                       'delete': ()}
    subject = 'File'
    object = 'Script'
    cardinality = '**'
    constraints = [
        RQLConstraint('EXISTS(P process_script O)',
                      msg=_('a script may validate a file only within a data '
                            'process execution')),
    ]


class produced_by(RelationDefinition):
    """A File may be produced by a Script"""
    __permissions__ = {'read': ('managers', 'users', 'guests'),
                       'add': (),
                       'delete': ()}
    subject = 'File'
    object = 'Script'
    cardinality = '?*'
    constraints = [
        RQLConstraint('EXISTS(P process_script O)',
                      msg=_('a script may produce a file only within a data '
                            'process execution')),
    ]


class produced_from(RelationDefinition):
    """A File may be produced by another File"""
    __permissions__ = {'read': ('managers', 'users', 'guests'),
                       'add': (),
                       'delete': ()}
    subject = 'File'
    object = 'File'
    cardinality = '?*'


# Set File permissions:
#  * use `produced_from` relation to prevent modification of generated files
#  * use relative permissions on the Dataset which the file may be a resource
#    of
#  * bind the update permissions on the Script which uses the File as
#    implementation if any
for action in ('update', 'delete'):
    File.set_action_permissions(
        action, ('managers', ERQLExpression(
            'NOT EXISTS(X produced_from Y), '
            'NOT EXISTS(X resource_of D1)'
            ' OR EXISTS(X resource_of D, U has_update_permission D), '
            'NOT EXISTS(S1 implemented_by X)'
            ' OR EXISTS(S implemented_by X, U has_update_permission S)')
        )
    )


class process_script(RelationDefinition):
    __permissions__ = {
        'read': ('managers', 'users', 'guests'),
        'add': ('managers', 'users'),
        'delete': (RRQLExpression('U has_update_permission S'), )
    }
    subject = ('DataTransformationProcess', 'DataValidationProcess')
    object = 'Script'
    cardinality = '1*'
    inlined = True


class _resourcefeed_script(RelationDefinition):
    __abstract__ = True
    __permissions__ = {
        'read': ('managers', 'users', 'guests'),
        'add': ('managers', 'users'),
        'delete': (RRQLExpression('U has_update_permission S'), )
    }
    subject = 'ResourceFeed'
    object = 'Script'
    cardinality = '?*'
    inlined = True


class validation_script(_resourcefeed_script):
    description = u'a Script used to validated files from this resource'


class transformation_script(_resourcefeed_script):
    description = u'a Script used to transform files from this resource'
