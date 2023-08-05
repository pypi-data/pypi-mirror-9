import environ

env = environ.Env()

SECRET_KEY = env('SECRET_KEY')

DEBUG = env('DEBUG', bool)
TEMPLATE_DEBUG = env('TEMPLATE_DEBUG', bool)

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'mama_cas',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'cas_dev_server.internal.urls'

WSGI_APPLICATION = 'cas_dev_server.internal.wsgi.application'

DATABASES = {'default': env.db(engine=env('DATABASE_ENGINE', str, None))}

LANGUAGE_CODE = env('LANGUAGE_CODE', str)
TIME_ZONE = env('TIME_ZONE', str)

USE_I18N = env('USE_I18N', bool)
USE_L10N = env('USE_L10N', bool)
USE_TZ = env('USE_TZ', bool)

STATIC_URL = '/static/'
