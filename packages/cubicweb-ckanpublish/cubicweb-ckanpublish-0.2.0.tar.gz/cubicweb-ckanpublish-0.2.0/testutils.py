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

"""cubicweb-ckanpublish test utilities"""


class CKANPublishTestMixin(object):
    """Test case mixin to handle CKAN instance configuration, setup and
    teardown.

    Relies on the presence of a `ckanconfig.py` module in test directory.
    """
    dataset_owner_org = None

    @classmethod
    def setUpClass(cls):
        try:
            from ckanconfig import baseurl, apikey, organization
        except ImportError:
            cls.__unittest_skip__ = True
            cls.__unittest_skip_why__ = 'no CKAN instance configuration found'
        else:
            cls.ckan_config = {'ckan-baseurl': baseurl,
                               'ckan-api-key': apikey,
                               'ckan-organization': organization}
            cls.dataset_owner_org = organization

    def setup_database(self):
        for k, v in self.ckan_config.items():
            self.config.global_set_option(k, v)
