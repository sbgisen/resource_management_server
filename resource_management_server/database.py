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
"""Functions for handling the resource management server database."""

import os
import sqlite3
import sys
import threading
import time

import yaml
from pydantic import ValidationError

from .config import Config
from .models import ResourceData


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
        expiration_time INTEGER,
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
                (bldg_id, resource_id, resource_type, max_timeout, default_timeout,
                locked_by, locked_time, expiration_time)\
            VALUES (?, ?, ?, ?, ?, '', 0, 0)
            ON CONFLICT(resource_id) DO NOTHING
            ''', (
                resource.bldg_id, resource.resource_id, resource.resource_type.value,
                resource.max_timeout * 1000, resource.default_timeout * 1000))  # Convert to milliseconds


def connect_db() -> sqlite3.Connection:
    """Connect to the SQLite database.

    Returns:
        sqlite3.Connection: Connection object to the SQLite database.
    """
    conn = sqlite3.connect(Config.RESOURCE_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_db() -> None:
    """Initialize the database and create a table using the given YAML config."""
    yaml_path = os.environ.get('RESOURCE_YAML_PATH')
    if not yaml_path:
        print('RESOURCE_YAML_PATH environment variable is not set.')
        sys.exit(1)
    with connect_db() as conn:
        c = conn.cursor()
        create_table(c)
        resources = load_resources_from_yaml(yaml_path)
        if not resources:
            print('Failed to load resources from YAML.')
            conn.close()
            sys.exit(1)
        insert_resources(c, resources)
        conn.commit()
        print(f'Database and table created successfully with data from {yaml_path}.')


def current_timestamp() -> int:
    """Get the current timestamp.

    Returns:
        int: The current timestamp in the specified format.
    """
    return int(time.time() * 1000)


def get_max_expiration_time(locked_time: int, max_timeout: int) -> int:
    """Calculate the max expiration time for a resource.

    Args:
        locked_time (int): The time the resource was locked.
        max_timeout (int): The max timeout for the resource.

    Returns:
        int: The max expiration time (millisecs) for the resource.
    """
    return locked_time + max_timeout


def get_expiration_time(
        locked_time: int, default_timeout: int, max_timeout: int, requested_timeout: int) -> int | None:
    """Calculate the expiration time for a resource.

    Args:
        locked_time (int): The time the resource was locked.
        default_timeout (int): The default timeout for the resource.
        max_timeout (int): The max timeout for the resource.
        requested_timeout (int): The timeout requested from the client.

    Returns:
        int | None: The expiration time (millisecs) for the resource.
            None when the given timeout exceeds the max timeout or the current time exceeds the expiration time.
    """
    if requested_timeout == 0:
        requested_timeout = default_timeout
    if max_timeout < requested_timeout:
        return None
    expiration_time = locked_time + requested_timeout
    if current_timestamp() > expiration_time:
        return None
    return expiration_time


def check_for_timeout() -> None:
    """Periodically checks for resources that have exceeded their max timeout and releases them."""
    while True:
        current_time = current_timestamp()
        try:
            with connect_db() as conn:
                c = conn.cursor()
                # Select all resources where the locked time exceeds the max timeout.
                c.execute('''
                    SELECT * FROM resource_operator
                    WHERE locked_by != "" AND locked_time + max_timeout < ?
                ''', (current_time,))
                rows = c.fetchall()

                for row in rows:
                    # Release resources that have exceeded the max timeout
                    c.execute('''
                        UPDATE resource_operator
                        SET locked_by = ?, locked_time = 0, expiration_time = 0
                        WHERE bldg_id = ? AND resource_id = ?
                    ''', ("", row['bldg_id'], row['resource_id']))
                    conn.commit()
                    print(f"Released resource {row['resource_id']} in building {row['bldg_id']} due to timeout.")
        except sqlite3.Error as err:
            print(f"SQLite error during timeout check: {err}")
        time.sleep(1)


def start_timeout_check() -> None:
    """Start the timeout check thread."""
    timeout_thread = threading.Thread(target=check_for_timeout, daemon=True)
    timeout_thread.start()
