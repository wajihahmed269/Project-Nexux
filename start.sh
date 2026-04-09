#!/bin/bash
echo "Starting NEXUS..."
source .env
cd "$(dirname "$0")"
python dashboard/server.py
