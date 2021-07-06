#!/bin/bash

PORT=5432
FLASK_APP=app
flask run --port "$PORT" --host 0.0.0.0
