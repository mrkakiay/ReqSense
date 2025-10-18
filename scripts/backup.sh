#!/bin/bash
export DATABASE_URL="postgresql://reqsense_user:reqsense_pass@localhost:5432/reqsense"
cd "$(dirname "$0")/.."
python -c "from src.backup import create_backup; create_backup('$DATABASE_URL')"