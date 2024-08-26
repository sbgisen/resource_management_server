#initialize_db.py

#!/usr/bin/env python3

import sqlite3
from constants import RESOURCE_DB_NAME, RESOURCE_DB_PATH

# データベースファイルを作成または接続
conn = sqlite3.connect(RESOURCE_DB_PATH)

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
