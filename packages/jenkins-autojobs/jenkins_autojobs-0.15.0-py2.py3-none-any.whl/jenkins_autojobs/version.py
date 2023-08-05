#!/usr/bin/env python
# encoding: utf-8

'''
Version information constants and auxiliary functions.
'''


VERSION = (0, 6, 0)


import os
import subprocess as sub

__here__ = os.path.abspath(os.path.dirname(__file__))


def _check_output(*cmd):
    p = sub.Popen(cmd, stdout=sub.PIPE, stderr=sub.PIPE, cwd=__here__)
    return p.communicate()[0].rstrip('\n')


# PEP8 hates me
_gitsha = lambda : _check_output('git', 'rev-parse',    'HEAD')
_gitbrc = lambda : _check_output('git', 'symbolic-ref', 'HEAD').replace('refs/heads/', '')


def version():
    return '.'.join([str(i) for i in VERSION])


def version_verbose():
    res = 'jenkins-autojobs version %s' % version()
    try:
        sha = _gitsha() ; brc = _gitbrc()
        if sha or brc:
            res = '%s (%s:%s)' % (res, brc, sha[:8])
    except:
        pass

    return res


__all__ = (VERSION, version, version_verbose)


if __name__ == '__main__':
    from sys import stdout
    stdout.write(version_verbose())
