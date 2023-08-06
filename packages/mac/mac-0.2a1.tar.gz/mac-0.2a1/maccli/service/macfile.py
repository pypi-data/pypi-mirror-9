import time
import datetime

import yaml
import yaml.representer

from maccli.helper.unsortable import ordered_load
import maccli
from maccli.helper.unsortable import UnsortableOrderedDict


""" Yaml file format
description: Manageacloud CLI
version: 0.1a6
timestamp: '2015-02-05 11:59:07'
roles:
  default:
    instance create:
      branch: master
      configuration: basic_ubuntu_1404
      deployment: testing
      environment:
      - DBNAME: pgbench
      - PGUSER: benchuser
      hardware: https://www.googleapis.com/compute/v1/projects/soy-sound-613/zones/asia-east1-a/machineTypes/f1-micro
      location: asia-east1-a
      name: localtesting
      provider: gce
      release: any
"""


def convert_args_to_yaml(args):
    key = ""
    if args.cmd is not None and args.subcmd is not None:
        key = args.cmd + ' ' + args.subcmd
    elif args.cmd is not None:
        key = args.cmd

    attributes = filter(
        lambda a: not a.startswith('_') and a not in ["cmd", "subcmd", "yaml", "debug"], dir(args))

    # defines the parameter that must exist, even if empty
    empty_parameters = ['name']

    params_instance = UnsortableOrderedDict()
    params_infrastructure = UnsortableOrderedDict()
    for attr in attributes:
        if attr in empty_parameters:
            value = ""
        else:
            value = getattr(args, attr)

        if value is not None:
            if attr in ['hardware', 'location', 'provider', 'deployment', 'lifespan', 'name', 'release']:
                params_infrastructure[attr] = value
            else:
                params_instance[attr] = value

    # default roles, what tier can be created
    params_role = UnsortableOrderedDict()
    params_role[key] = params_instance
    role_name = "default"
    roles = UnsortableOrderedDict()
    roles["default"] = params_role

    # default infrastructures, create one
    params_infrastructure['role'] = role_name
    params_infrastructure['amount'] = 1
    infrastructures = UnsortableOrderedDict()
    infrastructures["default"] = params_infrastructure

    # general structure
    data = UnsortableOrderedDict()
    data["mac"] = maccli.__version__
    data["description"] = "Manageacloud CLI"
    data["name"] = "manageacloud.com"
    data["version"] = "1.0"
    data["roles"] = roles
    data["infrastructures"] = infrastructures

    yaml.add_representer(UnsortableOrderedDict, yaml.representer.SafeRepresenter.represent_dict)
    print yaml.dump(data, default_flow_style=False)

    exit(0)


def validate_param(actual, expected, optional=None):
    unexpected = is_unexpected(actual, expected)
    if optional is not None:
        unexpected_optional = is_unexpected(unexpected, optional)
    else:
        unexpected_optional = unexpected

    if len(unexpected_optional):
        print "Incorrect file format. The following parameters are unexpected:"
        for p in unexpected_optional:
            print " - %s" % p
        exit(1)

    notpresent = is_present(actual, expected)
    if optional is not None:
        notpresent_optional = is_unexpected(notpresent, optional)
    else:
        notpresent_optional = notpresent

    if len(notpresent_optional):
        print "Incorrect file format. The following parameters are needed and not present:"
        for p in notpresent_optional:
            print " - %s" % p
        exit(2)


def is_present(actual, expected):
    """ evaluates if all params in actual exist in expected  """
    return filter(lambda x: x not in actual, expected)


def is_unexpected(actual, expected):
    """ evaluates if there is a parameter in actual that does not exist in expected  """
    return filter(lambda x: x not in expected, actual)


def load_macfile(path):
    stram = open(path, "r")
    raw = ordered_load(stram, yaml.SafeLoader)

    # validate root
    root_params = ['mac', 'version', 'name',  'description', 'roles', 'infrastructures']
    raw_root_keys = raw.keys()
    validate_param(raw_root_keys, root_params)

    # validate roles
    expected_roles = []
    role_root_params = ["instance create"]
    role_params = ['branch', 'configuration']
    role_optional_params = ['hd', 'lifespan', 'environment']
    raw_role_root_keys = raw['roles'].keys()
    for key_role_root in raw_role_root_keys:
        expected_roles.append(key_role_root)
        raw_role_keys = raw['roles'][key_role_root].keys()
        validate_param(raw_role_keys, role_root_params)
        for key_role in raw_role_keys:
            raw_role = raw['roles'][key_role_root][key_role].keys()
            validate_param(raw_role, role_params, role_optional_params)

    # validate infrastructures
    infrastructure_root_params = ['amount', 'role', 'hardware', 'location', 'provider', 'name', 'deployment',
                                  'release' ]
    infrastructure_root_params_mac = ['amount', 'role', 'location', 'provider', 'name', 'deployment',
                                     'release']
    raw_infrastructure_root_keys = raw['infrastructures'].keys()
    actual_roles = []
    for key_infrastructure_root in raw_infrastructure_root_keys:
        raw_infrastructure_keys = raw['infrastructures'][key_infrastructure_root].keys()
        try:
            provider = raw['infrastructures'][key_infrastructure_root]['provider']
        except:
            provider = ""
        if provider == "manageacloud":
            validate_param(raw_infrastructure_keys, infrastructure_root_params_mac)
        else:
            validate_param(raw_infrastructure_keys, infrastructure_root_params)
        actual_roles.append(raw['infrastructures'][key_infrastructure_root]["role"])

    # check the values of infrastructures > default > role
    not_existing_roles = is_unexpected(actual_roles, expected_roles)
    if len(not_existing_roles):
        print "The following roles are used under 'infrastructures' but are never defined:"
        for p in not_existing_roles:
            print " - %s" % p
        exit(3)

    # check the values of infrastructures > default > role
    not_existing_roles = is_present(actual_roles, expected_roles)
    if len(not_existing_roles):
        print "WARNING! The following roles are defined but never user:"
        for p in not_existing_roles:
            print " - %s" % p

    # get the root parameters
    root = {
        'version': raw['version'],
        'name': raw['name'],
        }

    return root, raw['roles'], raw['infrastructures']