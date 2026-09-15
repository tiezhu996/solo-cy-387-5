import os
import sys
import tempfile
import uuid
from pathlib import Path
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'dev-secret')
DEBUG = os.getenv('DJANGO_DEBUG', 'true') == 'true'
ALLOWED_HOSTS = ['*']
LANGUAGE_CODE = 'zh-hans'
USE_TZ = True

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'rest_framework',
    'app.apps.users',
    'app.apps.properties',
    'app.apps.booking',
    'app.apps.contract',
    'app.apps.repair',
    'app.apps.packages',
]

MIDDLEWARE = ['django.middleware.common.CommonMiddleware', 'app.middleware.request_log.RequestLogMiddleware']
ROOT_URLCONF = 'app.urls'
DATABASES = {'default': dj_database_url.config(default=os.getenv('DATABASE_URL', 'sqlite:///db.sqlite3'))}
# SQLite 并发写入时等待写锁而非立即报错（PostgreSQL 由行锁串行化，无需此项）
if DATABASES['default'].get('ENGINE', '').endswith('sqlite3'):
    DATABASES['default'].setdefault('OPTIONS', {})['timeout'] = 20

# 测试库按进程隔离：多个 `manage.py test` 进程并发运行时各自使用独立的库名，
# 结束后由 Django 测试运行器自动删除（SQLite 删文件 / PostgreSQL 删测试库）。
# 名称在进程内保持稳定（建库与销毁用同一名称），跨进程通过 PID + 随机后缀保证唯一。
if 'test' in sys.argv or os.getenv('RENTFIND_TEST') == '1':
    _isolation_suffix = f'{os.getpid()}_{uuid.uuid4().hex[:8]}'
    _test_cfg = DATABASES['default'].setdefault('TEST', {})
    if DATABASES['default'].get('ENGINE', '').endswith('sqlite3'):
        _test_cfg['NAME'] = os.path.join(
            tempfile.gettempdir(), f'rentfind_test_{_isolation_suffix}.sqlite3'
        )
    else:
        _db_name = DATABASES['default'].get('NAME', 'rentfind')
        _test_cfg.setdefault('NAME', f'test_{_db_name}_{_isolation_suffix}')
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
MEDIA_ROOT = BASE_DIR / 'media'
MEDIA_URL = '/media/'
REST_FRAMEWORK = {'EXCEPTION_HANDLER': 'app.utils.exception_handler.standard_exception_handler'}
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {'console': {'class': 'logging.StreamHandler'}},
    'root': {'handlers': ['console'], 'level': 'INFO'},
}
