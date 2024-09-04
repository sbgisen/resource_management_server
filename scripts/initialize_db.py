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

from resource_management_server.config import Config

# データベースファイルを作成または接続
conn = sqlite3.connect(Config.RESOURCE_DB_PATH)

# カーソルオブジェクトを作成
c = conn.cursor()

# 既存のテーブルを削除する
c.execute('DROP TABLE IF EXISTS resource_operator')

# テーブルを作成
c.execute('''
CREATE TABLE IF NOT EXISTS resource_operator (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    building_id TEXT NOT NULL,
    resource_id TEXT NOT NULL,
    robot_id TEXT NOT NULL
)
''')

# データの挿入
c.execute('''
INSERT INTO resource_operator (building_id, resource_id, robot_id)
VALUES ('Takeshiba', 'Resource01', '')
''')

# コミットして変更を保存
conn.commit()

# 接続を閉じる
conn.close()

print("Database and table created successfully.")
