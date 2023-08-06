import os
import sys
import re
import tempfile
from collections import defaultdict

from fabric.api import (
    env,
    local,
    put as _put,
    require,
    #run as _run,
    run,
    settings,
    sudo,
    cd,
    task,
    runs_once,
    execute,
)

from fabric.contrib import files
from fabric.tasks import Task

from burlap import common
from burlap.common import (
    run_or_dryrun,
    sudo_or_dryrun,
)
from burlap.common import (
    run,
    put,
    SITE,
    ROLE,
    find_template,
    QueuedCommand,
)
from burlap import versioner

env.pip_build_directory = '/tmp/pip-build-root/pip'
env.pip_check_permissions = True
env.pip_user = 'www-data'
env.pip_group = 'www-data'
env.pip_chmod = '775'
env.pip_python_version = 2.7
env.pip_virtual_env_dir_template = '%(remote_app_dir)s/.env'
env.pip_virtual_env_dir = '.env'
env.pip_virtual_env_exe = sudo
env.pip_requirements_fn = 'pip-requirements.txt'
env.pip_use_virt = True
env.pip_build_dir = '/tmp/pip-build'
env.pip_path = 'pip%(pip_python_version)s'
env.pip_update_command = '%(pip_path_versioned)s install --use-mirrors --timeout=120 --no-install %(pip_no_deps)s --build %(pip_build_dir)s --download %(pip_cache_dir)s --exists-action w %(pip_package)s'
#env.pip_install_command = 'cd %(pip_virtual_env_dir)s; . %(pip_virtual_env_dir)s/bin/activate; pip install --upgrade --timeout=60 "%(pip_package)s"; deactivate'
env.pip_remote_cache_dir = '/tmp/pip_cache'
env.pip_local_cache_dir_template = './.pip_cache/%(ROLE)s'
env.pip_upgrade = ''
env.pip_install_command = ". %(pip_virtual_env_dir)s/bin/activate; %(pip_path_versioned)s install %(pip_no_deps)s %(pip_upgrade_flag)s --build %(pip_build_dir)s --find-links file://%(pip_cache_dir)s --no-index %(pip_package)s; deactivate"
env.pip_uninstall_command = ". %(pip_virtual_env_dir)s/bin/activate; %(pip_path_versioned)s uninstall %(pip_package)s; deactivate"

INSTALLED = 'installed'
PENDING = 'pending'

PIP = 'PIP'

common.required_system_packages[PIP] = {
    common.FEDORA: [
        #'python-pip'#obsolete?
    ],
    (common.UBUNTU, '12.04'): [
        #'python-pip',#obsolete in 14.04?
        #'python-virtualenv',#obsolete in 14.04?
        'gcc', 'python-dev', 'build-essential'
    ],
    (common.UBUNTU, '14.04'): [
        #'python-pip',#obsolete in 14.04?
        #'python-virtualenv',#obsolete in 14.04?
        'gcc', 'python-dev', 'build-essential'
    ],
}

def render_paths():
    from burlap.dj import render_remote_paths
    env.pip_path_versioned = env.pip_path % env
    render_remote_paths()
    if env.pip_virtual_env_dir_template:
        env.pip_virtual_env_dir = env.pip_virtual_env_dir_template % env
    if env.is_local:
        env.pip_virtual_env_dir = os.path.abspath(env.pip_virtual_env_dir)

def clean_virtualenv():
    render_paths()
    with settings(warn_only=True):
        print 'Deleting old virtual environment...'
        sudo('rm -Rf %(pip_virtual_env_dir)s' % env)
    assert not files.exists(env.pip_virtual_env_dir), \
        'Unable to delete pre-existing environment.'

@task
def bootstrap(dryrun=0):
    """
    Installs all the necessary packages necessary for managing virtual
    environments with pip.
    """
    env.pip_path_versioned = env.pip_path % env
    run_or_dryrun('wget http://peak.telecommunity.com/dist/ez_setup.py -O /tmp/ez_setup.py', dryrun=dryrun)
    #sudo_or_dryrun('python{pip_python_version} /tmp/ez_setup.py -U setuptools'.format(**env), dryrun=dryrun)
    with settings(warn_only=True):
        sudo_or_dryrun('python{pip_python_version} /tmp/ez_setup.py -U setuptools'.format(**env), dryrun=dryrun)
    sudo_or_dryrun('easy_install -U pip', dryrun=dryrun)
    sudo_or_dryrun('{pip_path_versioned} install --upgrade setuptools'.format(**env), dryrun=dryrun)
    sudo_or_dryrun('{pip_path_versioned} install --upgrade distribute'.format(**env), dryrun=dryrun)
    sudo_or_dryrun('{pip_path_versioned} install --upgrade virtualenv'.format(**env), dryrun=dryrun)

