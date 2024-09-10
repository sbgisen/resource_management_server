# resource_management_server

Python package for launching a Flask-based server for running the "Resource Management Server" endpoint compliant with RFA Standards.

## Prepare resource configuration

See [sample_resource_config.yaml](config/sample_resource_config.yaml) and create your own file containing a list of resource configuration you want to manage.

## Install

```bash
cd ~/workspace
git clone https://github.com/sbgisen/resource_management_server.git
cd resource_management_server
pip install .
cd scripts
./initialize_db.py /path/to/resource_config.yaml # Initialize the database, database will be located at ~/.resource_management_server dir.
```

Run the `initialize_db.py` script each time you update the resource configuration file.

## Quick Test

### Launch Server

Launch the Resource Management Server as follows.

```bash
cd ~/workspace/resource_management_server/resource_management_server
export FLASK_APP=resource_management_server
flask run --host=0.0.0.0 --port=5000
```

### Get All Resources

(Not defined in RFA Standards, but for debug purposes.)

```bash
curl -X GET http://127.0.0.1:5000/api/all_data
```

### Request Resource Registration

```bash
curl -X POST http://127.0.0.1:5000/api/registration -H "Content-Type: application/json" -d '{
  "api": "Registration",
  "robot_id": "cuboid01",
  "bldg_id" : "Takeshiba",
  "resource_id": "27F_R01",
  "timeout" : 0,
  "request_id": "12345",
  "timestamp": 1725948482218
}'
```

### Request Resource Release

```bash
curl -X POST http://127.0.0.1:5000/api/release -H "Content-Type: application/json" -d '{
  "api": "Release",
  "robot_id": "cuboid01",
  "bldg_id" : "Takeshiba",
  "resource_id": "27F_R01",
  "timeout" : 0,
  "request_id": "12345",
  "timestamp": 1725948482218
}'
```

### Request Resource Status

```bash
curl -X POST http://127.0.0.1:5000/api/request_resource_status -H "Content-Type: application/json" -d '{
  "api": "RequestResourceStatus",
  "bldg_id" : "Takeshiba",
  "resource_id": "27F_R01",
  "request_id": "12345",
  "timestamp": 1725948482218
}'
```

### Send Robot Status

```bash
curl -X POST http://127.0.0.1:5000/api/robot_status -H "Content-Type: application/json" -d '{
  "api": "RobotStatus",
  "robot_id": "cuboid01",
  "bldg_id" : "Takeshiba",
  "resource_id": "27F_R01",
  "state": 0,
  "state_detail": 0,
  "request_id": "12345",
  "timestamp": 1725948482218
}'
```
