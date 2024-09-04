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
"""Script for running the resource management server."""


import sqlite3
import time

from config import Config
from flask import Flask
from flask import jsonify
from flask import request

app = Flask(__name__)


def connect_db() -> sqlite3.Connection:
    """Connect to the SQLite database.

    Returns:
        sqlite3.Connection: Connection object to the SQLite database.
    """
    return sqlite3.connect(Config.RESOURCE_DB_PATH)


def current_timestamp() -> int:
    """Get the current timestamp.

    Returns:
        int: The current timestamp in the specified format.
    """
    return int(time.time() * 1000)


@app.before_first_request
def initialize() -> None:
    """Reset occupation status of all resources."""
    with connect_db() as conn:
        c = conn.cursor()
        update_query = '''
        UPDATE resource_operator
        SET robot_id = '';
        '''
        c.execute(update_query)
        conn.commit()
        print("All robot_id values have been set to an empty string.")


@app.route('/api/all_data', methods=['GET'])
def get_data() -> dict:
    """Get all data from the resource_operator table (for debug purposes).

    Returns:
        dict: A dictionary containing the data from the resource_operator table.
    """
    try:
        with connect_db() as conn:
            c = conn.cursor()
            c.execute('SELECT * FROM resource_operator')
            rows = c.fetchall()
    except sqlite3.Error as e:
        return jsonify({"error": str(e)}), 500
    data = [{"building_id": row[1], "resource_id": row[2], "robot_id": row[3]} for row in rows]
    return jsonify(data)


@app.route('/api/registration', methods=['POST'])
def registration_call() -> dict:
    """Register a robot to a resource.

    Returns:
        dict: A dictionary containing the result of the registration request.
    """
    received_data = request.json
    if not received_data or not all(key in received_data for key in ["api", "request_id"]):
        return jsonify({"error": "Invalid request data"}), 400
    if received_data["api"] != "Registration":
        return jsonify({
            "api": "RegistrationResult",
            "result": 3,
            "request_id": received_data["request_id"],
            "timestamp": current_timestamp()})

    try:
        with connect_db() as conn:
            c = conn.cursor()
            c.execute(
                'SELECT * FROM resource_operator WHERE building_id = ? AND resource_id = ?',
                (received_data["bldg_id"], received_data["resource_id"]))
            row = c.fetchone()
            if row and row[3]:
                return_data = {
                    "api": "RegistrationResult",
                    "result": 2,
                    "request_id": received_data["request_id"],
                    "timestamp": current_timestamp()}
            else:
                c.execute('UPDATE resource_operator SET robot_id = ? WHERE building_id = ? AND resource_id = ?',
                          (received_data["robot_id"], received_data["bldg_id"], received_data["resource_id"]))
                return_data = {
                    "api": "RegistrationResult",
                    "result": 1,
                    "request_id": received_data["request_id"],
                    "timestamp": current_timestamp()}
                conn.commit()
    except sqlite3.Error as e:
        return jsonify({"error": str(e)}), 500

    return jsonify(return_data)


@app.route('/api/release', methods=['POST'])
def release_call() -> dict:
    """Release a robot from a resource.

    Returns:
        dict: A dictionary containing the result of the release request.
    """
    received_data = request.json

    if not received_data or not all(key in received_data for key in ["api", "request_id"]):
        return jsonify({"error": "Invalid request data"}), 400

    if received_data["api"] != "Release":
        return jsonify({
            "api": "ReleaseResult",
            "result": 3,
            "resource_id": received_data.get("resource_id", ""),
            "request_id": received_data["request_id"],
            "timestamp": current_timestamp()})
    try:
        with connect_db() as conn:
            c = conn.cursor()
            c.execute('SELECT * FROM resource_operator WHERE building_id = ? AND resource_id = ?',
                      (received_data["bldg_id"], received_data["resource_id"]))
            row = c.fetchone()

            if row and received_data["robot_id"] == row[3]:
                # Update the resource to release the robot
                c.execute('''
                    UPDATE resource_operator
                    SET robot_id = ?
                    WHERE building_id = ? AND resource_id = ?
                ''', ("", received_data["bldg_id"], received_data["resource_id"]))

                conn.commit()

                return_data = {
                    "api": "ReleaseResult",
                    "result": 1,
                    "resource_id": received_data["resource_id"],
                    "request_id": received_data["request_id"],
                    "timestamp": current_timestamp()}
            else:
                return_data = {
                    "api": "ReleaseResult",
                    "result": 2,
                    "resource_id": received_data["resource_id"],
                    "request_id": received_data["request_id"],
                    "timestamp": current_timestamp()}
    except sqlite3.Error as e:
        return jsonify({"error": str(e)}), 500
    return jsonify(return_data)


if __name__ == "__main__":
    app.run(debug=True)
