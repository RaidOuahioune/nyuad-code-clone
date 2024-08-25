import ast
import astor

class SimplifyOperations(ast.NodeTransformer):
    def visit_BinOp(self, node):
        # First, visit the left and right children
        node.left = self.visit(node.left)
        node.right = self.visit(node.right)

        # Evaluate var/var to 1
        if isinstance(node.op, ast.Div):
            if isinstance(node.left, ast.Name) and isinstance(node.right, ast.Name):
                if node.left.id == node.right.id:
                    return ast.Constant(value=1)

        # Evaluate var*0 to 0
        if isinstance(node.op, ast.Mult):
            if (isinstance(node.left, ast.Name) and isinstance(node.right, ast.Constant) and node.right.value == 0) or \
               (isinstance(node.right, ast.Name) and isinstance(node.left, ast.Constant) and node.left.value == 0):
                return ast.Constant(value=0)

        # Evaluate var-var to 0
        if isinstance(node.op, ast.Sub):
            if isinstance(node.left, ast.Name) and isinstance(node.right, ast.Name):
                if node.left.id == node.right.id:
                    return ast.Constant(value=0)
                
        if isinstance(node.op, ast.Add):
            if isinstance(node.left, ast.Name) and isinstance(node.right, ast.Name):
                if node.left.id == node.right.id:
                    return ast.BinOp(left=ast.Constant(value=2), op=ast.Mult(), right=node.left)

        return node

def simplify_obvious_operations(code_snippet):
    # Parse code snippet into AST
    tree = ast.parse(code_snippet)
    
    # Apply the transformation
    transformer = SimplifyOperations()
    transformed_tree = transformer.visit(tree)
    
    # Convert AST back to source code
    new_code_snippet = astor.to_source(transformed_tree).strip()
    
    return new_code_snippet


