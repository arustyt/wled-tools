from collections import deque


class Tracer:

    def __init__(self):
        self.function_stack = deque()
        self.indent_stack = deque()

    def entering(self, function, verbose=True):
        self.function_stack.append(function)
        self.indent()

        if verbose:
            print("{indent}{prefix} Entering {function}".format(indent=self.get_indent(), prefix="{", function=".".join(self.function_stack)))

    def indent(self):
        self.indent_stack.append("  ")

    def exiting(self, verbose=True):
        if verbose:
            print("{indent}{prefix} Exiting {function}".format(indent=self.get_indent(), prefix="}", function=".".join(self.function_stack)))

        self.function_stack.pop()
        self.unindent()

    def unindent(self):
        self.indent_stack.pop()

    def get_indent(self):
        return "".join(self.indent_stack)
