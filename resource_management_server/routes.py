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
"""Routing for the Flask server app."""

import sqlite3

from flask import Flask
from flask import Response
from flask import jsonify
from flask import request
from pydantic import ValidationError

from .database import connect_db
from .database import current_timestamp
from .database import get_expiration_time
from .database import get_max_expiration_time
from .models import RegistrationPayload
from .models import RegistrationResultPayload
from .models import ReleasePayload
from .models import ReleaseResultPayload
from .models import RequestResourceStatusPayload
from .models import ResourceData
from .models import ResourceState
from .models import ResourceStatusPayload
from .models import ResultId
from .models import RobotState
from .models import RobotStatusPayload
from .models import RobotStatusResultPayload


def register_routes(app: Flask) -> None:
    @app.route('/api/all_data', methods=['GET'])
    def get_all_data() -> Response:
        """Get all data from the resource_operator table.

        THIS API IS FOR DEBUG PURPOSES ONLY.

        Returns:
            Response: JSON response containing the data from the resource_operator table.
        """
        try:
            with connect_db() as conn:
                c = conn.cursor()
                c.execute('SELECT * FROM resource_operator')
                rows = c.fetchall()
        except sqlite3.Error as err:
            return jsonify({'error': str(err)}), 500
        try:
            data = [ResourceData(**row) for row in rows]
            return jsonify([item.dict() for item in data])
        except ValidationError as err:
            return jsonify({'error': f'Data validation error: {str(err)}'}), 500

    @app.route('/api/registration', methods=['POST'])
    def registration_call() -> Response:
        """Register a robot to a resource.

        Returns:
            Response: JSON response containing the result of the registration request.
        """
        try:
            request_data = RegistrationPayload(**request.json)
        except ValidationError as err:
            print(f'Validation error:\n{err}')
            error_response = RegistrationResultPayload(
                result=ResultId.OTHERS,
                max_expiration_time=0,
                expiration_time=0,
                request_id=request.json.get("request_id", ""),
                timestamp=current_timestamp())
            return jsonify(error_response.model_dump()), 400
        return_data = RegistrationResultPayload(
            result=ResultId.SUCCESS,
            max_expiration_time=0,
            expiration_time=0,
            request_id=request_data.request_id,
            timestamp=current_timestamp())
        try:
            with connect_db() as conn:
                c = conn.cursor()
                c.execute(
                    'SELECT * FROM resource_operator WHERE bldg_id = ? AND resource_id = ?',
                    (request_data.bldg_id, request_data.resource_id))
                row = c.fetchone()
                if row is None:
                    return_data.result = ResultId.OTHERS
                elif row['locked_by']:
                    return_data.result = ResultId.FAILURE
                else:
                    expiration_time = get_expiration_time(
                        request_data.timestamp, row['default_timeout'], row['max_timeout'], request_data.timeout)
                    if not expiration_time:
                        print('Requested timeout or timestamp is invalid.')
                        return_data.result = ResultId.OTHERS
                    else:
                        c.execute('''
                            UPDATE resource_operator SET locked_by = ?, locked_time = ?, expiration_time = ?\
                                WHERE bldg_id = ? AND resource_id = ?
                        ''', (
                            request_data.robot_id, request_data.timestamp, expiration_time,
                            request_data.bldg_id, request_data.resource_id))
                        return_data.max_expiration_time = get_max_expiration_time(
                            request_data.timestamp, row['max_timeout'])
                        return_data.expiration_time = expiration_time
                        conn.commit()
        except sqlite3.Error as err:
            print(f'SQLite error:\n{err}')
            return_data.result = ResultId.OTHERS
        return jsonify(return_data.model_dump())

    @app.route('/api/release', methods=['POST'])
    def release_call() -> Response:
        """Release a robot from a resource.

        Returns:
            Response: JSON response containing the result of the release request.
        """
        try:
            received_data = ReleasePayload(**request.json)
        except ValidationError as err:
            print(f'Validation error:\n{err}')
            error_response = ReleaseResultPayload(
                result=ResultId.OTHERS,
                resource_id=request.json.get("resource_id", ""),
                request_id=request.json.get("request_id", ""),
                timestamp=current_timestamp())
            return jsonify(error_response.model_dump()), 400
        return_data = ReleaseResultPayload(
            result=ResultId.SUCCESS,
            resource_id=received_data.resource_id,
            request_id=received_data.request_id,
            timestamp=current_timestamp())
        try:
            with connect_db() as conn:
                c = conn.cursor()
                c.execute(
                    'SELECT * FROM resource_operator WHERE bldg_id = ? AND resource_id = ?',
                    (received_data.bldg_id, received_data.resource_id))
                row = c.fetchone()
                if row and received_data.robot_id == row['locked_by']:
                    # Update the resource to release the robot
                    c.execute('''
                        UPDATE resource_operator
                        SET locked_by = ?
                        WHERE bldg_id = ? AND resource_id = ?
                    ''', ("", received_data.bldg_id, received_data.resource_id))

                    conn.commit()
                else:
                    return_data.result = ResultId.FAILURE
        except sqlite3.Error as err:
            print(f'SQLite error:\n{err}')
            return_data.result = ResultId.OTHERS
        return jsonify(return_data.model_dump())

    @app.route('/api/request_resource_status', methods=['POST'])
    def request_resource_status() -> Response:
        """Request the status of a resource.

        Returns:
            Response: JSON response containing the status of the requested resource.
        """
        try:
            received_data = RequestResourceStatusPayload(**request.json)
        except ValidationError as err:
            error_response = ResourceStatusPayload(
                result=ResultId.OTHERS,
                resource_id=request.json.get("resource_id", ""),
                resource_state=ResourceState.UNKNOWN,
                request_id=request.json.get("request_id", ""),
                timestamp=current_timestamp())
            print(f'Validation error:\n{err}')
            return jsonify(error_response.model_dump()), 400
        return_data = ResourceStatusPayload(
            result=ResultId.SUCCESS,
            robot_id="",
            max_expiration_time=0,
            expiration_time=0,
            resource_id=received_data.resource_id,
            resource_state=ResourceState.UNKNOWN,
            request_id=received_data.request_id,
            timestamp=current_timestamp())
        try:
            with connect_db() as conn:
                c = conn.cursor()
                c.execute(
                    'SELECT * FROM resource_operator WHERE bldg_id = ? AND resource_id = ?',
                    (received_data.bldg_id, received_data.resource_id))
                row = c.fetchone()
                if row:
                    return_data.resource_state = \
                        ResourceState.OCCUPIED if row['locked_by'] else ResourceState.AVAILABLE
                    return_data.robot_id = row['locked_by']  # Should be empty string when unoccupied.
                    if row['locked_by']:
                        return_data.expiration_time = row['expiration_time']
                        return_data.max_expiration_time = get_max_expiration_time(
                            row['locked_time'], row['max_timeout'])
                else:
                    return_data.result = ResultId.FAILURE
        except sqlite3.Error as err:
            print(f'SQLite error:\n{err}')
            return_data.result = ResultId.OTHERS
        return jsonify(return_data.model_dump())

    @app.route('/api/robot_status', methods=['POST'])
    def robot_status() -> Response:
        """Update the status of a robot.

        Returns:
            Response: JSON response containing the result of the robot status update.
        """
        try:
            received_data = RobotStatusPayload(**request.json)
        except ValidationError as err:
            error_response = RobotStatusResultPayload(
                result=ResultId.OTHERS,
                request_id=request.json.get("request_id", ""),
                timestamp=current_timestamp())
            print(f'Validation error:\n{err}')
            return jsonify(error_response.model_dump()), 400
        return_data = RobotStatusResultPayload(
            result=ResultId.SUCCESS,
            request_id=received_data.request_id,
            timestamp=current_timestamp())
        # TODO
        try:
            with connect_db() as conn:
                if received_data.state == RobotState.CANCEL:
                    print("Robot has canceled the request.")
                    # Find the resource the robot is using and release it.
                    c = conn.cursor()
                    c.execute(
                        'SELECT * FROM resource_operator WHERE locked_by = ?',
                        (received_data.robot_id,))
                    row = c.fetchone()
                    if row:
                        c.execute('''
                            UPDATE resource_operator
                            SET locked_by = ?
                            WHERE bldg_id = ? AND resource_id = ?
                        ''', ('', row['bldg_id'], row['resource_id']))
                        conn.commit()
                    else:
                        return_data.result = ResultId.FAILURE
                # TODO: Manage other states?
        except sqlite3.Error as err:
            print(f'SQLite error:\n{err}')
            return_data.result = ResultId.OTHERS
        return jsonify(return_data.model_dump())
