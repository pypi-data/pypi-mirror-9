import os
import sys
import datetime
import hashlib

from fabric.api import (
    env,
    require,
    settings,
    cd,
    task,
)
from fabric.contrib import files

from burlap.common import (
    QueuedCommand,
    local_or_dryrun,
    run_or_dryrun,
    sudo_or_dryrun,
    put_or_dryrun,
)
from burlap import common
from burlap.decorators import task_or_dryrun

env.tarball_gzip = True
env.tarball_exclusions = [
    '*_local.py',
    '*.pyc',
    '*.svn',
    '*.tar.gz',
    #'static',
]
env.tarball_dir = '.tarball_cache'
env.tarball_extra_dirs = []

TARBALL = 'TARBALL'

def get_tarball_path():
    env.tarball_gzip_flag = ''
    env.tarball_ext = 'tar'
    if env.tarball_gzip:
        env.tarball_gzip_flag = '--gzip'
        env.tarball_ext = 'tgz'
    if not os.path.isdir(env.tarball_dir):
        os.makedirs(env.tarball_dir)
    env.absolute_src_dir = os.path.abspath(env.src_dir)
    env.tarball_path = os.path.abspath('%(tarball_dir)s/code-%(ROLE)s-%(SITE)s-%(host_string)s.%(tarball_ext)s' % env)
    return env.tarball_path

@task_or_dryrun
def create(gzip=1):
    """
    Generates a tarball of all deployable code.
    """
    
    assert env.SITE, 'Site unspecified.'
    assert env.ROLE, 'Role unspecified.'
    env.tarball_gzip = bool(int(gzip))
    get_tarball_path()
    print 'Creating tarball...'
    env.tarball_exclusions_str = ' '.join(
        "--exclude='%s'" % _ for _ in env.tarball_exclusions)
    cmd = ("cd %(absolute_src_dir)s; " \
        "tar %(tarball_exclusions_str)s --exclude-vcs %(tarball_gzip_flag)s " \
        "--create --verbose --dereference --file %(tarball_path)s *") % env
    local_or_dryrun(cmd)

@task_or_dryrun
def deploy(clean=0):
    """
    Copies the tarball to the target server.
    
    Note, clean=1 will delete any dynamically generated files not included
    in the tarball.
    """
    
    tarball_path = get_tarball_path()
    assert os.path.isfile(tarball_path), \
        'No tarball found. Ensure you ran create() first.'
    put_or_dryrun(local_path=env.tarball_path)
    
    env.remote_app_dir = env.remote_app_dir_template % env
    env.remote_app_src_dir = env.remote_app_src_dir_template % env
    env.remote_app_src_package_dir = env.remote_app_src_package_dir_template % env
    
    if int(clean):
        print 'Deleting old remote source...'
        #sudo('[ -d %(remote_app_src_dir)s ] && rm -Rf  %(remote_app_src_dir)s' % env)
        sudo_or_dryrun('rm -Rf  %(remote_app_src_dir)s' % env)
        sudo_or_dryrun('mkdir -p %(remote_app_src_dir)s' % env)
    
    print 'Extracting tarball...'
    sudo_or_dryrun('mkdir -p %(remote_app_src_dir)s' % env)
    sudo_or_dryrun('tar -xvzf %(put_remote_path)s -C %(remote_app_src_dir)s' % env)
    
    for path in env.tarball_extra_dirs:
        env.tarball_extra_dir_path = path % env
        if path.startswith('/'):
            sudo_or_dryrun('mkdir -p %(tarball_extra_dir_path)s' % env)
        else:
            sudo_or_dryrun('mkdir -p %(remote_app_dir)s/%(tarball_extra_dir_path)s' % env)
    
    # Mark executables.
    print 'Marking source files as executable...'
    sudo_or_dryrun('chmod +x %(remote_app_src_package_dir)s/*' % env)
    sudo_or_dryrun('chmod -R %(apache_chmod)s %(remote_app_src_package_dir)s' % env)
    sudo_or_dryrun('chown -R %(apache_user)s:%(apache_group)s %(remote_app_dir)s' % env)

@task_or_dryrun
def get_tarball_hash(fn=None, refresh=1, verbose=0):
    """
    Calculates the hash for the tarball.
    """
    get_tarball_path()
    fn = fn or env.tarball_path
    if int(refresh):
        create()
    # Note, gzip is almost deterministic, but it includes a timestamp in the
    # first few bytes so we strip that off before taking the hash.
    tarball_hash = hashlib.sha512(open(fn).read()[8:]).hexdigest()
    if int(verbose):
        print fn
        print tarball_hash
    return tarball_hash

@task_or_dryrun
def record_manifest():
    """
    Called after a deployment to record any data necessary to detect changes
    for a future deployment.
    """
    
    # Record tarball hash.
    data = {'tarball_hash': get_tarball_hash()}
    
    return data

def compare_manifest(data=None):
    """
    Called before a deployment, given the data returned by record_manifest(),
    for determining what, if any, tasks need to be run to make the target
    server reflect the current settings within the current context.
    """
    data = data or {}
    pre = ['user', 'package', 'pip']
    new_hash = get_tarball_hash()
#    print 'old:',data.get('tarball_hash')
#    print 'new:',new_hash
    if data.get('tarball_hash') != new_hash:
        return [
            QueuedCommand('tarball.create', pre=pre),
            QueuedCommand('tarball.deploy', pre=pre),
        ]

common.manifest_recorder[TARBALL] = record_manifest
common.manifest_comparer[TARBALL] = compare_manifest
