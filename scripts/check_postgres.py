#!/usr/bin/env python3
"""Simple helper to verify PostgreSQL connectivity using DATABASE_URL from backend/.env"""
import os
from sqlalchemy import create_engine
from sqlalchemy import text
from dotenv import load_dotenv
from pathlib import Path

# Load backend/.env
backend_env = Path(__file__).resolve().parents[1] / 'backend' / '.env'
if backend_env.exists():
    load_dotenv(backend_env)

DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    raise SystemExit('ERROR: DATABASE_URL not set in backend/.env')

# SQLAlchemy needs postgresql+psycopg2://
if DATABASE_URL.startswith('postgresql://') or DATABASE_URL.startswith('postgres://'):
    # Leave as-is; SQLAlchemy will accept the prefix used in app config (it performs replacement there)
    pass

print(f'Testing DB connection to: {DATABASE_URL}')
try:
    engine = create_engine(DATABASE_URL, connect_args={})
    with engine.connect() as conn:
        result = conn.execute(text('SELECT 1'))
        print('DB connection OK - SELECT 1 returned:', result.scalar())
except Exception as e:
    print('DB connection FAILED:', str(e))
    raise SystemExit(1)

print('Success')
