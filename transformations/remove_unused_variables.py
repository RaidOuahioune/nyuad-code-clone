import ast
import astor

class RemoveUnusedVariables(ast.NodeTransformer):
    def __init__(self):
        self.used_vars = set()
        self.assigned_vars = set()
    
    def visit_Assign(self, node):
        if isinstance(node.targets[0], ast.Name):
            self.assigned_vars.add(node.targets[0].id)
        return self.generic_visit(node)
    
    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load):
            self.used_vars.add(node.id)
        return self.generic_visit(node)
    
    def visit_FunctionDef(self, node):
        self.used_vars = set()
        self.assigned_vars = set()
        self.generic_visit(node)
        return node
    
    def visit_Module(self, node):
        self.used_vars = set()
        self.assigned_vars = set()
        self.generic_visit(node)
        # Filter out assignments to unused variables
        node.body = [n for n in node.body if not (
            isinstance(n, ast.Assign) and n.targets[0].id not in self.used_vars)]
        return node

def remove_unused_vars(code):
    # Parse the code into an AST
    tree = ast.parse(code)
    
    # Create a transformer and apply it
    transformer = RemoveUnusedVariables()
    new_tree = transformer.visit(tree)
    
    # Convert the transformed AST back to code
    new_code = astor.to_source(new_tree)
    
    return new_code

