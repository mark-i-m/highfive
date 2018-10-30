from copy import deepcopy
import json
from jsonschema import validate
from jsonschema.exceptions import ValidationError
import os
import pytest


CONFIG_SCHEMA = {
    "type": "object",
    "required": [
        "groups",
    ],
    "properties": {
        "contributing" : {
            "type": "string",
        },
        "dirs": {
            "type": "object",
            "properties": {
                "patternProperties": {
                    "^.*$": {
                        "type": "array",
                        "items": {
                            "type": "string",
                        },
                    },
                },
            },
        },
        "expected_branch": {
            "type": "string",
        },
        "groups": {
            "type": "object",
            "required": [
                "all",
            ],
            "patternProperties": {
                "^.*$": {
                    "type": "array",
                    "items": {
                        "type": "string",
                    },
                },
            },
        },
        "mentions": {
            "type": "object",
            "patternProperties": {
                "^.*$": {
                    "type": "object",
                    "required": [
                        "message",
                        "reviewers",
                    ],
                    "properties": {
                        "message": {
                            "type": "string",
                        },
                        "reviewers": {
                            "type": "array",
                            "items": {
                                "type": "string",
                            },
                        },
                    },
                },
            },
        },
        "new_pr_labels": {
            "type": "array",
            "items": {
                "type": "string",
            },
        },
    },
    "additionalProperties": False,
}

# The schema for _global.json does not require "all" in groups.
GLOBAL_SCHEMA = deepcopy(CONFIG_SCHEMA)
del GLOBAL_SCHEMA['properties']['groups']['required']

def config_valid(fname):
    with open(fname, 'r') as fin:
        try:
            config = json.load(fin)
        except ValueError:
            raise ValueError('Cannot parse %s' % fname)

    try:
        validate(
            config,
            GLOBAL_SCHEMA if fname.endswith("_global.json") else CONFIG_SCHEMA
        )
    except ValidationError as e:
        e.message = "In %s: %s" % (fname, e.message)
        raise

    return True

@pytest.mark.config
@pytest.mark.hermetic
def test_configs():
    """Check that the repo config files are valid JSON and contain the expected
    sorts of values."""
    config_path = os.path.join(str(pytest.config.rootdir), 'highfive/configs')
    for fname in os.listdir(config_path):
        if fname.endswith('.json'):
            assert config_valid(os.path.join(config_path, fname))
