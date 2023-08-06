# Copyright 2010 Jacob Kaplan-Moss

# Copyright 2011 OpenStack LLC.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import ddt
import mock

from manilaclient import exceptions
from manilaclient import extension
from manilaclient.tests.unit import utils
from manilaclient.tests.unit.v1 import fakes
from manilaclient.v1 import shares


extensions = [
    extension.Extension('shares', shares),
]
cs = fakes.FakeClient(extensions=extensions)


@ddt.ddt
class SharesTest(utils.TestCase):

    # Testcases for class Share
    def setUp(self):
        super(SharesTest, self).setUp()
        self.share = shares.Share(None, {'id': 1})
        self.share.manager = mock.Mock()

    def test_share_allow_access_cert(self):
        access_type = 'cert'
        access_to = 'client.example.com'
        access_level = None

        self.share.allow(access_type, access_to, access_level)

        self.assertTrue(self.share.manager.allow.called)

    def test_share_allow_access_cert_error_gt64(self):
        access_type = 'cert'
        access_to = 'x' * 65
        access_level = None

        self.assertRaises(exceptions.CommandError, self.share.allow,
                          access_type, access_to, access_level)
        self.assertFalse(self.share.manager.allow.called)

    def test_share_allow_access_cert_error_whitespace(self):
        access_type = 'cert'
        access_to = ' '
        access_level = None

        self.assertRaises(exceptions.CommandError, self.share.allow,
                          access_type, access_to, access_level)
        self.assertFalse(self.share.manager.allow.called)

    def test_share_allow_access_cert_error_zero(self):
        access_type = 'cert'
        access_to = ''
        access_level = None

        self.assertRaises(exceptions.CommandError, self.share.allow,
                          access_type, access_to, access_level)
        self.assertFalse(self.share.manager.allow.called)

    @ddt.data(
        'Administrator',
        'MYDOMAIN\Administrator',
        'fake\\]{.-_\'`;}[',
        '1' * 4,
        '1' * 32)
    def test_share_allow_access_user(self, user):
        self.share.allow('user', user, None)
        self.assertTrue(self.share.manager.allow.called)

    @ddt.data(
        '',
        'abc',
        'root^',
        '1' * 33)
    def test_share_allow_access_user_invalid(self, user):
        self.assertRaises(
            exceptions.CommandError, self.share.allow, 'user', user, None)
        self.assertFalse(self.share.manager.allow.called)

    # Testcases for class ShareManager
    def test_create_nfs_share(self):
        cs.shares.create('nfs', 1)
        cs.assert_called('POST', '/shares')

    def test_create_cifs_share(self):
        cs.shares.create('cifs', 2)
        cs.assert_called('POST', '/shares')

    @ddt.data(True, False)
    def test_create_share_with_public_attr_defined(self, is_public):
        body = {
            'share': {
                'is_public': is_public,
                'share_type': None,
                'name': None,
                'snapshot_id': None,
                'description': None,
                'metadata': {},
                'share_proto': 'nfs',
                'share_network_id': None,
                'size': 1,
            }
        }
        cs.shares.create('nfs', 1, is_public=is_public)
        cs.assert_called('POST', '/shares', body)

    def test_delete_share(self):
        share = cs.shares.get('1234')
        cs.shares.delete(share)
        cs.assert_called('DELETE', '/shares/1234')

    def test_manage_share(self):
        cs.shares.manage('fake_service', 'fake_proto', 'fake_export_path', {})
        cs.assert_called('POST', '/os-share-manage')

    def test_unmanage_share(self):
        share = cs.shares.get('1234')
        cs.shares.unmanage(share)
        cs.assert_called('POST', '/os-share-unmanage/1234/unmanage')

    def test_force_delete_share(self):
        share = cs.shares.get('1234')
        cs.shares.force_delete(share)
        cs.assert_called('POST', '/shares/1234/action',
                         {'os-force_delete': None})

    def test_list_shares_index(self):
        cs.shares.list(detailed=False)
        cs.assert_called('GET', '/shares?is_public=True')

    def test_list_shares_index_with_search_opts(self):
        search_opts = {
            'fake_str': 'fake_str_value',
            'fake_int': 1,
        }
        cs.shares.list(detailed=False, search_opts=search_opts)
        cs.assert_called(
            'GET',
            '/shares?fake_int=1&fake_str=fake_str_value&is_public=True')

    def test_list_shares_detailed(self):
        cs.shares.list(detailed=True)
        cs.assert_called('GET', '/shares/detail?is_public=True')

    def test_list_shares_detailed_with_search_opts(self):
        search_opts = {
            'fake_str': 'fake_str_value',
            'fake_int': 1,
        }
        cs.shares.list(detailed=True, search_opts=search_opts)
        cs.assert_called(
            'GET',
            '/shares/detail?fake_int=1&fake_str=fake_str_value&is_public=True')

    def test_list_shares_sort_by_asc_and_host_key(self):
        cs.shares.list(detailed=False, sort_key='host', sort_dir='asc')
        cs.assert_called('GET',
                         '/shares?is_public=True&sort_dir=asc&sort_key=host')

    def test_list_shares_sort_by_desc_and_size_key(self):
        cs.shares.list(detailed=False, sort_key='size', sort_dir='desc')
        cs.assert_called('GET',
                         '/shares?is_public=True&sort_dir=desc&sort_key=size')

    def test_list_shares_filter_by_share_network_alias(self):
        cs.shares.list(detailed=False, sort_key='share_network')
        cs.assert_called('GET',
                         '/shares?is_public=True&sort_key=share_network_id')

    def test_list_shares_filter_by_snapshot_alias(self):
        cs.shares.list(detailed=False, sort_key='snapshot')
        cs.assert_called('GET', '/shares?is_public=True&sort_key=snapshot_id')

    def test_list_shares_filter_by_share_type_alias(self):
        cs.shares.list(detailed=False, sort_key='share_type')
        cs.assert_called('GET',
                         '/shares?is_public=True&sort_key=share_type_id')

    def test_list_shares_by_improper_direction(self):
        self.assertRaises(ValueError, cs.shares.list, sort_dir='fake')

    def test_list_shares_by_improper_key(self):
        self.assertRaises(ValueError, cs.shares.list, sort_key='fake')

    def test_allow_access_to_share(self):
        share = cs.shares.get(1234)
        ip = '192.168.0.1'
        cs.shares.allow(share, 'ip', ip, None)
        cs.assert_called('POST', '/shares/1234/action')

    def test_allow_access_to_share_with_cert(self):
        share = cs.shares.get(1234)
        common_name = 'test.example.com'
        cs.shares.allow(share, 'cert', common_name, None)
        cs.assert_called('POST', '/shares/1234/action')

    def test_get_metadata(self):
        cs.shares.get_metadata(1234)
        cs.assert_called('GET', '/shares/1234/metadata')

    def test_set_metadata(self):
        cs.shares.set_metadata(1234, {'k1': 'v2'})
        cs.assert_called('POST', '/shares/1234/metadata',
                         {'metadata': {'k1': 'v2'}})

    def test_delete_metadata(self):
        keys = ['key1']
        cs.shares.delete_metadata(1234, keys)
        cs.assert_called('DELETE', '/shares/1234/metadata/key1')

    def test_metadata_update_all(self):
        cs.shares.update_all_metadata(1234, {'k1': 'v1'})
        cs.assert_called('PUT', '/shares/1234/metadata',
                         {'metadata': {'k1': 'v1'}})
