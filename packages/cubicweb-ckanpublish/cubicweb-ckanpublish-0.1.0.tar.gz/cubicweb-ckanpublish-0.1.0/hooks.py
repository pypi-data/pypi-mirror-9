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

"""cubicweb-ckanpublish specific hooks and operations"""

from requests.exceptions import RequestException

from cubicweb import ValidationError, role
from cubicweb.predicates import adaptable, score_entity, PartialPredicateMixIn
from cubicweb.server import hook

from cubes.ckanpublish.utils import (ckan_post, CKANPostError,
                                     ckan_instance_configured)


def _ckan_action(config, eid, action, **kwargs):
    """Run `ckan_post` and eventually raise ValidationError."""
    try:
        return ckan_post(config, action, **kwargs)
    except (CKANPostError, RequestException) as exc:
        raise ValidationError(eid, {'ckan_dataset_id': unicode(exc)})


def create_dataset(config, eid, data):
    """Create a CKAN dataset and set `ckan_dataset_id` attribute or
    respective entity. Return the dataset id.
    """
    res = _ckan_action(config, eid, 'package_create', data=data)
    return res['id']


def update_dataset(config, eid, datasetid, udata):
    """Update an existing CKAN dataset"""
    data = _ckan_action(config, eid, 'package_show', data={'id': datasetid})
    data.update(udata)
    _ckan_action(config, eid, 'package_update', data=data)


def delete_dataset(config, eid, datasetid):
    """Delete a CKAN dataset"""
    _ckan_action(config, eid, 'package_delete', data={'id': datasetid})


def create_dataset_resource(config, eid, datasetid, metadata, data):
    """Add a resource to an existing CKAN dataset"""
    metadata['package_id'] = datasetid
    res = _ckan_action(config, eid, 'resource_create', data=metadata,
                       files=[('upload', data)])
    return res['id']


def update_dataset_resource(config, eid, resourceid, metadata, data):
    """Update an existing CKAN resource."""
    metadata['id'] = resourceid
    _ckan_action(config, eid, 'resource_update', data=metadata,
                 files=[('upload', data)])


def delete_dataset_resource(config, eid, resourceid):
    """Delete a CKAN resource"""
    _ckan_action(config, eid, 'resource_delete', data={'id': resourceid})


class DeleteCKANDataSetHook(hook.Hook):
    """Delete CKAN dataset upon deletion of the corresponding entity"""
    __regid__ = 'ckanpublish.delete-ckan-dataset'
    __select__ = (hook.Hook.__select__ & ckan_instance_configured &
                  adaptable('ICKANDataset') &
                  score_entity(lambda x: x.ckan_dataset_id))
    events = ('before_delete_entity', )

    def __call__(self):
        CKANDatasetOp.get_instance(self._cw).add_data(self.entity.eid)


class AddOrUpdateCKANDataSetHook(hook.Hook):
    """Add or update a CKAN dataset upon addition or update of an entity"""
    __regid__ = 'ckanpublish.add-update-ckan-dataset'
    __select__ = (hook.Hook.__select__ & ckan_instance_configured &
                  adaptable('ICKANDataset'))
    events = ('after_add_entity', 'after_update_entity', )

    def __call__(self):
        CKANDatasetOp.get_instance(self._cw).add_data(self.entity.eid)


class CKANDatasetOp(hook.DataOperationMixIn, hook.Operation):
    """Operation to create, update or delete a CKAN dataset"""

    def precommit_event(self):
        for eid in self.get_data():
            entity = self.cnx.entity_from_eid(eid)
            datasetid = entity.ckan_dataset_id
            config = self.cnx.vreg.config
            if self.cnx.deleted_in_transaction(eid):
                delete_dataset(config, eid, datasetid)
                self.info('deleted CKAN dataset %s', datasetid)
            else:
                cpublish = entity.cw_adapt_to('ICKANDataset')
                data = cpublish.ckan_data()
                if datasetid is not None:
                    update_dataset(config, eid, datasetid, data)
                    self.info('updated %s fields in CKAN dataset %s',
                              data.keys(), datasetid)
                else:
                    datasetid = create_dataset(config, eid, data)
                    self.cnx.execute(
                        'SET X ckan_dataset_id %(dsid)s WHERE X eid %(eid)s',
                        {'eid': eid, 'dsid': datasetid})
                    self.info('created CKAN dataset %s', datasetid)


