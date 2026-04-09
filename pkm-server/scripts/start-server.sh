#!/bin/bash
cd "$(dirname "$0")/.."
python -m uvicorn main:app --host 0.0.0.0 --port 7890
