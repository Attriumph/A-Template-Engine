import re
from codeBuilder import *


class TempliteSyntaxError(ValueError):
    # raised when a template has a synax error
    pass


class Templite(object):

    def __init__(self, text, *contexts):
        """Construct a Templite Object with the given `text`.
        `contexts` are dictionaries of values to use for future renderings.
        These are good for filters and global values.
        """
        # define a dict of context
        self.context = {}
        for context in contexts:
            self.context.update(context)
        # define two set that will record all variables and loop variables
        self.all_vars = set()
        self.loop_vars = set()

        # create an object of CodeBuilder and create fixed python code of final exectuable python code
        code = CodeBuilder()
        code.add_line('def render_function(context, do_dots):')
        code.indent()
        vars_code = code.add_section()
        code.add_line('result = []')
        code.add_line('append_result = result.append')
        code.add_line('extend_result = result.extend')
        code.add_line('to_str = str')

        buffered = []

        def flush_output():

            """ an inner function to help us with buffering output strings."""
            if len(buffered) == 1:
                code.add_line("append_result(%s)" % buffered[0])
            elif len(buffered) > 1:
                # combine repeated append calls into one extend call
                code.add_line("extend_result([%s])" % ", ".join(buffered))
            del buffered[:]

        ops_stack = []

        # Split the text according to special signs to form a list of tokens.
        tokens = re.split(r"(?s)({{.*?}}|{%.*?%}|{#.*?#})", text)

        # deal with four situations of tokens according to the begin of them
        for token in tokens:
            if token.startswith('{#'):
                # it means comment, ignore it and move on.
                continue
            elif token.startswith('{{'):
                # An expression need to be deal with _expr_code method(convert token into python code).
                expr = self._expr_code(token[2:-2].strip())
                buffered.append("to_str(%s)" % expr)
            elif token.startswith('{%'):
                # if or for statement, which need to be split into words and parse further.
                flush_output()
                words = token[2:-2].strip().split()
                if words[0] == 'if':
                    # means it is a if statement, evaluate the expression to determine if.
                    if len(words) != 2:
                        self._syntax_error("Don't understand if", token)
                    ops_stack.append('if')
                    code.add_line("if %s:" % self._expr_code(words[1]))
                    code.indent()
                elif words[0] == 'for':
                    # means a for loop, iterate over expression result.
                    if len(words) != 4 or words[2] != 'in':
                        self._syntax_error("Don't understand for", token)
                    ops_stack.append('for')
                    self._variable(words[1], self.loop_vars)
                    code.add_line(
                        "for c_%s in %s:" % (
                            words[1],
                            self._expr_code(words[3])
                        )
                    )
                    code.indent()
                elif words[0].startswith('end'):
                    # End of a for or if, pop the ops stack.
                    if len(words) != 1:
                        self._syntax_error("Don't understand end", token)
                    end_what = words[0][3:]
                    if not ops_stack:
                        self._syntax_error("Too many ends", token)
                    start_what = ops_stack.pop()
                    if start_what != end_what:
                        self._syntax_error("Mismatched end tag", end_what)
                    code.dedent()
                else:
                    self._syntax_error("Don't understand tag", words[0])
            else:
                # Literal content.  If it isn't empty, output it.
                if token:
                    buffered.append(repr(token))

            if ops_stack:
                self._syntax_error("Unmatched action tag", ops_stack[-1])

            flush_output()

            # define local variables by compare all_vars and loop_vars
            for var_name in self.all_vars - self.loop_vars:
                vars_code.add_line("c_%s = context[%r]" % (var_name, var_name))

            code.add_line("return ''.join(result)")
            code.dedent()
            """"
            grab the render_function value from the result of get_globals, 
            and save it as an attribute in our Templite object:
            """
            self._render_function = code.get_globals()['render_function']

        def _expr_code(self, expr):
            """Generate a Python expression for `expr`."""
        if "|" in expr:
            pipes = expr.split("|")
            code = self._expr_code(pipes[0])
            for func in pipes[1:]:
                self._variable(func, self.all_vars)
                code = "c_%s(%s)" % (func, code)
        elif "." in expr:
            dots = expr.split(".")
            code = self._expr_code(dots[0])
            args = ", ".join(repr(d) for d in dots[1:])
            code = "do_dots(%s, %s)" % (code, args)
        else:
            self._variable(expr, self.all_vars)
            code = "c_%s" % expr
        return code

        def _syntax_error(self, msg, thing):
            """Raise a syntax error using `msg`, and showing `thing`."""
        raise TempliteSyntaxError("%s: %r" % (msg, thing))

    def _variable(self, name, vars_set):
        """Track that `name` is used as a variable.
        Adds the name to `vars_set`, a set of variable names.
        """
        if not re.match(r"[_a-zA-Z][_a-zA-Z0-9]*$", name):
            self._syntax_error("Not a valid name", name)
        vars_set.add(name)

    def render(self, context=None):
        """Render this template by applying it to `context`.
        """
        # Make the complete context we'll use.
        render_context = dict(self.context)
        if context:
            render_context.update(context)
        return self._render_function(render_context, self._do_dots)

    def _do_dots(self, value, *dots):
        for dot in dots:
            try:
                value = getattr(value, dot)
            except AttributeError:
                value = value[dot]
            if callable(value):
                value = value()
        return value
