from . import schema, verify, apply
import os, platform
import pytest
import jsonschema

root = {
    'name': 'sys',
    'gid': 3
}

test_group = {
    'name':'testgroup1234',
}

def test_schema():
    jsonschema.validate(root, schema())
    jsonschema.validate(test_group, schema())

def test_verify():
    result = verify([root, test_group])
    assert len(result) == 1
    assert result[0] == test_group

