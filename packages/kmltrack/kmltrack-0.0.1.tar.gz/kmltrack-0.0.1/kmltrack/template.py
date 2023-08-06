import re
import types

class Template(object):
    """A generic templating system using the same syntax as Pythons string
    Template, but generates output directly to a file, without
    constructing the whole thing in memory first.
    """

    template = ""
    ignore_missing = False

    def __init__(self, *arg, **kw):
        if arg or kw:
            self.render(*arg, **kw)

    def render(self, out_file, context=None):
        if context is None:
            context = {}
        for escape, parenvar, var, verbatim in re.findall(r"([$][$])|([$]{[a-z0-9_]*})|([$][a-z0-9_]*)|([^$]*)", self.template):
            if escape:
                out_file.write('$')
            elif parenvar:
                self.writevar(parenvar[2:-1], out_file, context)
            elif var:
                self.writevar(var[1:], out_file, context)
            else:
                out_file.write(verbatim)

    def writevar(self, name, out_file, context):
        cls = type(self)
        if name in context:
            value = context[name]
        elif hasattr(self, name):
            value = getattr(self, name)
        elif hasattr(cls, name):
            value = getattr(cls, name)
        elif self.ignore_missing:
            return
        else:
            raise Exception("Unknown substitution %s not in %s" % (name, context.keys()))

        if isinstance(value, type) and issubclass(value, Template):
            value(out_file, context)
        elif isinstance(value, (types.MethodType, types.FunctionType)):
            value(out_file, context)
        else:
            out_file.write(unicode(value).encode("utf-8"))
