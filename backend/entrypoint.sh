#!/bin/sh
set -e
# 等待数据库就绪并应用迁移，再启动服务
python manage.py migrate --noinput
exec gunicorn app.wsgi:application --bind 0.0.0.0:8000
