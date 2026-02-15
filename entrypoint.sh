#!/bin/bash
set -e

# 1. PERMISSIONS FIX
# 공식 이미지에서는 보통 불필요하지만, 볼륨 마운트 이슈를 위해 유지합니다.
mkdir -p /opt/airflow/dags /opt/airflow/logs /opt/airflow/plugins
chown -R airflow:0 /opt/airflow/dags /opt/airflow/logs /opt/airflow/plugins
chmod -R 775 /opt/airflow/dags /opt/airflow/logs /opt/airflow/plugins

# 2. AUTOMATED DB UPGRADE
# Airflow 2.x uses 'db upgrade' instead of 'db migrate'
echo "Running database migrations..."
gosu airflow airflow db upgrade

# 3. AUTOMATED ADMIN CREATION
echo "Ensuring Admin user exists..."
# In Airflow 2.x, sync-perm helps initialize FAB roles properly
gosu airflow airflow sync-perm || true

gosu airflow airflow users create \
    --username admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com \
    --password admin || echo "Admin already exists or user creation skipped."

# 4. HAND OFF TO AIRFLOW
echo "Starting Airflow with command: $@"
# This will now correctly receive 'webserver' from docker-compose
exec gosu airflow airflow "$@"