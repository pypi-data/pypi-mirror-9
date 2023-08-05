# copyright 2015 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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

"""cubicweb-ckanpublish server objects"""

from requests.exceptions import RequestException

from cubicweb.server import Service
from cubicweb.predicates import adaptable

from cubes.ckanpublish.utils import (ckan_instance_configured, ckan_post,
                                     CKANPostError)

class CKANSyncError(Exception):
    """Error during synchronization to CKAN instance"""


def _ckan_action(config, eid, action, **kwargs):
    """Run `ckan_post` and eventually raise CKANSyncError."""
    try:
        return ckan_post(config, action, **kwargs)
    except (CKANPostError, RequestException) as exc:
        raise CKANSyncError(str(exc))


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


class SyncCKANDataset(Service):
    """Service for synchronization of a "dataset-like" entity to a CKAN
    instance.
    """
    __regid__ = 'ckanpublish.sync_dataset'
    __select__ = ckan_instance_configured()

    def call(self, eid, **kwargs):
        """Create or update a CKAN dataset using dataset-like entity eid"""
        entity = self._cw.entity_from_eid(eid)
        datasetid = entity.ckan_dataset_id
        data = entity.cw_adapt_to('ICKANDataset').ckan_data()
        config = self._cw.vreg.config
        if datasetid is not None:
            update_dataset(config, eid, datasetid, data)
            self.info('updated %s fields in CKAN dataset %s',
                      data.keys(), datasetid)
        else:
            datasetid = create_dataset(config, eid, data)
            with self._cw.allow_all_hooks_but('ckanpublish.dataset'):
                self._cw.execute(
                    'SET X ckan_dataset_id %(dsid)s WHERE X eid %(eid)s',
                    {'eid': eid, 'dsid': datasetid})
            self.info('created CKAN dataset %s', datasetid)


class SyncCKANResource(Service):
    """Service for synchronization of a "resource-like" entity to a CKAN
    instance.
    """
    __regid__ = 'ckanpublish.sync_resource'
    __select__ = ckan_instance_configured()

    def call(self, eid, **kwargs):
        """Create or update a CKAN resource using resource-like entity eid"""
        entity = self._cw.entity_from_eid(eid)
        resourceid = entity.ckan_resource_id
        iresource = entity.cw_adapt_to('ICKANResource')
        config = self._cw.vreg.config
        metadata = iresource.ckan_metadata()
        data = iresource.read()
        if resourceid is None:
            dataset = iresource.dataset
            assert dataset, 'no dataset for resource #%d' % eid
            if not dataset.ckan_dataset_id:
                self.error('skipping resource #%d as its dataset %#d is '
                           'not in the CKAN instance', eid, dataset.eid)
                return
            resourceid = create_dataset_resource(
                config, eid, dataset.ckan_dataset_id, metadata, data)
            with self._cw.allow_all_hooks_but('ckanpublish.resource'):
                self._cw.execute(
                    'SET X ckan_resource_id %(rid)s WHERE X eid %(eid)s',
                    {'eid': eid, 'rid': resourceid})
            self.info('added resource %s', resourceid)
        else:
            update_dataset_resource(
                config, eid, resourceid, metadata, data)
            self.info('updated resource %s', resourceid)
