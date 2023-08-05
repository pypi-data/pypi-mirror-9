#!/usr/bin/env python
"""
 Deploy Django Projects into HTTPD Wsgi Container
"""
from __future__ import print_function

import os
import sys
import subprocess
import virtualenv
import re
import platform
import logging

from six.moves.configparser import SafeConfigParser
from lockfile import LockFile


__all__ = ['deploy_django', 'DEFAULT_SETTINGS_APPEND']

logger = logging.getLogger(__name__)

SCM_DEFAULT_CHECKOUT = {
    'svn': 'co',
    'git': 'clone',
    'hg': 'clone',
}

CFG_SECTION = 'deploy'

WSGI_TEMPLATE = """
import os
import sys

_BASE_DIR = os.path.dirname(__file__)

# Add local paths
sys.path.insert(0, _BASE_DIR)
sys.path.insert(1, os.path.join(_BASE_DIR, '%(dst)s'))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "%(settings)s")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
"""

DEFAULT_SETTINGS_APPEND = """
LOGGING = {
  'version': 1,
  'disable_existing_loggers': False,
  'handlers': {
    'file': {
      'level': 'DEBUG',
      'class': 'logging.FileHandler',
      'filename': '/var/tmp/%(name)s-wsgi.log',
    },
  },
  'loggers': {
    '': {
      'handlers': ['file'],
      'level': 'WARNING',
      'propagate': True,
    }
  }
}
"""

DJANGO_SETTINGS_TEMPLATE = """
from %(name)s.settings import *

DEBUG=False
TEMPLATE_DEBUG=DEBUG

ALLOWED_HOSTS = ['%(allowed_hosts)s']
SECRET_KEY='%(secret_key)s'

MEDIA_ROOT='%(media_root)s'
STATIC_ROOT='%(static_root)s'

%(settings_append)s

"""

HTTPD_CONF_TEMPLATE = """
WSGIDaemonProcess %(name)s processes=1 threads=4 display-name=%%{GROUP} python-path=%(site_libs)s umask=002
<Directory %(proj_base)s>
WSGIProcessGroup %(name)s
</Directory>
WSGIScriptAlias %(url)s %(proj_base)s/%(wsgi)s
"""

WSGI_PYTHON_PATH = u'^%s.*site-packages$'

def parse_list(value):
    """
    Parse a string as a list of CSVs.
    It always returns a list of string
    s"""
    return re.split(r', *', value)

