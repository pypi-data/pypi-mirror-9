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

"""cubicweb-ckanpublish entity's classes"""

import re
import unicodedata
from urllib2 import urlopen

from cubicweb.predicates import relation_possible, adaptable, is_instance
from cubicweb.view import EntityAdapter

from cubes.ckanpublish.utils import ckan_post


def slugify(value):
    """Converts to lowercase, removes non-word characters (alphanumerics and
    underscores) and converts spaces to hyphens. Also strips leading and
    trailing whitespace.

    Adapted from django.utils.text and novaclient.utils.
    """
    if not isinstance(value, unicode):
        value = unicode(value)
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    value = unicode(re.sub('[^\w\s-]', '', value).strip().lower())
    return re.sub('[-\s]+', '-', value)


class CKANDatasetAdapter(EntityAdapter):
    """Adapter for entity that can be mapped to a CKAN dataset"""
    __regid__ = 'ICKANDataset'
    __abstract__ = True
    __select__ = (EntityAdapter.__select__ &
                  relation_possible('ckan_dataset_id', role='subject'))

    @property
    def ckan_name(self):
        """name field suitable for CKAN (must be unique, hence the eid prefix)
        """
        mainattr = self.entity.e_schema.main_attribute().type
        name = getattr(self.entity, mainattr)
        return str(self.entity.eid) + '-' + slugify(name).lower()

    def ckan_notes(self):
        """Build the CKAN dataset notes attribute

        This contains the entity description along with the list of related
        columns
        """
        if 'description' not in self.entity.e_schema.subject_relations():
            return
        # XXX CKAN uses Markdown syntax for notes field.
        return self.entity.printable_value('description', format='text/plain')

    def ckan_package_resources(self):
        """Return the list of resources URL for dataset"""
        data = {'id': self.entity.ckan_dataset_id}
        res = ckan_post(self._cw.vreg.config, 'package_show', data)
        if res:
            return [d['url'] for d in res['resources']]
        return []

    @property
    def ckan_organization(self):
        """The CKAN organization which should own the dataset"""
        return self._cw.vreg.config.get('ckan-organization')

    def ckan_get_organization_id(self, orgname):
        """Retrieve the ID of an organization given its name"""
        data = {'organizations': [orgname],
                'all_fields': True}
        res = ckan_post(self._cw.vreg.config, 'organization_list', data)
        if res:
            return res[0]['id']
        else:
            raise Exception('no organization named %s in CKAN instance' %
                            orgname)

    def dataset_title(self):
        """Title of the CKAN dataset"""
        return self.entity.dc_title()

    def ckan_data(self):
        """Return a dict with all data to build a CKAN dataset from entity"""
        data = {'name': self.ckan_name,
                'title': self.dataset_title(),
                'notes': self.ckan_notes(),
                'maintainer': None,
                'maintainer_email': None,
                'owner_org':self.ckan_get_organization_id(
                    self.ckan_organization)
               }
        maintainer, maintainer_email = self.dataset_maintainer()
        if maintainer:
            data['maintainer'] = maintainer
        if maintainer_email:
            data['maintainer_email'] = maintainer_email
        data['tags'] = list(self.dataset_tags())
        data['extras'] = list(self.dataset_extras())
        return data

    def dataset_extras(self):
        """Extra fields for the dataset"""
        return []

    def dataset_tags(self):
        """Yield tag data for entity"""
        if self.entity.e_schema.has_relation('tags', role='object'):
            for tag in self.entity.reverse_tags:
                yield {'name': slugify(tag.name)}

    def dataset_maintainer(self):
        """May return (name, email) information about the maintainer of
        dataset-like entity.
        """
        return None, None


class CKANResourceAdapter(EntityAdapter):
    """Adapter for entity that can be mapped to a CKAN resource"""
    __regid__ = 'ICKANResource'
    __abstract__ = True
    __select__ = (EntityAdapter.__select__ &
                  relation_possible('ckan_resource_id', role='subject'))

    @property
    def dataset(self):
        """The dataset-like entity (adaptable as ICKANDataset) associated with
        this resource.
        """
        raise NotImplementedError()

    def ckan_metadata(self):
        """Return a dict of metadata about the resource"""
        metadata = {
            'created': self.entity.creation_date.isoformat(),
            'last_modified': self.entity.modification_date.isoformat(),
        }
        return metadata

    def read(self):
        """Read resource content (file-like interface)."""
        raise NotImplementedError()


class DownloadableCKANResourceAdapter(CKANResourceAdapter):
    """Adapter for downloadable entities that can be mapped to a CKAN
    resource.
    """
    __abstract__ = True
    __select__ = CKANResourceAdapter.__select__ & adaptable('IDownloadable')

    def ckan_metadata(self):
        """Basic metadata extended with IDownloadable"""
        metadata = super(DownloadableCKANResourceAdapter, self).ckan_metadata()
        idownload = self.entity.cw_adapt_to('IDownloadable')
        metadata.update(
            {'name': idownload.download_file_name(),
             'mimetype': idownload.download_content_type(),
            }
        )
        return metadata

    def read(self):
        """Read content using IDownloadable adapter from URL."""
        idownload = self.entity.cw_adapt_to('IDownloadable')
        return urlopen(idownload.download_url())


class FileCKANResourceAdapter(DownloadableCKANResourceAdapter):
    """Adapter for File entities that can be mapped to a CKAN resource."""
    __abstract__ = True
    __select__ = (DownloadableCKANResourceAdapter.__select__ &
                  is_instance('File'))

    def read(self):
        """Read file content relying on File interface."""
        return self.entity
