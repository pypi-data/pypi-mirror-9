# coding: utf-8
from __future__ import with_statement
import codecs
import json
import os
import platform
import subprocess
import sys

from fabric.api import *
from fabric.colors import *
from fabric.utils import abort
from fabric.contrib.console import confirm

# Examples of Usage
# fab -f fabfile_heroku.py --list
# fab --list
# fab localhost bootstrap
# fab localhost info
# fab localhost test
# fab localhost start_server
# fab production/staging bootstrap_heroku
# fab production/staging upload_static_files
# fab production/staging set_env_vars
# fab production/staging deploy
# fab production/staging rollback
# fab production/staging logs
# fab production/staging ssh
# fab localhost/production/staging ping
# fab localhost/production/staging warmup
# fab localhost/production/staging benchmark
# fab localhost/production/staging browse


# Environments

@task
def localhost():
    common()
    read_config_file('_localhost.json')
    env.heroku_app_git_remote = None
    env.heroku_worker_git_remote = None
    env.heroku_deploy_branch = None
    env.aws_bucket = 'codeart-localhost'
    print(blue("Localhost"))

@task
def staging():
    common()
    if current_git_branch() != 'staging':
        if not confirm('Using staging environment without staging branch (%s). Are you sure?' % current_git_branch()):
            abort('cancelled by the user')
    env.venv = 'envstaging'
    read_config_file('_staging.json')
    env.heroku_app_git_remote = 'heroku-staging'
    env.heroku_worker_git_remote = 'heroku-worker-staging'
    env.heroku_deploy_branch = 'staging:master'
    env.aws_bucket = env.heroku_app
    print(blue("Staging"))

@task
def production():
    common()
    if current_git_branch() != 'master':
        if not confirm('Using production environment without master branch (%s). Are you sure?' % current_git_branch()):
            abort('cancelled by the user')
    read_config_file('_production.json')
    env.heroku_app_git_remote = 'heroku'
    env.heroku_worker_git_remote = 'heroku-worker'
    env.heroku_deploy_branch = 'master'
    env.aws_bucket = env.heroku_app
    print(blue("Production"))

def common():
    env.python = 'python2.7'
    env.url = 'http://localhost:8000'
    env.host = 'localhost'
    env.port = 8000
    env.heroku_app = None
    env.heroku_app_addons = []
    env.heroku_worker = None
    env.heroku_worker_addons = []
    env.heroku_cedar = None
    env.paths = []

    env.run = local
    env.sudo = local
    env.cd = lcd
    env.venv = 'env'


# Utilities

def read_config_file(filename):
    """
    Example of the file localhost.json:
    {
        "ami": "123",
        "hosts": ["a.com", "b.com"]
    }
    """
    if os.path.exists(filename):
        with codecs.open(filename, 'r', 'utf-8') as f:
           data = json.loads(f.read())
           print(data)
           env.update(data)

def current_git_branch():
    label = subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD'])
    return label.strip()

def isMac():
    return platform.system().lower() == 'darwin'

def isLinux():
    return platform.system().lower() == 'linux'

def venv():
    return 'source %(env)s/bin/activate' % dict(env=env.venv)

def python(command):
    return 'python %(command)s' % dict(command=command)

def manage(command):
    return 'python manage.py %(command)s' % dict(command=command)

def install(packages):
    packages = ' '.join(packages)
    if isMac():
        env.run('brew install %(packages)s' % dict(packages=packages))
    elif isLinux():
        env.sudo('apt-get install -y %(package)s' % dict(package=packages))

def bootstrap_heroku(app_name, addons, branch=None, domain=None, cedar=None):
    print(red("Configuring heroku"))
    env.run('heroku apps:create %s' % app_name)
    if branch:
        env.run('git remote add %s git@heroku.com:%s.git' % (branch, app_name))
    if cedar:
        env.run('heroku stack:set %s --app %s' % (cedar, app_name))
    for addon in addons:
        env.run('heroku addons:add %s --app %s' % (addon, app_name))
        if addon == 'newrelic':
            newrelic_key = env.run('heroku config:get NEW_RELIC_LICENSE_KEY --app %s' % (app_name), capture=True)
            env.run('newrelic-admin generate-config %s newrelic.ini' % newrelic_key)
    if domain and not domain.endswith('herokuapp.com'):
        env.run('heroku domains:add %s --app %s' % (domain, app_name))
    print(green("Bootstrap success"))

def get_bucket_policy(bucket, host):
    policy = """
    {
      "Version":"2012-10-17",
      "Id":"http referer policy example",
      "Statement":[
        {
          "Sid":"Allow get requests originated from www.example.com and example.com",
          "Effect":"Allow",
          "Principal":"*",
          "Action":"s3:GetObject",
          "Resource":"arn:aws:s3:::%s/*",
          "Condition":{
            "StringLike":{"aws:Referer":["http://www.%s/*","http://%s/*","https://www.%s/*","https://%s/*"]}
          }
        }
      ]
    }""" % (bucket, host, host, host, host)
    return policy.strip()