@task
def init(clean=0, check_global=0):
    """
    Creates the virtual environment.
    """
    assert env[ROLE]
    
    render_paths()
    
    # Delete any pre-existing environment.
    if int(clean):
        clean_virtualenv()
    
    # Important. Default Ubuntu 12.04 package uses Pip 1.0, which
    # is horribly buggy. Should use 1.3 or later.
    if int(check_global):
        print 'Ensuring the global pip install is up-to-date.'
        sudo('pip install --upgrade pip')
    
    print env.pip_virtual_env_dir
    #if not files.exists(env.pip_virtual_env_dir):
    print 'Creating new virtual environment...'
    with settings(warn_only=True):
        cmd = 'virtualenv --no-site-packages %(pip_virtual_env_dir)s' % env
        if env.is_local:
            run(cmd)
        else:
            sudo(cmd)
        
    if not env.is_local and env.pip_check_permissions:
        sudo('chown -R %(pip_user)s:%(pip_group)s %(remote_app_dir)s' % env)
        sudo('chmod -R %(pip_chmod)s %(remote_app_dir)s' % env)

def iter_pip_requirements():
    for line in open(find_template(env.pip_requirements_fn)):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        yield line.split('#')[0]

def get_desired_package_versions(preserve_order=False):
    versions_lst = []
    versions = {}
    for line in open(find_template(env.pip_requirements_fn)).read().split('\n'):
        line = line or ''
        if '#' in line:
            line = line.split('#')[0].strip()
        if not line.strip() or line.startswith('#'):
            continue
        #print line
        matches = re.findall('([a-zA-Z0-9\-_]+)[\=\<\>]{2}(.*)', line)
        if matches:
            if matches[0][0] not in versions_lst:
                versions_lst.append((matches[0][0], (matches[0][1], line)))
            versions[matches[0][0]] = (matches[0][1], line)
        else:
            matches = re.findall('([a-zA-Z0-9\-]+)\-([0-9\.]+)(?:$|\.)', line)
            if matches:
                if matches[0][0] not in versions_lst:
                    versions_lst.append((matches[0][0], (matches[0][1], line)))
                versions[matches[0][0]] = (matches[0][1], line)
            else:
                if line not in versions_lst:
                    versions_lst.append((line, ('current', line)))
                versions[line] = ('current', line)
    if preserve_order:
        return versions_lst
    return versions

@task
@runs_once
def check_report():
    """
    Runs check() on all hosts and reports the results.
    """
    execute(check)

    #report here
    todo
    pass

GITHUB_TO_PIP_NAME_PATTERN = re.compile('^.*github.com/[^/]+/(?P<name>[^/]+)/[^/]+/(?P<tag>[^/]+)/?')

@task
def check_for_updates():
    """
    Determines which packages have a newer version available.
    """
    stale_lines = []
    lines = list(iter_pip_requirements())
    total = len(lines)
    i = 0
    for line in lines:
        i += 1
        print '\rChecking requirement %i of %i...' % (i, total),
        sys.stdout.flush()
        #if i > 5:break#TODO:remove
        
        # Extract the dependency data from the pip-requirements.txt line.
        # e.g.
        #type,name,uri,version,rss_field,rss_regex
        #pip,Django,Django,1.4,,
        parts = line.split('==')
        if len(parts) == 2:
            dep_type = versioner.PIP
            name = uri = parts[0].strip()
            version = parts[1].strip()
