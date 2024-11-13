# SPDX-FileCopyrightText: 2024 SAP SE or an SAP affiliate company and Gardener contributors
#
# SPDX-License-Identifier: Apache-2.0

from functools import reduce

class ConfigValidator:
    @staticmethod
    def validate_str(clazz, config):
        if not isinstance(config, str):
            raise TypeError("Incorrect type for {} config. Required str, got {}.".format(clazz, type(config)))

    @staticmethod
    def validate_dict(clazz, config):
        if not isinstance(config, dict):
            raise TypeError("Incorrect type for {} config. Required dict, got {}.".format(clazz, type(config)))

        if not ConfigValidator.__is_dict_config_valid(config, clazz.__dict__.get("required_keys"), clazz.__dict__.get("optional_keys")):
            raise ValueError("Config for {} is not in the correct format: {}.".format(clazz, config))

        for base in clazz.__bases__:
            if not ConfigValidator.__is_dict_config_valid(config, base.__dict__.get("required_keys"), base.__dict__.get("optional_keys")):
                raise ValueError("Config for {} is not in the correct format: {}.".format(clazz, config))

    @staticmethod
    def __is_dict_config_valid(config, required_keys, optional_keys=None):
        def validate_required_keys(key):
            return False if key["key"] not in config.keys() or not isinstance(config[key["key"]], key["types"]) else True

        def validate_optional_keys(key):
            return False if key["key"] in config.keys() and not isinstance(config[key["key"]], key["types"]) else True

        def reducer(x, y):
            return x and y

        return (required_keys is None or len(required_keys) == 0 or reduce(reducer, map(validate_required_keys, required_keys))) \
            and (optional_keys is None or len(optional_keys) == 0 or reduce(reducer, map(validate_optional_keys, optional_keys)))
