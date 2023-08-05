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

from cubicweb import role
from cubicweb.predicates import adaptable, score_entity, PartialPredicateMixIn
from cubicweb.server import hook

from cubes.ckanpublish.sobjects import (delete_dataset,
                                        delete_dataset_resource,
                                        CKANSyncError)
from cubes.ckanpublish.utils import ckan_instance_configured



class DeleteCKANDataSetHook(hook.Hook):
    """Delete CKAN dataset upon deletion of the corresponding entity"""
    __regid__ = 'ckanpublish.delete-ckan-dataset'
    __select__ = (hook.Hook.__select__ & ckan_instance_configured() &
                  adaptable('ICKANDataset') &
                  score_entity(lambda x: x.ckan_dataset_id))
    events = ('before_delete_entity', )
    category = 'ckanpublish.dataset'

    def __call__(self):
        CKANDatasetOp.get_instance(self._cw).add_data(self.entity.eid)


class AddOrUpdateCKANDataSetHook(hook.Hook):
    """Add or update a CKAN dataset upon addition or update of an entity"""
    __regid__ = 'ckanpublish.add-update-ckan-dataset'
    __select__ = (hook.Hook.__select__ & ckan_instance_configured() &
                  adaptable('ICKANDataset'))
    events = ('after_add_entity', 'after_update_entity', )
    category = 'ckanpublish.dataset'

    def __call__(self):
        CKANDatasetOp.get_instance(self._cw).add_data(self.entity.eid)


class CKANDatasetOp(hook.DataOperationMixIn, hook.Operation):
    """Operation to create, update or delete a CKAN dataset"""

    def precommit_event(self):
        for eid in self.get_data():
            event = ('deletion' if self.cnx.deleted_in_transaction(eid)
                     else 'synchronization')
            try:
                if event == 'deletion':
                    datasetid = self.cnx.entity_from_eid(eid).ckan_dataset_id
                    delete_dataset(self.cnx.vreg.config, eid, datasetid)
                    self.info('deleted CKAN dataset %s', datasetid)
                else:
                    self.cnx.call_service('ckanpublish.sync_dataset', eid=eid)
            except CKANSyncError as exc:
                self.error('%s of CKAN dataset linked to entity #%d failed: %s',
                           event, eid, str(exc))
                if self.cnx.vreg.config.mode == 'test':
                    raise


class DeleteCKANResourceHook(hook.Hook):
    """Delete CKAN resource upon deletion of the corresponding entity"""
    __regid__ = 'ckanpublish.delete-ckan-resource'
    __select__ = (hook.Hook.__select__ & ckan_instance_configured() &
                  adaptable('ICKANResource') &
                  score_entity(lambda x: x.ckan_resource_id))
    category = 'ckanpublish.resource'
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
    __select__ = (hook.Hook.__select__ & ckan_instance_configured() &
                  partial_match_rtype())
    __abstract__ = True
    category = 'ckanpublish.resource'
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
    __select__ = (hook.Hook.__select__ & ckan_instance_configured() &
                  adaptable('ICKANResource'))
    category = 'ckanpublish.resource'
    events = ('after_update_entity', )

    def __call__(self):
        CKANResourceOp.get_instance(self._cw).add_data(self.entity.eid)


class CKANResourceOp(hook.DataOperationMixIn, hook.Operation):
    """Operation to create, update or delete a CKAN resource"""

    def precommit_event(self):
        for eid in self.get_data():
            resourceid = self.cnx.entity_from_eid(eid).ckan_resource_id
            event = ('deletion' if (self.cnx.deleted_in_transaction(eid)
                                    and resourceid is not None)
                     else 'synchronization')
            try:
                if event == 'deletion':
                    delete_dataset_resource(self.cnx.vreg.config, eid, resourceid)
                    self.info('deleted resource %s', resourceid)
                else:
                    self.cnx.call_service('ckanpublish.sync_resource', eid=eid)
            except CKANSyncError as exc:
                self.error('%s of CKAN resource linked to entity #%d failed: %s',
                           event, eid, str(exc))
                if self.cnx.vreg.config.mode == 'test':
                    raise
