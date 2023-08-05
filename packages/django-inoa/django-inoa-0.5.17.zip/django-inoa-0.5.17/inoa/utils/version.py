# -*- coding: utf-8 -*-
import os.path
from django.conf import settings
from django.core.cache import cache
from django.utils.version import get_version as get_django_version
from threading import Thread
import dateutil.parser
import subprocess
import time


UPDATE_CACHE_KEY = 'SYSTEM_IS_UPDATING'
INFO_CACHE_KEY = 'PROCESS_VERSION_INFO'
INFO_CACHE_TIMEOUT = 60 * 60 * 24  # 1 day


def get_release_version():
    try:
        module_name = getattr(settings, 'RELEASE_VERSION_MODULE_NAME', None)
        if not module_name:
            return None
        module = __import__(module_name, fromlist='__version__')
        return getattr(module, '__version__', None)
    except:
        return None


def get_version_info():
    info = cache.get(INFO_CACHE_KEY)

    if info is None:
        try:
            info = {}
            info['django'] = get_django_version()
            info['release'] = get_release_version()
            
            log_file_path = os.path.join(settings.PROJECT_DIR, 'version_log.txt')
            branch_file_path = os.path.join(settings.PROJECT_DIR, 'version_branch.txt')
            if os.path.isfile(log_file_path):
                with open(log_file_path, 'r') as log_file:
                    log_str = log_file.read()
            else:
                log_str = subprocess.check_output(['git', 'log', 'HEAD', '-1', '--format=%h%n%an%n%ai%n%s'],
                                                  cwd=settings.PROJECT_DIR)
            log_components = log_str.split("\n")
            info['hash'] = log_components[0]
            info['author'] = log_components[1]
            info['datetime'] = dateutil.parser.parse(log_components[2])
            info['log'] = log_components[3]
            info['branch'] = None
            info['branches'] = []
            if os.path.isfile(branch_file_path):
                with open(branch_file_path, 'r') as branch_file:
                    info['branch'] = branch_file.read()
            else:
                for branch in subprocess.check_output(['git', 'branch', '--list', '--all'],
                                                      cwd=settings.PROJECT_DIR).split("\n"):
                    branch = branch.strip()
                    if not branch:
                        continue
                    active_branch = branch[0] == '*'
                    detached_branch = "detached from" in branch
                    branch = branch.strip('* ()')
                    if branch[0:14] == "detached from ":
                        branch = branch[14:]
                    if branch[0:8] == "remotes/":
                        branch = branch[8:]
                    if active_branch:
                        info['branch'] = branch
                    if not detached_branch:
                        info['branches'].append(branch)
        except:
            info = {}
        cache.set(INFO_CACHE_KEY, info, INFO_CACHE_TIMEOUT)

    return info


def is_updating():
    return bool(cache.get(UPDATE_CACHE_KEY))


def can_update(user):
    return getattr(settings, 'SELF_UPDATE_ENABLE', False) and user.is_superuser


def update(user, branch=None):
    if is_updating() or not can_update(user):
        return False
    cache.set(UPDATE_CACHE_KEY, True)
    Thread(target=delayed_update, args=(branch,)).start()
    return True


def delayed_update(branch=None):
    branch = branch or 'origin/master'
    time.sleep(3)
    try:
        command = [settings.SELF_UPDATE_SCRIPT_PATH, settings.SELF_UPDATE_ENV_ACTIVATE_PATH,
                   settings.SELF_UPDATE_APACHE_SERVICE, branch]
        if settings.SELF_UPDATE_SCRIPT_PARAMS:
            command += settings.SELF_UPDATE_SCRIPT_PARAMS.split()
        log_stdout = open(settings.SELF_UPDATE_LOG_STDOUT, 'w', buffering=0)
        log_stderr = open(settings.SELF_UPDATE_LOG_STDERR, 'w', buffering=0)
        subprocess.call(command, stdout=log_stdout, stderr=log_stderr)
    except:
        pass
    cache.delete(UPDATE_CACHE_KEY)
