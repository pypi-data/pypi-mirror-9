# -*- coding: utf-8 -*-
"""
:summary: All utility functionality goes in here.

:author: francis.horsman@gmail.com
"""

import copy
import os


def update_dict(a, b, in_place=True):
    if not in_place:
        a = copy.deepcopy(a)
    for k, v in b.iteritems():
        a[k] = v
    return a


def new_env(d):
    env = os.environ.copy()
    env.update(d)
    return env


def get_env_str(env=None):
    env = env if env is not None else os.environ.copy()
    s = ', '.join(['(%s=%s)' % (k, v) for k, v in env.iteritems()])
    return s


if __name__ == '__main__':  # pragma no cover
    pass
