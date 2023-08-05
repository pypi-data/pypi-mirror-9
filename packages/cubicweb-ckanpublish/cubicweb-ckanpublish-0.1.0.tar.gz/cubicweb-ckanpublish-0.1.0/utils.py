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
"""cubicweb-cg33catsi utilities"""

import json
from urlparse import urljoin

import requests

from cubicweb.predicates import objectify_predicate


class CKANPostError(Exception):
    """CKAN post action error"""


def ckan_buildurl(config, path):
    """Return a full URL in the CKAN instance built from path"""
    base = config['ckan-baseurl']
    if not base.endswith('/'):
        base += '/'
    return urljoin(base, path)


def ckan_post(config, action, data=None, files=None):
    """Post an API request for `action` in the CKAN instance"""
    url = ckan_buildurl(config, 'api/3/action/' + action)
    headers = {'Authorization': config['ckan-api-key']}
    if files is None:
        data = json.dumps(data or {})
        headers['Content-Type'] = 'application/json'
    resp = requests.post(url, headers=headers, data=data, files=files)
    try:
        jresp = resp.json()
    except ValueError:
        error = resp.text
    else:
        if resp.ok:
            return jresp['result']
        else:
            try:
                error = jresp['error']
            except TypeError:
                # Sometimes, jresp is not as dict.
                error = jresp
    raise CKANPostError('action %s failed: %s' % (action, error))


@objectify_predicate
def ckan_instance_configured(cls, req, **kwargs):
    """Return 1 if CKAN instance configuration is defined.

    (Mostly useful in tests to disable CKAN hooks.)
    """
    config = req.vreg.config
    for option in ('ckan-baseurl', 'ckan-api-key'):
        if not config.get(option):
            req.warning('CKAN instance configuration incomplete, missing "%s" '
                        'option' % option)
            return 0
    return 1