#            print 'name:',name
#            print 'version: "%s"' % version
        elif 'github' in line.lower():
            dep_type = versioner.GITHUB_TAG
            matches = GITHUB_TO_PIP_NAME_PATTERN.findall(line)
            assert matches, 'No github tag matches for line: %s' % line
            name = matches[0][0]
            uri = line
            tag_name = matches[0][1].strip()
            version = tag_name.replace(name, '')[1:].strip()
            if version.endswith('.zip'):
                version = version.replace('.zip', '')
            if version.endswith('.tar.gz'):
                version = version.replace('.tar.gz', '')
#            print
#            print 'name:',name
#            print 'uri:',uri
#            print 'tag_name:',tag_name
#            print 'version: "%s"' % version
        else:
            raise NotImplementedError, 'Unhandled line: %s' % line
        
        # Create the dependency.
        dep = versioner.Dependency(
            type=dep_type,
            name=name,
            uri=uri,
            version=version,
            rss_field=None,
            rss_regex=None,
        )
#        if dep_type == versioner.GITHUB_TAG:
#            print 'current version:',dep.get_current_version()
#            raw_input('enter')
        try:
            if dep.is_stale():
                stale_lines.append(dep)
        except Exception, e:
            print
            print 'Error checking line %s: %s' % (line, e)
            raise
            
    print
    print '='*80
    if stale_lines:
        print 'The following packages have updated versions available:'
        spaced_lines = []
        max_lengths = defaultdict(int)
        for dep in sorted(stale_lines, key=lambda _:_.name):
            dep_name = dep.name
            dep_current_version = dep.get_current_version()
            dep_installed_version = dep.version
            max_lengths['package'] = max(max_lengths['package'], len(dep_name))
            max_lengths['most_recent_version'] = max(max_lengths['most_recent_version'], len(str(dep_current_version)))
            max_lengths['installed_version'] = max(max_lengths['installed_version'], len(str(dep_installed_version)))
            spaced_lines.append((dep_name, dep_installed_version, dep_current_version))
        
        delimiter = ', '
        columns = ['package', 'installed_version', 'most_recent_version']
        for column in columns:
            max_lengths[column] = max(max_lengths[column], len(column))
        print ''.join((_+('' if i+1==len(columns) else delimiter)).ljust(max_lengths[_]+2) for i,_ in enumerate(columns))
        for dep in sorted(spaced_lines):
            last = i+1 == len(columns)
            line_data = dict(zip(columns, dep))
            print ''.join((line_data[_]+('' if i+1==len(columns) else delimiter)).ljust(max_lengths[_]+2) for i,_ in enumerate(columns))
    print '-'*80
    print '%i packages have updates' % (len(stale_lines),)

@task
def validate_requirements():
    """
    Ensures all package dependencies are included in our pip-requirements.txt
    file and that they're in the appropriate order.
    """
    todo

@task
def check(return_type=PENDING):
    """
    Lists the packages that are missing or obsolete on the target.
    
    return_type := pending|installed
    """
    from burlap.plan import get_original
    run0 = get_original('run')
    import inspect
    print 'run0:',run0, inspect.getsourcefile(run0)
    
    assert env[ROLE]
    
    env.pip_path_versioned = env.pip_path % env
    init()
    
    def get_version_nums(v):
        if re.findall('^[0-9\.]+$', v):
            return tuple(int(_) for _ in v.split('.') if _.strip().isdigit())
    
    use_virt = env.pip_use_virt
    if use_virt:
        cmd_template = ". %(pip_virtual_env_dir)s/bin/activate; %(pip_path_versioned)s freeze; deactivate"
    else:
        cmd_template = "%(pip_path_versioned)s freeze"
    cmd = cmd_template % env
    result = run0(cmd)
    installed_package_versions = {}
    for line in result.split('\n'):
        line = line.strip()
        if '#' in line:
            line = line.split('#')[0].strip()
        if not line:
            continue
        elif line.startswith('#'):
            continue
        elif ' ' in line:
            continue
        k, v = line.split('==')
        if not k.strip() or not v.strip():
            continue
        print 'Installed:',k,v
        installed_package_versions[k.strip()] = v.strip()
        
    desired_package_version = get_desired_package_versions()
    for k,v in desired_package_version.iteritems():
        print 'Desired:',k,v
    
    pending = [] # (package_line, type)]
    
    not_installed = {}
    for k, (v, line) in desired_package_version.iteritems():
        if k not in installed_package_versions:
            not_installed[k] = (v, line)
            
    if not_installed:
        print '!'*80
        print 'Not installed:'
        for k,(v,line) in sorted(not_installed.iteritems(), key=lambda o:o[0]):
            print k,v
            pending.append((line,'install'))
    else:
        print '-'*80
        print 'All are installed.'
    
    obsolete = {}
    for k,(v,line) in desired_package_version.iteritems():
        #line
        if v != 'current' and v != installed_package_versions.get(k,v):
            obsolete[k] = (v, line)
    if obsolete:
        print '!'*80
        print 'Obsolete:'
        for k,(v0,line) in sorted(obsolete.iteritems(), key=lambda o:o[0]):
            v0nums = get_version_nums(v0) or v0
            v1 = installed_package_versions[k]
            v1nums = get_version_nums(v1) or v1
            #print 'v1nums > v0nums:',v1nums, v0nums
            installed_is_newer = v1nums > v0nums
            newer_str = ''
            if installed_is_newer:
                newer_str = ', this is newer!!! Update pip-requirements.txt???'
            print k,v0,'(Installed is %s%s)' % (v1, newer_str)
            pending.append((line,'update'))
    else:
        print '-'*80
        print 'None are obsolete.'
    
    if return_type == INSTALLED:
        return installed_package_versions
    return pending

