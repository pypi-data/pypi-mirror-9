import ast

import dis
cde  = "def foo(a, b):\n"
cde += "    c = a + b\n"
cde += "    return c\n"

class GetReturnNode(ast.NodeVisitor):
    """
    A Visitor to get the return tuple names from a calc-style
    function
    """
    def visit_Return(self, node):
        if isinstance(node.value, ast.Tuple):
            return [e.id for e in node.value.elts]
        else: 
            return [node.value.id]



def bar(a, b):
    c = a + b
    d = 2*b
    return c, d


#func_code = compile(cde, "<string>", "exec")
#fakeglobals = {}
#eval(func_code, {}, fakeglobals)
#print(dis.dis(bar.__code__))


all_returned_vals = []
gnr = GetReturnNode()
all_out_args = None
tree = ast.parse(cde)
"""for node in ast.walk(ast.parse(''.join(cde))):
    all_out_args = gnr.visit(node)
    if all_out_args:
        break"""
 
