import collections
import datetime
import os
import subprocess

from .. import utils

Post = collections.namedtuple('Post', 'title date rst_path')


def rst_paths(blogroot):
    'Get a list of rST files in configured blog root dir'
    find = ['find', blogroot, '-name', '*.rst']
    try:
        return sorted(subprocess.check_output(find,
                                              stderr=subprocess.STDOUT)
                                .decode('utf-8')
                                .split(),
                      reverse=True)
    except subprocess.CalledProcessError:
        return tuple()


def blogtree(rst_paths):
    D = utils.OrderedDefaultdict
    d = D(lambda: D(list))
    for rst_path in rst_paths:
        date = datetime.date(*map(int, rst_path.split(os.sep)[1:4]))
        d[date.year][date.month].append(rst_path)
    return d


def prev_next(rst_path, rst_paths):
    try:
        next_index = rst_paths.index(rst_path) - 1
        if next_index < 0 :
            next_rst = None
        else:
            next_rst = rst_paths[next_index]
    except IndexError:
        next_rst = None
    try:
        previous_rst = rst_paths[rst_paths.index(rst_path) + 1]
    except IndexError:
        next_rst = None
    return previous_rst, next_rst
