#! /usr/bin/bash

# 
cd /app



# Run the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000