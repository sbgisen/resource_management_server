#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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
"""Script used for initializing the resource management database and create a table."""

import sqlite3
import sys

import yaml
from pydantic import ValidationError

from resource_management_server.config import Config
from resource_management_server.model import ResourceData


def create_table(c: sqlite3.Cursor) -> None:
    """Create DB table.

    Args:
        c: Cursor object for the database connection.
    """
    c.execute('DROP TABLE IF EXISTS resource_operator')
    c.execute('''
    CREATE TABLE IF NOT EXISTS resource_operator (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        bldg_id TEXT NOT NULL,
        resource_id TEXT NOT NULL UNIQUE,
        resource_type INTEGER,
        max_timeout INTEGER,
        default_timeout INTEGER,
        locked_by TEXT NOT NULL,
        locked_time INTEGER,
        UNIQUE(resource_id) ON CONFLICT IGNORE
    )
    ''')


def load_resources_from_yaml(yaml_path: str) -> list[ResourceData]:
    """Read resource info from given yaml file.

    Args:
        yaml_path (str): Path to the yaml file.

    Returns:
        list[ResourceData]: List of resource info.
    """
    with open(yaml_path, 'r') as file:
        resources = yaml.safe_load(file)
    validated_resources = []
    for resource in resources:
        try:
            validated_resource = ResourceData(**resource)
            validated_resources.append(validated_resource)
        except ValidationError as err:
            print(f"Validation error for resource {resource.get('resource_id', 'unknown')}: {err}")
            return []
    return validated_resources


def insert_resources(c: sqlite3.Cursor, resources: list[ResourceData]) -> None:
    """Insert given resource info to the database.

    Args:
        c (sqlite3.Cursor): Cursor object for the database connection.
        resources (list[ResourceData]): List of resource info.
    """
    for resource in resources:
        c.execute(
            '''
            INSERT INTO resource_operator\
                  (bldg_id, resource_id, resource_type, max_timeout, default_timeout, locked_by)
            VALUES (?, ?, ?, ?, ?, '')
            ON CONFLICT(resource_id) DO NOTHING
            ''', (
                resource.bldg_id, resource.resource_id, resource.resource_type.value,
                resource.max_timeout, resource.default_timeout))


def main(yaml_path: str) -> None:
    """Main function to initialize the database and create a table.

    Args:
        yaml_path (str): Path to the yaml file.
    """
    conn = sqlite3.connect(Config.RESOURCE_DB_PATH)
    c = conn.cursor()
    create_table(c)
    resources = load_resources_from_yaml(yaml_path)
    if not resources:
        print('Failed to load resources from YAML.')
        conn.close()
        sys.exit(1)
    insert_resources(c, resources)
    conn.commit()
    conn.close()
    print('Database and table created successfully with data from YAML.')


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python initialize_db.py <path_to_resource_config_yaml>")
        sys.exit(1)
    main(sys.argv[1])
