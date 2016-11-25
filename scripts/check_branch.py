#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''Validates that the branch is correct

Used in release environment for tox

Usage: {file} [options]

Options:
    -b --branch NAME  Branch to check for [default: master]
'''
from git import Repo


def check_branch(branch=None):
    '''Looks at current repo and validates that the branch is as expected.

    Args:
        branch(str): Name of branch [default: master]

    Raises:
        RuntimeError: If branch_name doesn't match current branch
    '''
    branch = branch or 'master'
    repo = Repo(search_parent_directories=True)
    branch_name = repo.active_branch.name
    if branch_name != branch:
        raise RuntimeError('Branch "{}" is not "{}".  Execution halted.'.format(branch_name, branch))


if __name__ == '__main__':
    from docopt import docopt

    def fix(k):
        k = k.lstrip('-')
        k = k.lstrip('<').rstrip('>')
        k = k.replace('-', '_')
        return k

    docstring = __doc__.format(file=__file__)
    options = {fix(k): v for k, v in docopt(docstring).items()}
    check_branch(**options)
