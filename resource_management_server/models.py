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
"""ID definition and data model for the resource management server."""

from enum import IntEnum
from typing import Optional

from pydantic import BaseModel
from pydantic import validator


class ResourceType(IntEnum):
    """Type of resource, currently only one type is defined."""
    ALLOW_ONE = 1


class ResourceData(BaseModel):
    """Data model for the resource data."""
    bldg_id: str
    resource_id: str
    resource_type: ResourceType
    max_timeout: int
    default_timeout: int
    locked_by: str = ''
    locked_time: int = 0
    expiration_time: int = 0

    @validator('max_timeout', 'default_timeout')
    def validate_timeouts(cls, value: int) -> int:
        if value <= 0:
            raise ValueError('Timeout values must be positive.')
        return value


class ResultId(IntEnum):
    """IntEnum class for the result field in the response data."""
    SUCCESS = 1
    FAILURE = 2
    OTHERS = 3
    EMERGENCY = 99


class ResourceState(IntEnum):
    """IntEnum class for the resource_state field in the response data."""
    AVAILABLE = 0
    OCCUPIED = 1
    UNKNOWN = 99


class RobotState(IntEnum):
    """IntEnum class for the state field in the request data."""
    ENTERING = 0
    EXITED = 1
    CANCEL = 3
    USING = 6


class RobotStateDetail(IntEnum):
    """IntEnum class for the state_detail field in the request data."""
    NORMAL = 0
    ERROR = 1


class RegistrationPayload(BaseModel):
    """Request data for the registration API."""
    api: str
    robot_id: Optional[str]
    bldg_id: str
    resource_id: str
    timeout: int
    request_id: str = ''
    timestamp: int

    @validator('api')
    def check_api_value(cls: type['RegistrationPayload'], value: str) -> str:
        """Check if the value of the API field is correct."""
        if value != "Registration":
            raise ValueError('api must be "Registration"')
        return value


class RegistrationResultPayload(BaseModel):
    """Response data for the registration API."""
    api: str = "RegistrationResult"
    result: ResultId
    max_expiration_time: int
    expiration_time: int
    request_id: str = ''
    timestamp: int


class RequestResourceStatusPayload(BaseModel):
    """Request data for the resource status API."""
    api: str
    bldg_id: str
    resource_id: str
    request_id: str = ''
    timestamp: int

    @validator('api')
    def check_api_value(cls: type['RequestResourceStatusPayload'], value: str) -> str:
        """Check if the value of the API field is correct."""
        if value != "RequestResourceStatus":
            raise ValueError('api must be "RequestResourceStatus"')
        return value


class ResourceStatusPayload(BaseModel):
    """Response data for the resource status API."""
    api: str = "ResourceStatus"
    result: ResultId
    robot_id: str | None = None
    max_expiration_time: int | None = None
    expiration_time: int | None = None
    resource_id: str
    resource_state: ResourceState
    request_id: str = ''
    timestamp: int


class RobotStatusPayload(BaseModel):
    """Request data for the robot status API."""
    api: str
    robot_id: str
    resource_id: str
    state: RobotState
    state_detail: RobotStateDetail | None = None
    request_id: str = ''
    timestamp: int

    @validator('api')
    def check_api_value(cls: type['RobotStatusPayload'], value: str) -> str:
        """Check if the value of the API field is correct."""
        if value != "RobotStatus":
            raise ValueError('api must be "RobotStatus"')
        return value


class RobotStatusResultPayload(BaseModel):
    """Response data for the robot status API."""
    api: str = "RobotStatusResult"
    result: ResultId
    request_id: str = ''
    timestamp: int


class ReleasePayload(BaseModel):
    """Request data for the release API."""
    api: str
    bldg_id: str
    robot_id: str
    resource_id: str
    request_id: str = ''
    timestamp: int

    @validator('api')
    def check_api_value(cls: type['ReleasePayload'], value: str) -> str:
        """Check if the value of the API field is correct."""
        if value != "Release":
            raise ValueError('api must be "Release"')
        return value


class ReleaseResultPayload(BaseModel):
    """Response data for the release API."""
    api: str = "ReleaseResult"
    result: ResultId
    resource_id: str
    request_id: str = ''
    timestamp: int
