#!/usr/bin/env bash
set -e

echo "Waiting for PostgreSQL database..."

python << 'EOF'
import os
import sys
import time
import psycopg2

db_name = os.environ.get("DB_NAME", "unity_game")
db_user = os.environ.get("DB_USER", "unity_user")
db_password = os.environ.get("DB_PASSWORD", "unity_password")
db_host = os.environ.get("DB_HOST", "db")
db_port = os.environ.get("DB_PORT", "5432")

max_attempts = 30
attempts = 0

while attempts < max_attempts:
    try:
        conn = psycopg2.connect(
            dbname=db_name,
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port,
            connect_timeout=2
        )
        conn.close()
        print("PostgreSQL is ready!")
        sys.exit(0)
    except Exception as e:
        attempts += 1
        print(f"PostgreSQL not ready yet ({attempts}/{max_attempts}): {e}")
        time.sleep(1)

print("Failed to connect to PostgreSQL in time.")
sys.exit(1)
EOF

echo "Applying database migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput --clear || true

echo "Ensuring default superuser exists..."
python << 'EOF'
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.users.models import User

su_username = os.environ.get("DJANGO_SUPERUSER_USERNAME", "admin")
su_password = os.environ.get("DJANGO_SUPERUSER_PASSWORD", "admin123456")
su_email = os.environ.get("DJANGO_SUPERUSER_EMAIL", "admin@game.local")

if not User.objects.filter(username=su_username).exists():
    User.objects.create_superuser(
        username=su_username,
        email=su_email,
        password=su_password
    )
    print(f"Superuser '{su_username}' successfully created!")
else:
    print(f"Superuser '{su_username}' already exists.")
EOF

echo "Starting server..."
exec "$@"
