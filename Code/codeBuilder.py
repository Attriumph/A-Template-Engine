# this class is just a easy tool for us to build python code of template


class CodeBuilder(object):

    INDENT_STEP = 4

    def __init__(self, indent=0):
        self.code = []
        self.indent_level = indent

    def add_line(self,line):
        self.code.extend(['' * self.indent_level,line,'\n'])

    def indent(self):
        self.indent_level += self.INDENT_STEP

    def dedent(self):
        self.indent_level -= self.INDENT_STEP

    def add_section(self):
        section = CodeBuilder(self.indent_level)
        self.code.append(section)
        return section

    def __str__(self):
        return ''.join(str(c) for c in self.code)

    def get_globals(self):
        """Execute the code, and return a dict of globals it defines."""
        # A check that the caller really finished all the blocks they started.
        assert self.indent_level == 0
        # Get the Python source in the form of  string.
        python_source = str(self)
        # Execute the python code and collect global varibales defined within the code.
        global_namespace = {}
        exec(python_source, global_namespace)
        return global_namespace