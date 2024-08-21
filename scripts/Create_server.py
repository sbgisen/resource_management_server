from flask import Flask, request, jsonify
import sqlite3
import time
import json

app = Flask(__name__)

# データベース接続用の関数
def connect_db():
    return sqlite3.connect('resource_operator.db')

# すべてのデータの取得エンドポイント
@app.route('/api/all_data', methods=['GET'])
def get_data():
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

# データの取得エンドポイント
@app.route('/api/resource01/regist', methods=['POST'])
def regist_call():
    # POSTリクエストから送信されたデータを格納
    received_data = request.json

    # DBからデータを取得
    conn = connect_db()
    c = conn.cursor()
    c.execute('SELECT * FROM resource_operator WHERE building_id = ? AND resource_id = ?', 
              (received_data.get("bldg_id"), "Resource01"))
    row = c.fetchone()

    if row and row[3]:  # robot_id が存在し、空でない場合
        return_data = {
            "api": "RegistrationResult",
            "result": 2,
            "request_id": received_data.get("request_id", ""),
            "timestamp": time.time()
        }
    else:
        # 更新処理
        c.execute('''
            UPDATE resource_operator
            SET robot_id = ?
            WHERE building_id = ? AND resource_id = ?
        ''', (received_data["robot_id"], received_data.get("bldg_id"), "Resource01"))
        
        return_data = {
            "api": "RegistrationResult",
            "result": 1,
            "request_id": received_data.get("request_id", ""),
            "timestamp": time.time()
        }

        conn.commit()

    conn.close()
    return jsonify(return_data)

if __name__ == "__main__":
    app.run(debug=True)
