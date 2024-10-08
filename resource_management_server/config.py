# Copyright (c) 2024 SoftBank Corp.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Configuration for the resource management server database."""

import os


class Config:
    """Configuration for the resource management server database."""
    BASE_DIR = os.path.expanduser('~/.resource_management_server')
    os.makedirs(BASE_DIR, exist_ok=True)
    RESOURCE_DB_NAME = 'resource_database.db'
    RESOURCE_DB_PATH = os.path.join(BASE_DIR, RESOURCE_DB_NAME)
