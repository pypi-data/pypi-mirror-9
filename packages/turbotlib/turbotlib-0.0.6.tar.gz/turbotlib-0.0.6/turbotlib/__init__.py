from __future__ import print_function

import os
import sys
import yaml

# We are running in production if MORPH_URL is set in the environment.
in_production = bool(os.getenv('MORPH_URL'))


def data_dir():
    if in_production:
        data_dir = '/data'
    else:
        data_dir = 'data'
        _set_up_data_dir(data_dir)
    return data_dir

def _vars_path():
    return data_dir() + '/_vars.yml'

def log(message):
    print(message, file=sys.stderr)


def save_var(key, val):
    vars = _get_vars()
    vars[key] = val
    _save_vars(vars)


def get_var(key):
    try:
        return _get_vars()[key]
    except KeyError:
        raise KeyError('No such var: ' + key)


def _save_vars(vars):
    with open(_vars_path(), 'w') as f:
        f.write(yaml.dump(vars))


def _get_vars():
    try:
        with open(_vars_path()) as f:
            return yaml.load(f)
    except IOError:
        return {}

def _set_up_data_dir(d):
    try:
        os.mkdir(d)
    except OSError:
        pass

os.environ["SCRAPERWIKI_DATABASE_NAME"] = "sqlite:///%s/data.sqlite" % data_dir()
