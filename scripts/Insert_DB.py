import sqlite3

# データベースに再接続
conn = sqlite3.connect('resource_operator.db')
c = conn.cursor()

# データの挿入
c.execute('''
INSERT INTO resource_operator (building_id, resource_id, robot_id)
VALUES ('Takeshiba', 'Resource01', '')
''')


# コミットして変更を保存
conn.commit()

# 接続を閉じる
conn.close()

print("Data inserted successfully.")
