# Copyright 2012 NetApp
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
"""Interface for shares extension."""

try:
    from urllib import urlencode  # noqa
except ImportError:
    from urllib.parse import urlencode  # noqa

from manilaclient import base
from manilaclient.common import constants
from manilaclient.openstack.common.apiclient import base as common_base


class ShareSnapshot(common_base.Resource):
    """Represent a snapshot of a share."""

    def __repr__(self):
        return "<ShareSnapshot: %s>" % self.id

    def update(self, **kwargs):
        """Update this snapshot."""
        self.manager.update(self, **kwargs)

    def reset_state(self, state):
        """Update the snapshot with the privided state."""
        self.manager.reset_state(self, state)

    def delete(self):
        """Delete this snapshot."""
        self.manager.delete(self)

    def force_delete(self):
        """Delete the specified snapshot ignoring its current state."""
        self.manager.force_delete(self)


class ShareSnapshotManager(base.ManagerWithFind):
    """Manage :class:`ShareSnapshot` resources."""
    resource_class = ShareSnapshot

    def create(self, share, force=False, name=None, description=None):
        """Create a snapshot of the given share.

        :param share_id: The ID of the share to snapshot.
        :param force: If force is True, create a snapshot even if the
                      share is busy. Default is False.
        :param name: Name of the snapshot
        :param description: Description of the snapshot
        :rtype: :class:`ShareSnapshot`
        """
        body = {'snapshot': {'share_id': common_base.getid(share),
                             'force': force,
                             'name': name,
                             'description': description}}
        return self._create('/snapshots', body, 'snapshot')

    def get(self, snapshot_id):
        """Get a snapshot.

        :param snapshot_id: The ID of the snapshot to get.
        :rtype: :class:`ShareSnapshot`
        """
        return self._get('/snapshots/%s' % snapshot_id, 'snapshot')

    def list(self, detailed=True, search_opts=None, sort_key=None,
             sort_dir=None):
        """Get a list of snapshots of shares.

        :param search_opts: Search options to filter out shares.
        :param sort_key: Key to be sorted.
        :param sort_dir: Sort direction, should be 'desc' or 'asc'.
        :rtype: list of :class:`ShareSnapshot`
        """
        if search_opts is None:
            search_opts = {}

        if sort_key is not None:
            if sort_key in constants.SNAPSHOT_SORT_KEY_VALUES:
                search_opts['sort_key'] = sort_key
            else:
                raise ValueError(
                    'sort_key must be one of the following: %s.'
                    % ', '.join(constants.SNAPSHOT_SORT_KEY_VALUES))

        if sort_dir is not None:
            if sort_dir in constants.SORT_DIR_VALUES:
                search_opts['sort_dir'] = sort_dir
            else:
                raise ValueError(
                    'sort_dir must be one of the following: %s.'
                    % ', '.join(constants.SORT_DIR_VALUES))

        if search_opts:
            query_string = urlencode(
                sorted([(k, v) for (k, v) in list(search_opts.items()) if v]))
            if query_string:
                query_string = "?%s" % (query_string,)
        else:
            query_string = ''

        if detailed:
            path = "/snapshots/detail%s" % (query_string,)
        else:
            path = "/snapshots%s" % (query_string,)

        return self._list(path, 'snapshots')

    def delete(self, snapshot):
        """Delete a snapshot of a share.

        :param snapshot: The :class:`ShareSnapshot` to delete.
        """
        self._delete("/snapshots/%s" % common_base.getid(snapshot))

    def force_delete(self, snapshot):
        return self._action('os-force_delete', common_base.getid(snapshot))

    def update(self, snapshot, **kwargs):
        """Update a snapshot.

        :param snapshot: Snapshot to update.
        :rtype: :class:`ShareSnapshot`
        """
        if not kwargs:
            return

        body = {'snapshot': kwargs, }
        return self._update("/snapshots/%s" % snapshot.id, body)

    def reset_state(self, snapshot, state):
        """Update the specified share snapshot with the provided state."""
        return self._action('os-reset_status', snapshot, {'status': state})

    def _action(self, action, snapshot, info=None, **kwargs):
        """Perform a  snapshot 'action'."""
        body = {action: info}
        self.run_hooks('modify_body_for_action', body, **kwargs)
        url = '/snapshots/%s/action' % common_base.getid(snapshot)
        return self.api.client.post(url, body=body)
