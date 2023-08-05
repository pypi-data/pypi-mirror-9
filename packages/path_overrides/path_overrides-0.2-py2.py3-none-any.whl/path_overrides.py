#!/usr/bin/env python
"""
Detect duplicate program names in the path where one overrides another

Ignores ones which are really the same (e.g. a symlink from one to another)

Copyright (c) 2014-2015 Ben Bass <benbass@codedstructure.net>
See LICENSE file for details and (absence of) warranty

@codedstructure
"""

import os
import itertools

__version__ = "0.2"
__author__ = "Ben Bass"

identity = lambda x: x


class ExeInfo(object):
    path = None
    stat = None
    is_exec = None
    target = None
    error = None

    def __init__(self, path, root_dir=None):
        self.display_path = path

        if root_dir is not None:
            self.path = os.path.join(root_dir, path.lstrip(os.sep))
        else:
            self.path = path

        try:
            self.stat = os.stat(self.path)
            self.is_exec = os.access(self.path, os.X_OK)
        except OSError as e:
            self.error = str(e)
        if os.path.islink(self.path):
            self.target = os.readlink(self.path)

    def matches(self, other):
        if self.stat == other.stat:  # e.g. both None
            return True
        if self.stat is None or other.stat is None:
            return False
        return os.path.samestat(self.stat, other.stat)

    def render(self, default_format=None, link_format=None, error_format=None):
        default_format = default_format or identity
        link_format = link_format or identity
        error_format = error_format or identity

        result = self.display_path
        if self.target:
            result += ' ' + link_format('({})'.format(self.target))
        if self.error:
            result += ' ' + error_format('({})'.format(self.error))

        return default_format(result)

    def __str__(self):
        return self.render()


def path_diff(path=None, path_sep=None, root_dir=None):
    """
    yield pairs of program names in PATH where one overrides another

    :param path: if provided, alternate to system PATH environment variable
    :type path: str
    :param path_sep: if provide, alternate to standard path element separator
    :type path_sep: str
    :param root_dir: if given, make each absolute element of `path` relative
        to this (note relative entries are unaffected)
    :type root_dir: str
    """
    # map from entry in 'PATH' to the file listing for that path
    exes = {}

    if path is None:
        path = os.environ.get('PATH', '')

    if path_sep is None:
        path_sep = os.pathsep  # ':' on POSIX

    if root_dir is None:
        root_dir = os.sep  # '/' on POSIX
    else:
        root_dir = os.path.expanduser(root_dir)

    path_spec = path.split(path_sep)
    for path in path_spec[:]:
        # adjust absolute paths in path_spec by root_dir
        # ill-advised relative paths in PATH (e.g. '.') are not changed as
        # that would effectively make them absolute.
        if os.path.isabs(path):
            real_path = os.path.join(root_dir, path.lstrip(os.sep))
        else:
            real_path = path
        try:
            # Note we could filter on only executable things here, but that
            # would require additional IO; doing (CPU-bound) string
            # manipulation first and only IO if required is (probably?) faster
            exes[path] = set(os.listdir(real_path))
        except OSError:
            # Perhaps the PATH entry doesn't refer to a valid directory
            path_spec.remove(path)

    for left, right in itertools.combinations(path_spec, 2):
        # 'left' will always be earlier in the path since path_spec is
        # sorted and combinations preserves this
        overlap = exes[left] & exes[right]
        for entry in overlap:
            left_info = ExeInfo(os.path.join(left, entry), root_dir=root_dir)
            right_info = ExeInfo(os.path.join(right, entry), root_dir=root_dir)

            if not (left_info.is_exec or right_info.is_exec):
                # ignore non-executable files
                continue

            if not left_info.matches(right_info):
                yield (left_info, right_info)


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="""Display executables in the PATH which override other
                    (different) programs later in the PATH""")

    parser.add_argument('--version', action='version',
                        version='%(prog)s ' + __version__)
    parser.add_argument('-p', '--path', default=os.environ.get('ENVIRON'),
                        help="provide custom PATH value directly rather than from environment")
    parser.add_argument('--path-sep', default=os.pathsep,
                        help="path separator; defaults to system default")
    parser.add_argument('--root-dir',
                        help="assumed root of PATH if given")

    arguments = parser.parse_args()

    try:
        from blessings import Terminal
    except ImportError:
        class Terminal(object):
            def __getattr__(self, key):
                return identity

    T = Terminal()

    for left, right in path_diff(path=arguments.path,
                                 path_sep=arguments.path_sep,
                                 root_dir=arguments.root_dir):
        print("{} overrides {}".format(left.render(T.bright_cyan, T.cyan, T.red),
                                       right.render(T.bright_blue, T.blue, T.red)))


if __name__ == '__main__':
    main()
