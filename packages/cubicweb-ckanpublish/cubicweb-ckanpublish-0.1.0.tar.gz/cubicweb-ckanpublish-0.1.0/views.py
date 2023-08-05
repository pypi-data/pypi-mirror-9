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

from cubicweb.predicates import score_entity
from cubicweb.web import component

from cubes.ckanpublish.utils import ckan_post, ckan_buildurl


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
