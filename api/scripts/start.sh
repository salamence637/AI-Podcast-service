#! /usr/bin/bash

# 
cd /app



# Run the server
# fastapi dev --host 0.0.0.0 --port 8000
# uvicorn app.main:app --host 0.0.0.0 --port 8000
uvicorn main:app --host 0.0.0.0 --port 80 --log-level debug

