from flask import Flask, request, jsonify
import sqlite3
import time
import json

app = Flask(__name__)

# データベース接続用の関数
def connect_db():# 登録申請エンドポイント
@app.route('/api/resource01/regist', methods=['POST'])
def regist_call():
    # POSTリクエストから送信されたデータを格納
    received_data = request.json

    # DBからデータを取得
    conn = connect_db()
    c = conn.cursor()
    c.execute('SELECT * FROM resource_operator')
    rows = c.fetchall()

    # DBのデータを格納
    DB_data = {}
    for row in rows:
        if row[1]:  # データが存在するか確認
            try:
                DB_data[row[0]] = json.loads(row[1])
            except json.JSONDecodeError:
                print(f"Invalid JSON format in database: {row[1]}")
                DB_data[row[0]] = None  # 無効なJSONの場合の処理
        else:
            DB_data[row[0]] = None  # データが空の場合の処理


    if DB_data.get("robot_id"):  # robot_id が存在し、空でない場合
        return_data = {
            "api" : "RegistrationResult",
            "result" : 2,
            "request_id" : received_data.get("request_id", ""),
            "timestamp" : time.time()
        }
        conn.close()
        return jsonify(return_data)
    
    else:
        c.execute('''
            UPDATE resource_operator
            SET robot_id = ?
            WHERE building_id = ? AND resource_id = ?
        ''', (received_data["robot_id"], DB_data.get("building_id"), DB_data.get("resource_id")))
        
        return_data = {
            "api" : "RegistrationResult",
            "result" : 1,
            "request_id" : received_data.get("request_id", ""),
            "timestamp" : time.time()
        }

        conn.commit()
        conn.close()
        return jsonify(return_data)

if __name__ == "__main__":
    app.run(debug=True)

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

# 登録申請エンドポイント
@app.route('/api/resource01/regist', methods=['POST'])
def regist_call():
    # POSTリクエストから送信されたデータを格納
    received_data = request.json

    # DBからデータを取得
    conn = connect_db()
    c = conn.cursor()
    c.execute('SELECT * FROM resource_operator')
    rows = c.fetchall()

    # DBのデータを格納
    DB_data = {}
    for row in rows:
        if row[1]:  # データが存在するか確認
            try:
                DB_data[row[0]] = json.loads(row[1])
            except json.JSONDecodeError:
                print(f"Invalid JSON format in database: {row[1]}")
                DB_data[row[0]] = None  # 無効なJSONの場合の処理
        else:
            DB_data[row[0]] = None  # データが空の場合の処理


    if DB_data.get("robot_id"):  # robot_id が存在し、空でない場合
        return_data = {
            "api" : "RegistrationResult",
            "result" : 2,
            "request_id" : received_data.get("request_id", ""),
            "timestamp" : time.time()
        }
        conn.close()
        return jsonify(return_data)
    
    else:
        c.execute('''
            UPDATE resource_operator
            SET robot_id = ?
            WHERE building_id = ? AND resource_id = ?
        ''', (received_data["robot_id"], DB_data.get("building_id"), DB_data.get("resource_id")))
        
        return_data = {
            "api" : "RegistrationResult",
            "result" : 1,
            "request_id" : received_data.get("request_id", ""),
            "timestamp" : time.time()
        }

        conn.commit()
        conn.close()
        return jsonify(return_data)

if __name__ == "__main__":
    app.run(debug=True)

# 登録解除エンドポイント
@app.route('/api/resource01/release', methods=['POST'])
def regist_call():
    # POSTリクエストから送信されたデータを格納
    received_data = request.json

    # DBからデータを取得
    conn = connect_db()
    c = conn.cursor()
    c.execute('SELECT * FROM resource_operator')
    rows = c.fetchall()

    # DBのデータを格納
    DB_data = {}
    for row in rows:
        if row[1]:  # データが存在するか確認
            try:
                DB_data[row[0]] = json.loads(row[1])
            except json.JSONDecodeError:
                print(f"Invalid JSON format in database: {row[1]}")
                DB_data[row[0]] = None  # 無効なJSONの場合の処理
        else:
            DB_data[row[0]] = None  # データが空の場合の処理


    if DB_data.get("robot_id"):  # robot_id が存在し、空でない場合
        return_data = {
            "api" : "RegistrationResult",
            "result" : 2,
            "request_id" : received_data.get("request_id", ""),
            "timestamp" : time.time()
        }
        conn.close()
        return jsonify(return_data)
    
    else:
        c.execute('''
            UPDATE resource_operator
            SET robot_id = ?
            WHERE building_id = ? AND resource_id = ?
        ''', (received_data["robot_id"], DB_data.get("building_id"), DB_data.get("resource_id")))
        
        return_data = {
            "api" : "RegistrationResult",
            "result" : 1,
            "request_id" : received_data.get("request_id", ""),
            "timestamp" : time.time()
        }

        conn.commit()
        conn.close()
        return jsonify(return_data)

if __name__ == "__main__":
    app.run(debug=True)
