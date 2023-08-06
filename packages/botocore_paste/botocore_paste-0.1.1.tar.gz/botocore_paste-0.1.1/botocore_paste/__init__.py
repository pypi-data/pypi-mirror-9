# -*- coding: utf-8 -*-

import botocore.session


__version__ = '0.1.1'


def normalize_config(config, prefix='botocore.', **kwargs):
    """
    :type config: dict
    :type prefix: str
    :rtype: dict
    """
    env_vars = dict((k[len(prefix):], config[k]) for k in config
                    if k.startswith(prefix) and len(config[k]) > 0)
    env_vars.update(kwargs)
    for k in ('metadata_service_num_attempts', 'metadata_service_timeout'):
        if k in env_vars:
            env_vars[k] = int(env_vars[k])
    return env_vars


def session_from_config(config, prefix='botocore.', **kwargs):
    """
    :type config: dict
    :type prefix: str
    :rtype: botocore.session.Session
    """
    env_vars = normalize_config(config, prefix, **kwargs)
    return botocore.session.get_session(env_vars)
