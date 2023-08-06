import asyncio
from pathlib import PurePosixPath
import re

from . import cache
from .error import PrintableError
from . import glob


class Rule:
    def __init__(self, name, copy, move, executable, pick, export):
        self.name = name
        self.copy = copy
        self.move = move
        self.executable = executable
        self.pick = pick
        self.export = export

    def _cache_key(self, input_tree):
        return cache.compute_key({
            'input_tree': input_tree,
            'copy': self.copy,
            'move': self.move,
            'executable': self.executable,
            'pick': self.pick,
            'export': self.export,
        })

    @asyncio.coroutine
    def get_tree(self, runtime, input_tree):
        key = self._cache_key(input_tree)

        # As with Module, take a lock on the cache key to avoid running the
        # same rule (or identical rules) twice with the same input.
        cache_lock = runtime.cache_key_locks[key]
        with (yield from cache_lock):
            if key in runtime.cache.keyval:
                return runtime.cache.keyval[key]

            tree = input_tree
            if self.copy:
                tree = copy_files(runtime.cache, tree, self.copy)
            if self.move:
                tree = move_files(runtime.cache, tree, self.move)
            if self.pick:
                tree = pick_files(runtime.cache, tree, self.pick)
            if self.executable:
                tree = make_files_executable(
                    runtime.cache, tree, self.executable)
            if self.export:
                tree = get_export_tree(runtime.cache, tree, self.export)

            runtime.cache.keyval[key] = tree

        return tree


def _copy_files_modifications(_cache, tree, paths_multimap):
    modifications = {}
    for source in paths_multimap:
        source_info_dict = _cache.ls_tree(tree, source)
        if not source_info_dict:
            raise NoMatchingFilesError(
                'Path "{}" does not exist.'.format(source))
        source_info = list(source_info_dict.items())[0][1]
        for dest in paths_multimap[source]:
            # If dest is a directory, put the source inside dest instead of
            # overwriting dest entirely.
            dest_is_dir = False
            dest_info_dict = _cache.ls_tree(tree, dest)
            if dest_info_dict:
                dest_info = list(dest_info_dict.items())[0][1]
                dest_is_dir = (dest_info.type == cache.TREE_TYPE)
            adjusted_dest = dest
            if dest_is_dir:
                adjusted_dest = str(PurePosixPath(dest) /
                                    PurePosixPath(source).name)
            modifications[adjusted_dest] = source_info
    return modifications


def copy_files(_cache, tree, paths_multimap):
    modifications = _copy_files_modifications(_cache, tree, paths_multimap)
    return _cache.modify_tree(tree, modifications)


def move_files(_cache, tree, paths_multimap):
    # First obtain the copies from the original tree. Moves are not ordered but
    # happen all at once, so if you move a->b and b->c, the contents of c will
    # always end up being b rather than a.
    modifications = _copy_files_modifications(_cache, tree, paths_multimap)
    # Now add in deletions, but be careful not to delete a file that just got
    # moved. Note that if "a" gets moved into "dir", it will end up at "dir/a",
    # even if "dir" is deleted (because modify_tree always modifies parents
    # before decending into children, and deleting a dir is a modification of
    # that dir's parent).
    for source in paths_multimap:
        if source not in modifications:
            modifications[source] = None
    return _cache.modify_tree(tree, modifications)


def _get_glob_entries(_cache, tree, globs_list):
    matches = {}
    for glob_str in globs_list:
        # Do an in-memory match of all the paths in the tree against the
        # glob expression. As an optimization, if the glob is something
        # like 'a/b/**/foo', only list the paths under 'a/b'.
        regex = glob.glob_to_path_regex(glob_str)
        prefix = glob.unglobbed_prefix(glob_str)
        entries = _cache.ls_tree(tree, prefix, recursive=True)
        found = False
        for path, entry in entries.items():
            if re.match(regex, path):
                matches[path] = entry
                found = True
        if not found:
            raise NoMatchingFilesError(
                '"{}" didn\'t match any files.'.format(glob_str))
    return matches


def pick_files(_cache, tree, globs_list):
    picks = _get_glob_entries(_cache, tree, globs_list)
    return _cache.modify_tree(None, picks)


def make_files_executable(_cache, tree, globs_list):
    entries = _get_glob_entries(_cache, tree, globs_list)
    exes = {}
    for path, entry in entries.items():
        # Ignore directories.
        if entry.type == cache.BLOB_TYPE:
            exes[path] = entry._replace(mode=cache.EXECUTABLE_FILE_MODE)
    return _cache.modify_tree(tree, exes)


def get_export_tree(_cache, tree, export_path):
    entries = _cache.ls_tree(tree, export_path)
    if not entries:
        raise NoMatchingFilesError('Export path "{}" doesn\'t exist.'
                                   .format(export_path))
    entry = list(entries.values())[0]
    if entry.type != cache.TREE_TYPE:
        raise NoMatchingFilesError('Export path "{}" is not a directory.'
                                   .format(export_path))
    return entry.hash


class NoMatchingFilesError(PrintableError):
    pass