def deploy_django(proj):
    """
    Deploy a Django project
    """

    wsgi_base_path = os.environ.get('WSGI_BASE_PATH',
                                    '/var/www/wsgi')
    httpd_conf_dir = os.environ.get('HTTPD_CONF_DIR',
                                    '/etc/httpd/locations.d')
    httpd_host = os.environ.get('HTTPD_HOST',
                                platform.node())
    httpd_media_base = os.environ.get('HTTPD_MEDIA_BASE',
                                      '/var/www/html/media')
    httpd_static_base = os.environ.get('HTTPD_STATIC_BASE',
                                       '/var/www/html/static')
    secret_key_gen = os.environ.get('SECRET_KEY_GEN',
                                    '/usr/bin/pwgen -c -n -y 78 1')

    proj_base = os.path.join(wsgi_base_path, proj)
    path = lambda p: os.path.join(proj_base, p)


    proj_defaults = {
        'name': proj,
        'proj_base': proj_base,
        'dst': '%(name)s-project',
        'settings': '%(name)s_production',
        'url': '/%(name)s',
        'build': 'build/build.sh',
        'wsgi': 'wsgi.py',
        'allowed_hosts': httpd_host,
        'secret_key': subprocess.check_output(secret_key_gen.split()
                                          ).strip().replace("'", "-"),
        'media_root': os.path.join(httpd_media_base, proj),
        'static_root': os.path.join(httpd_static_base, proj),
        'scm': '/usr/bin/git',
        'settings_append': DEFAULT_SETTINGS_APPEND,
        'deploy_requires': None,
        'deploy_commands': ['migrate']
    }

    # Protect '%' from interpolation
    proj_defaults['secret_key'] = re.sub(r'%', r'',
                                        proj_defaults['secret_key'])
    # Choose clone command
    proj_defaults['scm_clone'] = SCM_DEFAULT_CHECKOUT[os.path.split(
        proj_defaults['scm'])[-1]]

    # Load defaults
    cfg = SafeConfigParser(proj_defaults)

    # Force read
    cfg.readfp(open(proj+'.cfg', 'r'))

    #logger.debug('Final configuration:')
    #for k,v in cfg.items(CFG_SECTION):
    #    logger.debug('\t%s: %s', k, v)

    # Create directory
    os.mkdir(proj_base)

    # Virtualenv
    virtualenv.create_environment(proj_base)

    # Checkout
    subprocess.check_call([
        cfg.get(CFG_SECTION, 'scm'),
        cfg.get(CFG_SECTION, 'scm_clone'),
        cfg.get(CFG_SECTION, 'src'),
        path(cfg.get(CFG_SECTION, 'dst')),
    ])

    # Build
    activate = path('bin/activate')
    build = os.path.join(
        cfg.get(CFG_SECTION, 'dst'),
        cfg.get(CFG_SECTION, 'build')
    )
    subprocess.check_call([build],
                          cwd=proj_base,
                          env={'BASH_ENV': activate})

    # Install Deploy Requiremts
    deploy_requires = cfg.get(CFG_SECTION, 'deploy_requires')
    if deploy_requires:
        logger.debug('Installing: %s', deploy_requires)
        cmd = [os.path.join(virtualenv.path_locations(proj_base)[-1],
                            'pip')
               , 'install']
        cmd.extend(parse_list(deploy_requires))
        subprocess.check_call(cmd)

    # Create settings
    settings_file = path(cfg.get(CFG_SECTION, 'settings'))+'.py'
    slock = LockFile(settings_file)
    slock.acquire()

    if os.path.exists(settings_file):
        slock.release()
        raise IOError([17, 'File exists'])
    try:
        sfp = open(settings_file, 'w')
        print(DJANGO_SETTINGS_TEMPLATE % dict(cfg.items(CFG_SECTION)),
              file=sfp)
        sfp.close()
    finally:
        slock.release()

    # Create wsgi script
    wsgi_file = path(cfg.get(CFG_SECTION, 'wsgi'))
    slock = LockFile(wsgi_file)
    slock.acquire()

    if os.path.exists(wsgi_file):
        slock.release()
        raise IOError([17, 'File exists'])
    try:
        wfp = open(wsgi_file, 'w')
        print(WSGI_TEMPLATE % dict(cfg.items(CFG_SECTION)),
              file=wfp)
        wfp.close()
    finally:
        slock.release()

    # Create apache conf
    conf_file = os.path.join(httpd_conf_dir,
                             cfg.get(CFG_SECTION, 'name'))+'.conf'
    slock = LockFile(conf_file)
    slock.acquire()

    if os.path.exists(conf_file):
        slock.release()
        raise IOError([17, 'File exists'])
    try:
        sfp = open(conf_file, 'w')
        conf = dict(cfg.items(CFG_SECTION))
        conf['site_libs'] = os.path.join(
            virtualenv.path_locations(proj_base)[1],
            'site-packages')
        http_conf = HTTPD_CONF_TEMPLATE % conf
        print(http_conf,
              file=sfp)
        sfp.close()
    finally:
        slock.release()


    # Perform django commands
    deploy_commands = cfg.get(CFG_SECTION, 'deploy_commands')
    if deploy_commands:
        manage = [os.path.join(virtualenv.path_locations(proj_base)[-1],
                               virtualenv.expected_exe)
                  , 'manage.py']
        os.chdir(path(cfg.get(CFG_SECTION, 'dst')))
        # Deployment django environment
        dep_env = os.environ.copy()
        dep_env['DJANGO_SETTINGS_MODULE'] = cfg.get(CFG_SECTION, 'settings')
        dep_env['PYTHONPATH'] = path('.')
        logger.debug('Environment for commands: PYTHONPATH=%s',
                     dep_env['PYTHONPATH'])
        logger.debug('  Django settings: %s', dep_env['DJANGO_SETTINGS_MODULE'])
        for cmd in parse_list(deploy_commands):
            logger.debug("Executing '%s'", ' '.join(manage+[cmd]))
            subprocess.check_call(manage+cmd.split(), env=dep_env)

    # That's it. Remember to reload apache
    print('You should reload apache:\n', '\t', 'systemctl reload httpd')
    return True
