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

"""cubicweb-ckanpublish views/forms/actions/components for web ui"""

from logilab.mtconverter import xml_escape

from cubicweb.predicates import score_entity, adaptable
from cubicweb.web import component, action, Redirect
from cubicweb.view import EntityView

from cubes.ckanpublish.sobjects import CKANSyncError
from cubes.ckanpublish.utils import (ckan_post, ckan_buildurl,
                                     ckan_instance_configured, CKANPostError)


_ = unicode


class GotoCKANDatasetComponent(component.EntityCtxComponent):
    """Contextual component displaying a link to the CKAN dataset in
    Dataset-like entities primary view.
    """
    __regid__ = 'ckanpublish.goto-ckan-dataset'
    __select__ = (component.EntityCtxComponent.__select__ &
                  score_entity(lambda x: getattr(x, 'ckan_dataset_id', False)))
    title = _('CKAN dataset')
    context = 'incontext'

    _ckan_response = None

    def init_rendering(self):
        super(GotoCKANDatasetComponent, self).init_rendering()
        config = self._cw.vreg.config
        entity = self._cw.entity_from_eid(self.cw_rset[0][0])
        try:
            r = ckan_post(config, 'package_show',
                          {'id': entity.ckan_dataset_id})
        except Exception as exc:
            self._cw.warning('fail to post to CKAN instance: %s', exc)
            raise component.EmptyComponent()
        self._ckan_response = r

    def render_body(self, w):
        r = self._ckan_response
        url = ckan_buildurl(self._cw.vreg.config,
                            'dataset/' + xml_escape(r['name']))
        w(u'<a target=_blank href="%s">%s</a>' % (url, xml_escape(url)))


class SyncDatasetToCKANMixin(object):
    """Mixin for dataset-like entity synchronization to CKAN instance."""
    __regid__ = 'ckanpublish.sync_dataset_to_ckan'
    __select__ = adaptable('ICKANDataset') & ckan_instance_configured()


class SyncDatasetToCKANAction(SyncDatasetToCKANMixin, action.Action):
    """Trigger synchronization of a dataset-like entity to the CKAN instance.
    """
    title = _('synchronize to CKAN')

    def url(self):
        entity = self.cw_rset.get_entity(self.cw_row or 0, self.cw_col or 0)
        return entity.absolute_url(vid=self.__regid__)


class SyncDatasetToCKANView(SyncDatasetToCKANMixin, EntityView):
    """Handle synchronization of a dataset-like entity to the CKAN instance.
    """

    def entity_call(self, entity):
        try:
            self._cw.call_service('ckanpublish.sync_dataset', eid=entity.eid)
        except (CKANSyncError, CKANPostError) as exc:
            msg = self._cw._('synchronization to CKAN failed: ' + str(exc))
        else:
            msg = self._cw._('synchronization to CKAN successfully completed')
        raise Redirect(entity.absolute_url(__message=msg))


class SyncResourceToCKANMixin(object):
    """Mixin for dataset resource-like entity synchronization to CKAN
    instance.
    """
    __regid__ = 'ckanpublish.sync_dataset_resource_to_ckan'
    __select__ = adaptable('ICKANResource') & ckan_instance_configured()


class SyncResourceToCKANAction(SyncResourceToCKANMixin, action.Action):
    """Trigger synchronization of a dataset resource-like entity to the CKAN
    instance.
    """
    title = _('synchronize to CKAN')

    def url(self):
        entity = self.cw_rset.get_entity(self.cw_row or 0, self.cw_col or 0)
        return entity.absolute_url(vid=self.__regid__)


class SyncResourceToCKANView(SyncResourceToCKANMixin, EntityView):
    """Handle synchronization of dataset resource-like entity to the CKAN
    instance.
    """

    def entity_call(self, entity):
        try:
            self._cw.call_service('ckanpublish.sync_resource', eid=entity.eid)
        except (CKANSyncError, CKANPostError) as exc:
            msg = self._cw._('synchronization to CKAN failed: ' + str(exc))
        else:
            msg = self._cw._('synchronization to CKAN successfully completed')
        raise Redirect(entity.absolute_url(__message=msg))
