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
from datetime import datetime

from constants import RESOURCE_DB_PATH
from flask import Flask
from flask import jsonify
from flask import request

app = Flask(__name__)

# データベース接続用の関数


def connect_db() -> sqlite3.Connection:
    return sqlite3.connect(RESOURCE_DB_PATH)


"""
@app.before_first_request
def initialize():
    # データベースに接続
    conn = connect_db()
    c = conn.cursor()

    # robot_idの値をすべて空文字列にするクエリ
    update_query = '''
    UPDATE resource_operator
    SET robot_id = '';
    '''

    # クエリを実行
    c.execute(update_query)

    # 変更をコミット
    conn.commit()

    # 接続を閉じる
    conn.close()

    print("All robot_id values have been set to an empty string.")
"""

# すべてのデータの取得エンドポイント


@app.route('/api/all_data', methods=['GET'])
def get_data() -> dict:
    conn = connect_db()
    c = conn.cursor()
    c.execute('SELECT * FROM resource_operator')
    rows = c.fetchall()
    conn.close()

    data = []
    for row in rows:
        entry = {
            "building_id": row[1],
            "resource_id": row[2],
            "robot_id": row[3]
        }
        data.append(entry)

    return jsonify(data)

# リソース登録エンドポイント


@app.route('/api/registration', methods=['POST'])
def registration_call() -> dict:
    # POSTリクエストから送信されたデータを格納
    received_data = request.json

    # APIエンドポイントとリクエストAPIの不一致
    if received_data["api"] != "Registration":
        return_data = {
            "api": "RegistrationResult",
            "result": 3,
            "request_id": received_data["request_id"],
            "timestamp": datetime.now()
        }
        return jsonify(return_data)

    # DBからデータを取得
    conn = connect_db()
    c = conn.cursor()
    c.execute('SELECT * FROM resource_operator WHERE building_id = ? AND resource_id = ?',
              (received_data["bldg_id"], received_data["resource_id"]))  # Resource01はこのままでいいのか
    row = c.fetchone()

    if row[3]:  # robot_id が存在し、空でない場合
        return_data = {
            "api": "RegistrationResult",
            "result": 2,
            "request_id": received_data["request_id"],
            "timestamp": datetime.now()
        }
    elif row[3] == "":
        # 更新処理
        c.execute('''
            UPDATE resource_operator
            SET robot_id = ?
            WHERE building_id = ? AND resource_id = ?
        ''', (received_data["robot_id"], received_data["bldg_id"], received_data["resource_id"]))

        return_data = {
            "api": "RegistrationResult",
            "result": 1,
            "request_id": received_data["request_id"],
            "timestamp": datetime.now()
        }

        conn.commit()

    conn.close()
    return jsonify(return_data)

# 登録解除エンドポイント


@app.route('/api/release', methods=['POST'])
def release_call() -> dict:
    # POSTリクエストから送信されたデータを格納(api, bldg-id, robot_id, resource_id, request_id, timestamp_id)
    received_data = request.json

    if received_data["api"] != "Release":
        return_data = {
            "api": "ReleaseResult",
            "result": 3,
            "resource_id": received_data["resource_id"],
            "request_id": received_data["request_id"],
            "timestamp": datetime.now()
        }
        return jsonify(return_data)

    # DBからデータを取得
    conn = connect_db()
    c = conn.cursor()
    c.execute('SELECT * FROM resource_operator WHERE building_id = ? AND resource_id = ?',
              (received_data["bldg_id"], received_data["resource_id"]))  # Resource01はこのままでいいのか
    row = c.fetchone()

    if received_data["robot_id"] == row[3]:  # リクエストしたロボットidと登録済みロボットのidが一致する場合
        # 更新処理
        c.execute('''
            UPDATE resource_operator
            SET robot_id = ?
            WHERE building_id = ? AND resource_id = ?
        ''', ("", received_data["bldg_id"], received_data["resource_id"]))

        return_data = {
            "api": "ReleaseResult",  # 文言チェック
            "result": 1,
            "resource_id": received_data["resource_id"],
            "request_id": received_data["request_id"],
            "timestamp": datetime.now()
        }

        conn.commit()

    else:  # リクエストしたロボットのidと登録済みロボットIDが異なる場合　and　登録済みロボットIDが空の場合
        return_data = {
            "api": "ReleaseResult",  # 文言チェック
            "result": 2,
            "resource_id": received_data["resource_id"],
            "request_id": received_data["request_id"],
            "timestamp": datetime.now()
        }

    conn.close()
    return jsonify(return_data)


if __name__ == "__main__":
    app.run(debug=True)
