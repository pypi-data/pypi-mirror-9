from helper import are_dir_trees_equal
from squadron import initialize
import os
import json

def test_basic(tmpdir):
    tmpdir = str(tmpdir)
    assert initialize.init(tmpdir, None, force=True)

    items = os.listdir(tmpdir)
    assert len(items) > 0

    assert '.git' in items

def test_service(tmpdir):
    tmpdir = str(tmpdir)
    assert initialize.init(tmpdir, None, force=True)
    assert initialize.init_service(tmpdir, 'api', '0.0.1')

    service_dir = os.path.join(tmpdir, 'services', 'api')
    version_dir = os.path.join(service_dir, '0.0.1')
    root_dir = os.path.join(version_dir, 'root')
    test_dir = os.path.join(version_dir, 'tests')

    items = os.listdir(service_dir)

    assert len(items) > 0
    schema_path = os.path.join(version_dir, 'schema')
    schema_handle = open(schema_path, 'r')
    json.load(schema_handle)

    assert os.path.exists(os.path.join(root_dir, 'config.sq'))
    assert os.path.exists(os.path.join(test_dir, 'example.sh'))

def test_environment(tmpdir):
    tmpdir = str(tmpdir)
    assert initialize.init(tmpdir, None, force=True)
    assert initialize.init_service(tmpdir, 'api', '0.0.1')

    assert initialize.init_environment(tmpdir, 'dev', None)

    config_dir = os.path.join(tmpdir, 'config')
    items = os.listdir(config_dir)

    assert len(items) == 1
    assert 'dev' in items

    dev_dir = os.path.join(config_dir, 'dev')
    subitems = os.listdir(dev_dir)

    assert len(subitems) == 1
    assert 'api' in subitems

    # Check that config was put in
    with open(os.path.join(dev_dir, subitems[0])) as jsonfile:
        config = json.loads(jsonfile.read())

    assert 'version' in config
    assert config['version'] == '0.0.1'
    assert config['config'] == {}
    assert 'base_dir' in config

    # Try copy from
    with open(os.path.join(dev_dir, 'fake.json'), 'w') as fd:
        fd.write(json.dumps({'testing':True}))

    assert initialize.init_environment(tmpdir, 'staging', 'dev')

    assert are_dir_trees_equal(dev_dir, os.path.join(config_dir, 'staging'))


