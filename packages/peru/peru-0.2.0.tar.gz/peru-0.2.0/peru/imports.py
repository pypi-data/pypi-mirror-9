import asyncio
import os

from .async import stable_gather
from . import compat
from .merge import merge_imports_tree


@asyncio.coroutine
def checkout(runtime, scope, imports, path):
    imports_tree = yield from get_imports_tree(runtime, scope, imports)
    last_imports_tree = _get_last_imports(runtime)
    runtime.cache.export_tree(imports_tree, path, last_imports_tree,
                              force=runtime.force)
    _set_last_imports(runtime, imports_tree)


@asyncio.coroutine
def get_imports_tree(runtime, scope, imports, base_tree=None):
    target_trees = yield from get_trees(runtime, scope, imports.keys())
    imports_tree = merge_imports_tree(runtime.cache, imports, target_trees,
                                      base_tree)
    return imports_tree


@asyncio.coroutine
def get_trees(runtime, scope, targets):
    futures = [get_tree(runtime, scope, target) for target in targets]
    trees = yield from stable_gather(*futures)
    return dict(zip(targets, trees))


@asyncio.coroutine
def get_tree(runtime, scope, target_str):
    module, rules = yield from scope.parse_target(runtime, target_str)
    tree = yield from module.get_tree(runtime)
    if module.default_rule:
        tree = yield from module.default_rule.get_tree(runtime, tree)
    for rule in rules:
        tree = yield from rule.get_tree(runtime, tree)
    return tree


def _last_imports_path(runtime):
    return os.path.join(runtime.peru_dir, 'lastimports')


def _get_last_imports(runtime):
    last_imports_tree = None
    if os.path.exists(_last_imports_path(runtime)):
        with open(_last_imports_path(runtime)) as f:
            last_imports_tree = f.read()
    return last_imports_tree


def _set_last_imports(runtime, tree):
    compat.makedirs(os.path.dirname(_last_imports_path(runtime)))
    with open(_last_imports_path(runtime), 'w') as f:
        f.write(tree)