def get_or_create_bucket(name, public=True, cors=None):
    import boto
    from boto.s3.cors import CORSConfiguration
    conn = boto.connect_s3() # read AWS env vars
    bucket = conn.lookup(name)
    if bucket is None:
        print('Creating bucket %s' % name)
        bucket = conn.create_bucket(name)
        if public:
            bucket.set_acl('public-read')
        if cors:
            cors_cfg = CORSConfiguration()
            cors_cfg.add_rule(['GET', 'POST'], 'http://*', allowed_header='*', max_age_seconds=604800)
            cors_cfg.add_rule(['GET', 'POST'], 'https://*', allowed_header='*', max_age_seconds=604800)
            cors_cfg.add_rule('GET', '*', allowed_header='*', max_age_seconds=604800)
            bucket.set_cors(cors_cfg)
            bucket.set_policy(get_bucket_policy(name, cors), headers=None)
    return bucket

def upload_file_to_s3(bucket_name, filename, public=True, static_headers=False, gzip=False):
    bucket = get_or_create_bucket(bucket_name, cors=True)
    print('Uploading %s to Amazon S3 bucket %s' % (filename, bucket_name))
    k = bucket.new_key(filename)
    if static_headers:
        content_types = {
            '.gz': 'application/x-gzip',
            '.js': 'application/x-javascript',
            '.map': 'application/json',
            '.json': 'application/json',
            '.css': 'text/css',
            '.html': 'text/html',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.gif': 'image/gif',
            '.png': 'image/png',
            '.pdf': 'application/pdf',
        }
        dir_filename, extension = os.path.splitext(filename)
        k.set_metadata('Content-Type', content_types.get(extension, 'text/plain'))
        k.set_metadata('Cache-Control', 'max-age=31536000')
        k.set_metadata('Expires', 'Thu, 31 Dec 2015 23:59:59 GM')
        if gzip:
            k.set_metadata('Content-Encoding', 'gzip')
    def percent_cb(complete, total):
        sys.stdout.write('.')
        sys.stdout.flush()
    k.set_contents_from_filename(filename, cb=percent_cb, num_cb=10)
    if public:
        k.set_acl('public-read')

def minify_js(jsfile):
    if jsfile.endswith('.js'):
        # env.run('sudo npm install uglify-js -g')
        dir_filename, extension = os.path.splitext(jsfile)
        fmin = dir_filename + '.min' + extension
        fmap = dir_filename + '.min' + extension + '.map'
        env.run('uglifyjs %s -o %s --source-map %s -p relative -c' % (jsfile, fmin, fmap))
        return fmin, fmap
    return jsfile, jsfile

def compress(textfile):
    env.run('gzip -k -f -9 %s' % textfile)
    dir_filename, extension = os.path.splitext(textfile)
    gzipped_file = '%s.gz%s' % (dir_filename, extension)
    env.run('mv %s.gz %s' % (textfile, gzipped_file))
    return gzipped_file

def upload_js(bucket_name, filename, minify=True, gzip=True):
    if minify:
        fmin, fmap = minify_js(filename)
        upload_file_to_s3(bucket_name, fmin, public=True, static_headers=True, gzip=False)
        upload_file_to_s3(bucket_name, fmap, public=True, static_headers=True, gzip=False)
        if gzip:
            upload_file_to_s3(bucket_name, compress(fmin), public=True, static_headers=True, gzip=True)
            upload_file_to_s3(bucket_name, compress(fmap), public=True, static_headers=True, gzip=True)
    if gzip:
        upload_file_to_s3(bucket_name, compress(filename), public=True, static_headers=True, gzip=True)
    upload_file_to_s3(bucket_name, filename, public=True, static_headers=True, gzip=False)

def upload_css(bucket_name, filename, gzip=True):
    if gzip:
        filename_gz = compress(filename)
        upload_file_to_s3(bucket_name, filename_gz, public=True, static_headers=True, gzip=True)
    upload_file_to_s3(bucket_name, filename, public=True, static_headers=True, gzip=False)

def upload_file(bucket_name, filename):
    if filename.endswith('.js'):
        upload_js(bucket_name, filename)
    elif filename.endswith('.css'):
        upload_css(bucket_name, filename)
    elif filename.endswith('.jpg') or filename.endswith('.jpeg') or filename.endswith('.gif') or filename.endswith('.png'):
        upload_file_to_s3(bucket_name, filename, public=True, static_headers=True, gzip=False)
    else:
        upload_file_to_s3(bucket_name, filename, public=True, static_headers=False, gzip=False)

def weighttp(requests=10000, concurrency=50, threads=5):
    # http://adventuresincoding.com/2012/05/how-to-get-apachebenchab-to-work-on-mac-os-x-lion
    # install('Weighttp')
    for path in env.paths:
        env.run('weighttp -n %s -c %s -t %s -k %s%s' % (requests, concurrency, threads, env.url, path))

# Tasks Localhost

