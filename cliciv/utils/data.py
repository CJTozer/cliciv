import os

import yaml

_DATA_DIR = os.path.join(
    os.path.dirname(__file__),
    '..',
    'data')


def dict_from_data(filename):
    full_path = os.path.join(_DATA_DIR, "{}.yaml".format(filename))
    with open(full_path) as f:
        return yaml.load(f)
