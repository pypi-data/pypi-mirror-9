

class _Context(object):

    def __init__(self):
        self.counter = -1
        self.current_group_stack = []
        self.expert_groups = set()

    def new_order(self):
        self.counter += 1
        return self.counter


class _ContextStack(object):

    """module global management of contexts.

    I'm not sure if this is realy needed, but if one accidentaly imports a module within
    a context and the module inturn creates a new context this would lead to very hard to
    find errors.
    """

    def __init__(self):
        self.stack = []

    def install_new_context(self):
        self.ctx = _Context()
        self.stack.append(self.ctx)

    def current_context(self):
        return self.ctx

    def drop_context(self):
        del self.stack[-1]

# this is a private module global variable:
_context_stack = _ContextStack()
