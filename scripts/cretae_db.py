import sqlite3

# データベースファイルを作成または接続
conn = sqlite3.connect('resource_operator.db')

# カーソルオブジェクトを作成
c = conn.cursor()

# テーブルを作成
c.execute('''
CREATE TABLE IF NOT EXISTS resource_operator (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    building_id TEXT NOT NULL,
    resource_id TEXT NOT NULL,
    robot_id TEXT NOT NULL
)
''')

# コミットして変更を保存
conn.commit()

# 接続を閉じる
conn.close()

print("Database and table created successfully.")
