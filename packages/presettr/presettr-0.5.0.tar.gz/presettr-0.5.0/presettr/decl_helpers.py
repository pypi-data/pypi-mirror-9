import contextlib


def propagate_change(from_, to, method=None):
    if method is None:
        method = lambda x: x
    from_.target = (to, method)


def propagate_default(from_, to, method=None):
    if method is None:
        method = lambda x: x
    to._value = from_.value


@contextlib.contextmanager
def ValueGroup(name, expert_settings=False):
    from . import _context_stack
    ctx = _context_stack.current_context()
    ctx.current_group_stack.append(name)
    group_stack = tuple(ctx.current_group_stack)
    if expert_settings:
        ctx.expert_groups.add(group_stack)
    yield
    del ctx.current_group_stack[-1]