class DeleteCKANResourceHook(hook.Hook):
    """Delete CKAN resource upon deletion of the corresponding entity"""
    __regid__ = 'ckanpublish.delete-ckan-resource'
    __select__ = (hook.Hook.__select__ & ckan_instance_configured &
                  adaptable('ICKANResource') &
                  score_entity(lambda x: x.ckan_resource_id))
    events = ('before_delete_entity', )

    def __call__(self):
        CKANResourceOp.get_instance(self._cw).add_data(self.entity.eid)


class partial_match_rtype(PartialPredicateMixIn, hook.match_rtype):
    """Same as :class:~`cubicweb.server.hook.match_rtype`, but will look for
    attributes `rtype`, `role`, `frometypes` and `toetypes` on the selected
    class to get information which is otherwise expected by the initializer.
    """
    def __init__(self, *expected, **more):
        super(partial_match_rtype, self).__init__()

    def complete(self, cls):
        self.expected = (cls.rtype, )
        self.role = role(cls)
        self.frometypes = getattr(cls, 'frometypes', None)
        self.toetypes = getattr(cls, 'toetypes', None)


class LinkResourceToDatasetHook(hook.Hook):
    """Create a CKAN resource upon link of a resource-like entity to a
    dataset-like entity.

    Actual implementations should at least fill the `rtype` attribute.
    """
    __regid__ = 'ckanpublish.link-ckan-resource-to-ckan-dataset'
    __select__ = (hook.Hook.__select__ & ckan_instance_configured &
                  partial_match_rtype())
    __abstract__ = True
    events = ('after_add_relation', )
    rtype = None  # Use to fill the `expected` argument of match_rtype.
    role  = 'object'
    frometypes = None
    toetypes = None

    def __call__(self):
        eid = {'subject': self.eidfrom, 'object': self.eidto}[self.role]
        CKANResourceOp.get_instance(self._cw).add_data(eid)


class UpdateCKANResourceHook(hook.Hook):
    """Update a CKAN resource upon update of an resource-like entity"""
    __regid__ = 'ckanpublish.update-ckan-resource'
    __select__ = (hook.Hook.__select__ & ckan_instance_configured &
                  adaptable('ICKANResource'))
    events = ('after_update_entity', )

    def __call__(self):
        CKANResourceOp.get_instance(self._cw).add_data(self.entity.eid)


class CKANResourceOp(hook.DataOperationMixIn, hook.Operation):
    """Operation to create, update or delete a CKAN resource"""

    def precommit_event(self):
        for eid in self.get_data():
            entity = self.cnx.entity_from_eid(eid)
            resourceid = entity.ckan_resource_id
            iresource = entity.cw_adapt_to('ICKANResource')
            config = self.cnx.vreg.config
            if self.cnx.deleted_in_transaction(eid) and resourceid is not None:
                delete_dataset_resource(config, eid, resourceid)
                self.info('deleted resource %s', resourceid)
            else:
                metadata = iresource.ckan_metadata()
                data = iresource.read()
                if resourceid is None:
                    dataset = iresource.dataset
                    assert dataset, 'no dataset for resource #%d' % eid
                    if not dataset.ckan_dataset_id:
                        self.error('skipping resource #%d as its dataset %#d is '
                                   'not in the CKAN instance', eid, dataset.eid)
                        continue
                    resourceid = create_dataset_resource(
                        config, eid, dataset.ckan_dataset_id, metadata, data)
                    self.cnx.execute(
                        'SET X ckan_resource_id %(rid)s WHERE X eid %(eid)s',
                        {'eid': eid, 'rid': resourceid})
                    self.info('added resource %s', resourceid)
                else:
                    update_dataset_resource(
                        config, eid, resourceid, metadata, data)
                    self.info('updated resource %s', resourceid)
