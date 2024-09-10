# resource_management_server

Python package for launching a Flask-based server for running the "Resource Management Server" endpoint compliant with [RFA](https://robot-friendly.org/) Standards.

>[!Note]
Not all functionalities are implemented yet. This is a work in progress.
(e.g. `max_timeout` and `default_timeout` are not handled as is expected in the RFA Standards.)

## Prepare resource configuration

See [sample_resource_config.yaml](config/sample_resource_config.yaml) and create your own file containing a list of resource configuration you want to manage.

## Install

```bash
cd ~/workspace
git clone https://github.com/sbgisen/resource_management_server.git
cd resource_management_server
pip install .
```

## Quick Test

### Launch Server

Launch the Resource Management Server as follows.

```bash
cd ~/workspace/resource_management_server/resource_management_server
export RESOURCE_YAML_PATH=/path/to/resource_config.yaml
flask run --host=0.0.0.0 --port=5000
```

### Get All Resource Information

(Not defined in RFA Standards, but for debug purposes.)

Example Request:

```bash
curl -X GET http://127.0.0.1:5000/api/all_data
```

Example Response:

```json
[{"bldg_id":"Takeshiba","locked_by":"","locked_time":0,"resource_id":"27F_R01"},{"bldg_id":"Takeshiba","locked_by":"","locked_time":0,"resource_id":"27F_R02"}]
```

### Request Resource Registration

Example Request:

```bash
curl -X POST http://127.0.0.1:5000/api/registration -H "Content-Type: application/json" -d '{
  "api": "Registration",
  "robot_id": "cuboid01",
  "bldg_id" : "Takeshiba",
  "resource_id": "27F_R01",
  "timeout" : 0,
  "request_id": "12345",
  "timestamp": 1725962117942
}'
```

Make sure that the unit of time stamp is milliseconds (same goes for other APIs).
Registrations will be automatically deleted after the timeout specified for the target resource (these timeouts should be defined in the config file).

Example Response:

```json
{"api":"RegistrationResult","expiration_time":1725962207942,"max_expiration_time":1725962207942,"request_id":"12345","result":1,"timestamp":1725962123157}
```

### Request Resource Release

Example Request:

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

Example Response:

```json
{"api":"ReleaseResult","request_id":"12345","resource_id":"27F_R01","result":1,"timestamp":1725962697012}
```

### Request Resource Status

Example Request:

```bash
curl -X POST http://127.0.0.1:5000/api/request_resource_status -H "Content-Type: application/json" -d '{
  "api": "RequestResourceStatus",
  "bldg_id" : "Takeshiba",
  "resource_id": "27F_R01",
  "request_id": "12345",
  "timestamp": 1725948482218
}'
```

Example Response:

```json
{"api":"ResourceStatus","expiration_time":0,"max_expiration_time":0,"request_id":"12345","resource_id":"27F_R01","resource_state":0,"result":1,"robot_id":"","timestamp":1725962223906}
```

### Send Robot Status

Example Request:

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

Example Response:

```json
{"api":"RobotStatusResult","request_id":"12345","result":1,"timestamp":1725962547709}
```

>[!Note]
Functions are not fully implemented for this API and data from the request will not be treated unless it's a CANCEL request (registration will be remove in this case).
