import os
import json
import jsonschema
import template
import subprocess
from git import *
from fileio.dirio import makedirsp
from fileio.gotoroot import *
import shutil
from pkg_resources import parse_version
from log import log

default_schema = { "$schema": "http://json-schema.org/draft-04/schema#", "type": "object", "properties": {}}

def _test_for_git():
    try:
        return Git('.').version()
    except OSError:
        return False
    except:
        return True

def init(squadron_dir, gitrepo, force=False, example=False):
    if os.path.exists(squadron_dir):
        # Check if it's empty-ish
        if len(os.listdir(squadron_dir)) > 0 and not force:
            if gitrepo is not None:
                # Grab the gitrepo name out and use that
                repo_name = gitrepo[gitrepo.rstrip('/').rfind('/'):].lstrip('/')
                if repo_name.endswith('.git'):
                    repo_name = repo_name[:-4]

                squadron_dir = os.path.join(squadron_dir, repo_name)
            else:
                log.error("Directory [" + squadron_dir + "] already exists and isn't empty.")
                log.error("Please provide a new directory or use -f.")
                return False

    try:
        if gitrepo is None:
            log.info("Creating Squadron config in {}".format(squadron_dir))
            makedirsp(squadron_dir)
            makedirsp(os.path.join(squadron_dir, 'config'))
            makedirsp(os.path.join(squadron_dir, 'libraries'))
            makedirsp(os.path.join(squadron_dir, 'nodes'))
            makedirsp(os.path.join(squadron_dir, 'resources'))
            makedirsp(os.path.join(squadron_dir, 'services'))
            repo = Repo.init(squadron_dir) # initialize repo
        else:
            log.info("Cloning Squadron config from {}".format(gitrepo))
            repo = Repo.clone_from(gitrepo, squadron_dir)
    except OSError:
        if not _test_for_git():
            log.error("Looks like git isn't installed! Install git to continue")
            return False
        else:
            raise

    log.info("Squadron has been initialized")
    if example is False:
        log.info("Now, you can initialize your service:")
        if squadron_dir != os.getcwd():
            log.info("\tcd %s", squadron_dir)
        log.info("\tsquadron init --service service_name")
    else:
        init_service(squadron_dir, 'example')
        log.info("We have init an example service for you, please check out services/example")

    return True



def create_json(path, to_write={}):
    with open(path, 'w+') as jsonfile:
        jsonfile.write(json.dumps(to_write, sort_keys=True, indent=4))

@go_to_root
def init_service(squadron_dir, service_name, service_ver):
    """ Initializes a service with the given name and version """
    service_dir = os.path.join(squadron_dir, 'services', service_name,
                    service_ver)

    rootdir = os.path.join(service_dir, 'root')
    makedirsp(rootdir)
    # rootdir shouldn't be empty
    with open(os.path.join(rootdir, 'config.sq'), 'w') as rfile:
        pass

    testdir = os.path.join(service_dir, 'tests')
    makedirsp(testdir)
    # testdir shouldn't be empty
    with open(os.path.join(testdir, 'example.sh'), 'w') as tfile:
        tfile.write("""#!/bin/bash
while read line; do
    echo $line
done
""")

    # Create the base files
    create_json(os.path.join(service_dir, 'actions'))
    create_json(os.path.join(service_dir, 'defaults'))

    # copy and react's top level are arrays
    create_json(os.path.join(service_dir, 'copy'), [])
    create_json(os.path.join(service_dir, 'react'), [])

    create_json(os.path.join(service_dir, 'schema'), default_schema)
    create_json(os.path.join(service_dir, 'state'), [])

    log.info("Initialized service {} version {}".format(service_name,
            service_ver))

    return True

def _get_latest_service_versions(service_dir):
    """
    Takes the service directory, and returns a map of service to
    latest version.

    Keyword arguments:
        service_dir
    """
    services = [ d for d in os.listdir(service_dir)
                if os.path.isdir(os.path.join(service_dir, d)) ]
    result = {}
    for s in services:
        max_version = None
        for d in os.listdir(os.path.join(service_dir, s)):
            if max_version is None or parse_version(d) > parse_version(max_version):
                max_version = d
        
        if max_version:
            result[s] = max_version
    return result

@go_to_root
def init_environment(squadron_dir, environment_name, copy_from):
    """ Initializes an environment """
    config_dir = os.path.join(squadron_dir, 'config')

    new_env = os.path.join(config_dir, environment_name)

    if copy_from:
        src = os.path.join(config_dir, copy_from)
        shutil.copytree(src, new_env)
    else:
        makedirsp(new_env)
        service_dir = os.path.join(squadron_dir, 'services')
        # Grab all the directories
        to_make = _get_latest_service_versions(service_dir)

        for service_name, service_version in to_make.items():
            create_json(os.path.join(new_env, service_name),
                    {'version': service_version, 'config':{},
                     'base_dir': 'TODO'})

    log.info("Initialized environment {}{}".format(environment_name,
            " copied from " + copy_from if copy_from else ""))
    return True

