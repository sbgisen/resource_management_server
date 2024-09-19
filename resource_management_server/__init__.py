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
"""Create a Flask application for the resource management server."""

from flask import Flask

from .database import initialize_db
from .database import start_timeout_check
from .routes import register_routes


def create_app() -> Flask:
    """Create a Flask application.

    Returns:
        Flask: The created Flask application.
    """
    app = Flask(__name__)
    print('Initializing database...')
    initialize_db()
    print('Database initialized.')
    register_routes(app)
    start_timeout_check()
    return app
