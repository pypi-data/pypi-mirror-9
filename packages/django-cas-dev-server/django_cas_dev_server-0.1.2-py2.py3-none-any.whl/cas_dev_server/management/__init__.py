import base64
import hashlib
import os

from django.conf import settings
from django.utils.encoding import force_bytes
from django.utils.six.moves.urllib.parse import urlencode
import environ

DB_SCHEMES_BY_BACKEND = {backend: scheme for scheme, backend in sorted(environ.Env.DB_SCHEMES.items(), reverse=True)}

def db_url_unparse(db_config):
    url = ''
    if db_config['ENGINE'] in DB_SCHEMES_BY_BACKEND:
        url += DB_SCHEMES_BY_BACKEND[db_config['ENGINE']] + ':'
    url += '//' + (db_config.get('USER') or '')
    if db_config.get('PASSWORD'):
        url += ':' + db_config['PASSWORD']
    if db_config.get('USER') or db_config.get('PASSWORD'):
        url += '@'
    url += db_config.get('HOST') or ''
    if db_config.get('PORT'):
        url += ':' + str(db_config['PORT'])
    url += '/'
    if not (db_config['ENGINE'] == 'ldapdb.backends.ldap' or
            (db_config['ENGINE'] == 'django.db.backends.sqlite3' and db_config.get('NAME') == ':memory:')):
        url += db_config.get('NAME') or ''
    params = dict(db_config.get('OPTIONS', {}),
                  **{option.lower(): db_config[option]
                     for option in environ.Env._DB_BASE_OPTIONS if db_config.get(option)})
    if params:
        url += '?' + urlencode(params)
    return url

def subprocess_environment():
    env = dict(os.environ, DJANGO_SETTINGS_MODULE='cas_dev_server.internal.settings',
               SECRET_KEY=base64.b64encode(hashlib.sha256(force_bytes(settings.SECRET_KEY)).digest()),
               DEBUG=str(settings.DEBUG), TEMPLATE_DEBUG=str(settings.TEMPLATE_DEBUG),
               DATABASE_URL=db_url_unparse(settings.CAS_DEV_DATABASE), LANGUAGE_CODE=settings.LANGUAGE_CODE,
               TIME_ZONE=settings.TIME_ZONE, USE_I18N=str(settings.USE_I18N), USE_L10N=str(settings.USE_L10N),
               USE_TZ=str(settings.USE_TZ))
    if settings.CAS_DEV_DATABASE['ENGINE'] not in DB_SCHEMES_BY_BACKEND:
        env['DATABASE_ENGINE'] = settings.CAS_DEV_DATABASE['ENGINE']
    return env
