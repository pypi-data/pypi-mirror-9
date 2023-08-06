# -*- coding:utf8 -*-

"""
aliyunauth.ecs
~~~~~~~~~~~~~~

This module contains the authentication handlers for Ali Ecs Service
"""

from . import sign_ver_1_0


class EcsAuth(sign_ver_1_0.AuthBase):
    """Attach Aliyun Ecs Authentication to the given request

    :param access_key: the access_key of your ecs account
    :param secret_key: the secret_key of your ecs account
    :param response_format: (optional) response format [`xml`/`json`(default)]
    :param ram: (optional) resource access managment string (default None)

    Usage::

        >>> import requests
        >>> from aliyunauth import EcsAuth
        >>> req = request.get(
        ...     "https://ecs.aliyuncs.com",
        ...     params=dict(Action="DescribeInstanceTypes"),
        ...     auth=EcsAuth("access-key", "secret-key")
        ... )
        <Response [200]>

    """
    SERVICE = "ecs"
    VERSION = "2014-05-26"