@task
def bootstrap():
    print(red("Configuring application"))
    env.run('virtualenv %(env)s -p %(python)s' % dict(env=env.venv, python=env.python))
    with prefix(venv()):
        env.run('pip install -r requirements.txt')
        start_server()
    print(green("Bootstrap success"))

@task
def info():
    env.run('uname -a')
    env.run('ulimit -aH')
    with prefix(venv()):
        env.run(python('--version'))
    if env.heroku_app:
        env.run('heroku config --app %s' % env.heroku_app)
    if env.heroku_worker:
        env.run('heroku config --app %s' % env.heroku_worker)

@task
def test():
    with prefix(venv()):
        env.run(vrun('tox'))

@task
def start_server():
    with prefix(venv()):
        # env.run('foreman start -p %s' % env.port)
        env.run('python app.py')

# Tasks Production/Staging

@task
def bootstrap_heroku():
    if env.heroku_app:
        bootstrap_heroku(env.heroku_app, env.heroku_app_addons,
            branch=env.heroku_app_git_remote, domain=env.host, cedar=env.heroku_cedar)
    if env.heroku_worker:
        bootstrap_heroku(env.heroku_worker, env.heroku_worker_addons,
            branch=env.heroku_app_git_remote, domain=env.host, cedar=env.heroku_cedar)

@task
def upload_static_files():
    print(red("Uploading static files to S3"))
    folder = 'static'
    for (current_dir, dirs, files) in os.walk(folder):
        for filename in files:
            block = ['.gz', '.min', '.map']
            skip = False
            for b in block:
                if b in filename:
                    skip = True
                    break
            if not skip:
                path = os.path.join(current_dir, filename)
                upload_file(env.aws_bucket, path)
    print(red("Uploaded succesful"))

@task
def set_env_vars():
    def vars_line(data):
        return ' '.join(['%s=%s' % (var, value) for var, value in data.items()])
    env_vars = dict(
        AWS_ACCESS_KEY_ID=os.getenv('AWS_ACCESS_KEY_ID', '').strip(),
        AWS_SECRET_ACCESS_KEY=os.getenv('AWS_SECRET_ACCESS_KEY', '').strip(),
        AWS_REGION=os.getenv('AWS_REGION', '').strip(),
    )
    shared_vars = dict(REDISTOGO_URL='', REDIS_URL='', MONGOHQ_URL='', MONGOLAB_URI='', DATABASE_URL='')
    if env.heroku_app:
        env.run('heroku config:set %(vars)s --app %(app)s' % dict(vars=vars_line(env_vars), app=env.heroku_app))
        for var, _ in shared_vars.items():
            value = env.run('heroku config:get %(var)s --app %(app)s' % dict(var=var, app=env.heroku_app), capture=True)
            shared_vars[var] = value

    if env.heroku_worker:
        env.run('heroku config:set %(vars)s --app %(app)s' % dict(vars=vars_line(env_vars), app=env.heroku_worker))
        env.run('heroku config:set %(vars)s --app %(app)s' % dict(vars=vars_line(shared_vars), app=env.heroku_worker))

@task
def deploy(tag=None):
    print(red("Deploying"))
    with prefix(venv()):
        upload_static_files()

    if env.heroku_app:
        set_env_vars()
        env.run('git push %s %s' % (env.heroku_app_git_remote, env.heroku_deploy_branch))
        env.run('heroku ps:scale web=1 --app %s' % env.heroku_app)
        if env.heroku_worker:
            env.run('heroku ps:scale worker=0 --app %s' % env.heroku_app)

    if env.heroku_worker:
        env.run('git push %s %s' % (env.heroku_worker_git_remote, env.heroku_deploy_branch))
        if env.heroku_app:
            env.run('heroku ps:scale web=0 --app %s' % env.heroku_worker)
        env.run('heroku ps:scale worker=1 --app %s' % env.heroku_worker)

    warmup()
    print(green("Deploy success"))

@task
def rollback(tag=None, worker=False):
    app = env.heroku_worker if worker else env.heroku_app
    env.run('heroku releases --app %s' % app)
    if not confirm('Rollback (tag %s). Are you sure?' % tag):
        abort('cancelled by the user')
    if tag:
        env.run('heroku rollback --app %s' % app)
    else:
        env.run('heroku rollback %s --app %s' % (tag, app))

@task
def logs(worker=False):
    app = env.heroku_app if not worker else env.heroku_worker
    env.run('heroku logs -n 100 --app %s' % app)
    env.run('heroku logs --tail --app %s' % app)

@task
def ssh(worker=False):
    if env.heroku_worker or worker:
        env.run('heroku run python --app %s' % env.heroku_worker)
    else:
        env.run('heroku run python --app %s' % env.heroku_app)

# Tasks Localhost/Production/Staging

@task
def ping(time=3):
    env.run('ping -c %(time)s %(host)s:%(port)s' % dict(time=time, host=env.host, port=env.port))

@task
def warmup():
    weighttp(requests=5000, concurrency=10)

@task
def benchmark():
    weighttp(requests=10000, concurrency=50)

@task
def browse():
    env.run('open %s' % env.url)
