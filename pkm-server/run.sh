#!/bin/bash
python -c "
import uvicorn
uvicorn.run('main:app', host='0.0.0.0', port=8890, single_threaded=True)
"
