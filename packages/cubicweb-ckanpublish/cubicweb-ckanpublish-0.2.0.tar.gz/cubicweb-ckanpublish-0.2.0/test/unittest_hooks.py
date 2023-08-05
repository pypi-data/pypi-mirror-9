"""cubicweb-ckanpublish unit tests for hooks"""

from cubicweb import Binary
from cubicweb.devtools.testlib import CubicWebTC

from cubes.ckanpublish.utils import ckan_post, CKANPostError
from cubes.ckanpublish.testutils import CKANPublishTestMixin


class CKANPublishHooksTC(CKANPublishTestMixin, CubicWebTC):

    def tearDown(self):
        with self.admin_access.repo_cnx() as cnx:
            # Delete entities linked to a CKAN dataset as well as their
            # resources, so that the CKAN dataset and resources get deleted.
            # However, datasets will still have to be purge from the web ui.
            cnx.execute('DELETE CWDataSet X WHERE EXISTS(X ckan_dataset_id I)')
            cnx.execute('DELETE File X WHERE EXISTS(X ckan_resource_id I)')
            cnx.commit()
        super(CKANPublishHooksTC, self).tearDown()

    def test_dataset(self):
        with self.admin_access.repo_cnx() as cnx:
            entity = cnx.create_entity('CWDataSet', name=u'buz buz ?!',
                                       description=u'opendata buzzzz')
            cnx.commit()
            yield self._check_dataset_create, cnx, entity
            yield self._check_dataset_update, cnx, entity
            yield self._check_dataset_delete, cnx, entity

    def _check_dataset_create(self, cnx, entity):
        self.set_description('entity creation')
        self.assertIsNotNone(entity.ckan_dataset_id)
        result = ckan_post(self.ckan_config, 'package_show',
                           {'id': entity.ckan_dataset_id})
        self.assertEqual(result['name'], '%s-buz-buz' % entity.eid)
        self.assertEqual(result['title'], entity.name)
        self.assertEqual(result['notes'], entity.description)
        cpublish = entity.cw_adapt_to('ICKANDataset')
        organization_id = cpublish.ckan_get_organization_id(
            self.dataset_owner_org)
        self.assertEqual(result['owner_org'], organization_id)

    def _check_dataset_update(self, cnx, entity):
        self.set_description('entity update')
        entity.cw_set(description=u'no this is actually serious')
        cnx.commit()
        result = ckan_post(self.ckan_config, 'package_show',
                           {'id': entity.ckan_dataset_id})
        self.assertEqual(result['notes'], entity.description)
        user = self.create_user(cnx, 'toto', firstname=u'T.',
                                surname=u'Oto', email=u'to@t.o')
        entity.cw_set(maintainer=user)
        cnx.commit()
        result = ckan_post(self.ckan_config, 'package_show',
                           {'id': entity.ckan_dataset_id})
        self.assertEqual(result['maintainer'], 'T. Oto')
        self.assertEqual(result['maintainer_email'], 'to@t.o')

    def _check_dataset_delete(self, cnx, entity):
        self.set_description('entity deletion')
        ckanid = entity.ckan_dataset_id
        entity.cw_delete()
        cnx.commit()
        result = ckan_post(self.ckan_config, 'package_show',
                           {'id': ckanid})
        self.assertEqual(result['state'], 'deleted')

    def test_resources(self):
        with self.admin_access.repo_cnx() as cnx:
            dataset = cnx.create_entity('CWDataSet', name=u'blurp',
                                        description=u'flop')
            resource = cnx.create_entity('File', data=Binary('yui'),
                                         data_format=u'text/plain',
                                         data_name=u'blurp')
            cnx.commit()
            yield self._check_resource_creation, cnx, dataset, resource
            yield self._check_resource_update, cnx, resource
            yield self._check_resource_delete, cnx, dataset, resource

    def _check_resource_creation(self, cnx, dataset, resource):
        self.set_description('resource creation')
        # Keep the modification_date before update of the File due to setting
        # the ckan_resource_id attribute as this event will not be propagated
        # to CKAN instance since the corresponding hook is disabled.
        resource_md = resource.modification_date.isoformat()
        dataset.cw_set(resources=resource)
        cnx.commit()
        resource.cw_clear_all_caches()
        self.assertIsNotNone(resource.ckan_resource_id)
        result = ckan_post(self.ckan_config, 'package_show',
                           {'id': dataset.ckan_dataset_id})
        resources = result['resources']
        self.assertEqual(len(resources), 1)
        result = ckan_post(self.ckan_config, 'resource_show',
                           {'id': resource.ckan_resource_id})
        self.assertEqual(result['created'],
                         resource.creation_date.isoformat())
        self.assertEqual(result['last_modified'], resource_md)
        self.assertEqual(result['name'], u'blurp')
        self.assertEqual(result['mimetype'], 'text/plain')

    def _check_resource_update(self, cnx, resource):
        self.set_description('resource update')
        resource.cw_set(data_name=u'gloups')
        cnx.commit()
        result = ckan_post(self.ckan_config, 'resource_show',
                           {'id': resource.ckan_resource_id})
        self.assertEqual(result['name'], u'gloups')

    def _check_resource_delete(self, cnx, dataset, resource):
        self.set_description('resource deletion')
        ckanid = dataset.ckan_dataset_id
        resource_id = resource.ckan_resource_id
        resource.cw_delete()
        cnx.commit()
        result = ckan_post(self.ckan_config, 'resource_show',
                           {'id': resource_id})
        self.assertEqual(result['state'], 'deleted')


if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()