@task
def update(package='', ignore_errors=0, no_deps=0, all=0, mirrors=1, dryrun=0):
    """
    Updates the local cache of pip packages.
    
    If all=1, skips check of host and simply updates everything.
    """
    dryrun = int(dryrun)
    assert env[ROLE]
    ignore_errors = int(ignore_errors)
    env.pip_path_versioned = env.pip_path % env
    env.pip_local_cache_dir = env.pip_local_cache_dir_template % env
    env.pip_cache_dir = env.pip_local_cache_dir
    if not os.path.isdir(env.pip_cache_dir):
        os.makedirs(env.pip_cache_dir)
    env.pip_package = (package or '').strip()
    env.pip_no_deps = '--no-deps' if int(no_deps) else ''
    env.pip_build_dir = tempfile.mkdtemp()
    
    # Clear build directory in case it wasn't properly cleaned up previously.
    cmd = 'rm -Rf %(pip_build_directory)s' % env
    if env.is_local:
        run(cmd)
    else:
        sudo(cmd)
    
    with settings(warn_only=ignore_errors):
        if package:
            # Download a single specific package.
            cmd = env.pip_update_command % env
            if not int(mirrors):
                cmd = cmd.replace('--use-mirrors', '')
            local(cmd)
        else:
            # Download each package in a requirements file.
            # Note, specifying the requirements file in the command isn't properly
            # supported by pip, thus we have to parse the file itself and send each
            # to pip separately.
            
            if int(all):
                packages = list(iter_pip_requirements())
            else:
                packages = [k for k,v in check()]
            
            for package in packages:
                env.pip_package = package.strip()
                
                cmd = env.pip_update_command % env
                if not int(mirrors):
                    cmd = cmd.replace('--use-mirrors', '')
                    
                local(cmd)

@task
def upgrade_pip():
    from burlap.dj import render_remote_paths
    render_remote_paths()
    if env.pip_virtual_env_dir_template:
        env.pip_virtual_env_dir = env.pip_virtual_env_dir_template % env
    run(". %(pip_virtual_env_dir)s/bin/activate; pip install --upgrade setuptools" % env)
    run(". %(pip_virtual_env_dir)s/bin/activate; pip install --upgrade distribute" % env)

@task
def uninstall(package):
    from burlap.dj import render_remote_paths
    
    render_remote_paths()
    if env.pip_virtual_env_dir_template:
        env.pip_virtual_env_dir = env.pip_virtual_env_dir_template % env
    
    env.pip_local_cache_dir = env.pip_local_cache_dir_template % env
    
    env.pip_package = package
    if env.is_local:
        run(env.pip_uninstall_command % env)
    else:
        sudo(env.pip_uninstall_command % env)
    
