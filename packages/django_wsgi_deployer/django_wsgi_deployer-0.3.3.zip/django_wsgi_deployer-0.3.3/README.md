
django_deployer
===============


Django Projects Deployer. It tries to automate deploying of Django
projects/apps into an existing Apache/WSGI server.

You should prepare your apache httpd to serve WSGI scripts from a
certain directory (default: /var/www/wsgi).  Then you could edit a cfg
file like this:

###### myproject.cfg
    [deploy]
    name = myproject
    src = http://source/of/your/repo/myproject
    scm = svn


Quick Usage
-----------
    # only the first time
    pip install django_deployer
    # where the wsgi scripts are served
    cd /var/www/wsgi
    # edit config (see below)
    vim myproject.cfg
    # deploy
    django_wsgi_deploy myproject
    # reload apache
    systemctl reload httpd


Config keywords
---------------
##### `name`
The Name of the project or application to deploy (*mandatory*)
##### `src`
The URL of the source code of the project (*mandatory*).
##### `scm`
The source code management used (`svn`, `git`, or `hg` for the moment).
_Default_: `'git'`.
##### `scm_clone`
The SCM command to clone (aka: checkout) the source tree.
_Default_: `'clone'`
##### `dst`
Destination directory.
##### `settings`
Settings module name.
_Default_: `name+'_production'`.
##### `url`
Relative URL where the project will be deployed
_Default_: `name`.
##### `build`
Build script used to prepare your project (relative to the projects code base).
_Default_: `'build/build.sh'`.
##### `deploy_requires`
List of python packages needed in deployment.
_Default_: `None`
##### `deploy_commands`
List of django commands to run for deployment (makemigrations, collectstatic,
 etc.).
_Default_: `migrate`
##### `wsgi`
WSGI script name.
_Default_:`'wsgi.py'`
##### `allowed_hosts`
Hosts allowed to run the deployed project.
_Default_: `os.environ['HTTPD_HOST']`
##### `secret_key`
Secret key to use as SECRET_KEY in django settings.
_Default_: Automatically generated on deploy.
##### `media_root`
Where your media files will be stored.
_Default_: `os.path.join(HTTPD_MEDIA_BASE, name),`
##### `static_root`
Where your static files will be collected
_Default_: `os.path.join(HTTPD_STATIC_BASE, name)`
##### `settings_append`
Additional settings that will go into the final `settings` module (tipically DATABASES definition, etc).
_Default_:

     LOGGING = {
      'version': 1,
      'disable_existing_loggers': False,
      'handlers': {
        'file': {
          'level': 'DEBUG',
          'class': 'logging.FileHandler',
          'filename': '/var/tmp/%(name)-wsgi.log',
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


Environment Variables
---------------------

##### `WSGI_BASE_PATH`
Directory were the Django projects will be deployed.
_Default_: `/var/www/wsgi`

##### `HTTPD_CONF_DIR`
Directory were the apache httpd .conf files will be installed.
_Default_: `/etc/httpd/locations.d`

##### `HTTPD_HOST`
Host name under which the Django projects will be
authrized to run (`ALLOWED_HOSTS`settings).
_Default_: Default hostname.

##### `HTTPD_MEDIA_BASE`
Directory under wich the media files will be stored. By default, each
project will create a subdirectory under it.
_Default_: `/var/www/media`

##### `HTTPD_STATIC_BASE`
Directory under wich the static files will be collected. By default, each
project will create a subdirectory under it.
_Default_: `/var/www/static`

##### `SECRET_KEY_GEN`
Command to generate the `SECRET_KEY` in Django settings.
_Default_: `/usr/bin/pwgen -c -n -y 78 1| /usr/bin/tr -d "%"`
