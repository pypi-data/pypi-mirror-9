from munch import Munch

import gossip
from gossip.exceptions import UndefinedHook
from .utils import TestSteps, _noop
import pytest


steps = TestSteps()

@steps.add
def _make_group_strict(ctx):
    if ctx.registered_undefined_hook or (ctx.registered_defined_hook and not ctx.defined_hook):
        raises_context = pytest.raises(UndefinedHook)
    else:
        raises_context = _noop()

    with raises_context:
        gossip.get_or_create_group("group").set_strict()
        ctx.made_strict = True

@steps.add
def _register_undefined_hook(ctx):
    if ctx.made_strict:
        raises_context = pytest.raises(UndefinedHook)
    else:
        raises_context = _noop()
    with raises_context:
        @gossip.register('group.undefined_hook')
        def handler():
            pass
    ctx.registered_undefined_hook = True

@steps.add
def _register_defined_hook(ctx):
    if ctx.made_strict and not ctx.defined_hook:
        raises_context = pytest.raises(UndefinedHook)
    else:
        raises_context = _noop()
    with raises_context:
        @gossip.register('group.defined_hook')
        def handler():
            pass
    ctx.registered_defined_hook = True

@steps.add
def _define_hook(ctx):
    gossip.define("group.defined_hook")
    ctx.defined_hook = True


@steps.get_all_permutations
def test_strict_groups(steps):
    ctx = Munch(
        made_strict=False,
        defined_hook=False,
        registered_undefined_hook=False,
        registered_defined_hook=False,
    )
    for step_func in steps:
        step_func(ctx)