@task
def install(package='', clean=0, no_deps=1, all=0, upgrade=1, dryrun=0):
    """
    Installs the local cache of pip packages.
    """
    from burlap.dj import render_remote_paths
    print 'Installing pip requirements...'
    assert env[ROLE]
    dryrun = int(dryrun)
    require('is_local')
    
    # Delete any pre-existing environment.
    if int(clean):
        clean_virtualenv()
    
    render_remote_paths()
    if env.pip_virtual_env_dir_template:
        env.pip_virtual_env_dir = env.pip_virtual_env_dir_template % env
    
    env.pip_local_cache_dir = env.pip_local_cache_dir_template % env
    
    env.pip_path_versioned = env.pip_path % env
    if env.is_local:
        env.pip_cache_dir = os.path.abspath(env.pip_local_cache_dir % env)
    else:
        env.pip_cache_dir = env.pip_remote_cache_dir % env
        print 'env.host_string:',env.host_string
        print 'env.key_filename:',env.key_filename
        run('mkdir -p %(pip_cache_dir)s' % env)
        
        if not env.pip_cache_dir.endswith('/'):
            env.pip_cache_dir = env.pip_cache_dir + '/'
        
        env.pip_key_filename = os.path.abspath(env.key_filename)
        local('rsync -avz --progress --rsh "ssh -o StrictHostKeyChecking=no -i %(pip_key_filename)s" %(pip_local_cache_dir)s/* %(user)s@%(host_string)s:%(pip_cache_dir)s' % env)
    
    env.pip_upgrade_flag = ''
    if int(upgrade):
        env.pip_upgrade_flag = ' -U '
    
    env.pip_no_deps = ''
    if int(no_deps):
        env.pip_no_deps = '--no-deps'
    
    if int(all):
        packages = list(iter_pip_requirements())
    elif package:
        packages = [package]
    else:
        packages = [k for k,v in check()]
    
    env.pip_build_dir = tempfile.mkdtemp()
    for package in packages:
        env.pip_package = package
        if env.is_local:
            run(env.pip_install_command % env)
        else:
            sudo(env.pip_install_command % env)

    if not env.is_local:
        sudo('chown -R %(pip_user)s:%(pip_group)s %(remote_app_dir)s' % env)
        sudo('chmod -R %(pip_chmod)s %(remote_app_dir)s' % env)

@task
def record_manifest():
    """
    Called after a deployment to record any data necessary to detect changes
    for a future deployment.
    """
    # Not really necessary, because pre-deployment, we'll just retrieve this
    # list again, but it's nice to have a separate record to detect
    # non-deployment changes to installed packages.
    #data = check(return_type=INSTALLED)
    
    desired = get_desired_package_versions(preserve_order=True)
    data = [[_n, _v, _raw] for _n, (_v, _raw) in desired]
    
    return data

def compare_manifest(data=None):
    """
    Called before a deployment, given the data returned by record_manifest(),
    for determining what, if any, tasks need to be run to make the target
    server reflect the current settings within the current context.
    """
#    pending = check(return_type=PENDING)
#    if pending:
#        return [update, install]

    pre = ['package', 'user']
    update_methods = []
    install_methods = []
    uninstall_methods = []
    old = data or []
    
    old_packages = set(tuple(_) for _ in old)
    old_package_names = set(tuple(_[0]) for _ in old)
    
    new_packages_ordered = get_desired_package_versions(preserve_order=True)
    new_packages = set((_n, _v, _raw) for _n, (_v, _raw) in new_packages_ordered)
    new_package_names = set(_n for _n, (_v, _raw) in new_packages_ordered)
    
    #print 'new_package_names:',new_package_names
    
    added = [_ for _ in new_packages if _ not in old_packages]
    #print 'added:',added
    for _name, _version, _line in added:
        update_methods.append(QueuedCommand('pip.update', kwargs=dict(package=_line), pre=pre))
        install_methods.append(QueuedCommand('pip.install', kwargs=dict(package=_line), pre=pre))
    
    removed = [(_name, _version, _line) for _name, _version, _line in old_packages if _name not in new_package_names]
    #print 'removed:',removed
    for _name, _version, _line in removed:
        uninstall_methods.append(QueuedCommand('pip.uninstall', kwargs=dict(package=_line), pre=pre))
    
    return update_methods + uninstall_methods + install_methods

common.manifest_recorder[PIP] = record_manifest
common.manifest_comparer[PIP] = compare_manifest
