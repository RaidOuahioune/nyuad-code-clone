import ast,astor
class RemoveUselessOperations(ast.NodeTransformer):
    def visit_BinOp(self, node):
        # First, visit the left and right children
        node.left = self.visit(node.left)
        node.right = self.visit(node.right)

        # Remove addition of zero
        if isinstance(node.op, ast.Add):
            if isinstance(node.right, ast.Constant) and node.right.value == 0:
                return node.left
            if isinstance(node.left, ast.Constant) and node.left.value == 0:
                return node.right

        # Remove multiplication by one
        if isinstance(node.op, ast.Mult):
            if isinstance(node.right, ast.Constant) and node.right.value == 1:
                return node.left
            if isinstance(node.left, ast.Constant) and node.left.value == 1:
                return node.right

        # Remove division by one
        if isinstance(node.op, ast.Div):
            if isinstance(node.right, ast.Constant) and node.right.value == 1:
                return node.left

        return node

def remove_useless_operations(code_snippet):
    # Parse code snippet into AST
    tree = ast.parse(code_snippet)
    
    # Apply the transformation
    transformer = RemoveUselessOperations()
    transformed_tree = transformer.visit(tree)
    
    # Convert AST back to source code
    new_code_snippet = astor.to_source(transformed_tree).strip()
    
    return new_code_snippet