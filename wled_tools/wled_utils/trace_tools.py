from collections import deque
from wled_utils.logger_utils import get_logger


class Tracer:

    def __init__(self, verbose=False):
        self.verbose = verbose
        self.function_stack = deque()
        self.indent_stack = deque()

    def entering(self, function):
        self.function_stack.append(function)
        self.indent()

        if self.verbose:
            get_logger().info("{indent}{prefix} Entering {function}".format(indent=self.get_indent(), prefix="{", function=".".join(self.function_stack)))

    def indent(self):
        self.indent_stack.append("    ")

    def exiting(self):
        if self.verbose:
            get_logger().info("{indent}{prefix} Exiting {function}".format(indent=self.get_indent(), prefix="}", function=".".join(self.function_stack)))

        self.function_stack.pop()
        self.unindent()

    def unindent(self):
        self.indent_stack.pop()

    def get_indent(self):
        return "".join(self.indent_stack)
