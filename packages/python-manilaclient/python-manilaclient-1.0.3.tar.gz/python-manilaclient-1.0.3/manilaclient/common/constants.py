# Copyright 2014 Mirantis, Inc.
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

"""Common constants that can be used all over the manilaclient."""

# These are used for providing desired sorting params with list requests
SORT_DIR_VALUES = ('asc', 'desc')
SHARE_SORT_KEY_VALUES = (
    'id', 'status', 'size', 'host', 'share_proto',
    'export_location', 'availability_zone',
    'user_id', 'project_id',
    'created_at', 'updated_at',
    'display_name', 'name',
    'share_type_id', 'share_type',
    'share_network_id', 'share_network',
    'snapshot_id', 'snapshot',
)

SNAPSHOT_SORT_KEY_VALUES = (
    'id',
    'status',
    'size',
    'share_id',
    'user_id',
    'project_id',
    'progress',
    'name', 'display_name',
)
