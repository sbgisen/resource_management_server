from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime
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

# リソース登録エンドポイント
@app.route('/api/regist', methods=['POST'])
def regist_call():
    # POSTリクエストから送信されたデータを格納
    received_data = request.json

    #APIエンドポイントとリクエストAPIの不一致
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
              (received_data["bldg_id"], received_data["resource_id"])) #Resource01はこのままでいいのか
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

#登録解除エンドポイント
@app.route('/api/release', methods=['POST'])
def release_call():
    # POSTリクエストから送信されたデータを格納(api, bldg-id, robot_id, resource_id, request_id, timestamp_id)
    received_data = request.json

    if received_data["api"] != "Release":
        return_data = {
            "api": "RegistrationResult",
            "result": 3,
            "resource_id" : received_data["resource_id"],
            "request_id": received_data["request_id"],
            "timestamp": datetime.now()
        }
        return jsonify(return_data)    

    # DBからデータを取得
    conn = connect_db()
    c = conn.cursor()
    c.execute('SELECT * FROM resource_operator WHERE building_id = ? AND resource_id = ?', 
              (received_data["bldg_id"], received_data[ "resource_id"])) #Resource01はこのままでいいのか
    row = c.fetchone()

    if received_data["robot_id"] == row[3]:  #リクエストしたロボットidと登録済みロボットのidが一致する場合
        # 更新処理
        c.execute('''
            UPDATE resource_operator
            SET robot_id = ?
            WHERE building_id = ? AND resource_id = ?
        ''', ("", received_data["bldg_id"], received_data["resource_id"]))
        
        return_data = {
            "api" : "ReleaseResult",#文言チェック
            "result" : 1,
            "resource_id" : received_data["resource_id"],
            "request_id" : received_data["request_id"],
            "timestamp": datetime.now()
        }

        conn.commit()

    else: #リクエストしたロボットのidと登録済みロボットIDが異なる場合　and　登録済みロボットIDが空の場合 
        return_data = {
            "api" : "ReleaseResult",#文言チェック
            "result" : 2,
            "resource_id" : received_data["resource_id"],
            "request_id" : received_data["request_id"],
            "timestamp": datetime.now()
        }        
       

    conn.close()
    return jsonify(return_data)

if __name__ == "__main__":
    app.run(debug=True)