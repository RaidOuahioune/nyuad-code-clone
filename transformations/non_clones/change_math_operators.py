import ast
import astor
import random

def change_math_operators(code_snippet):
    # Define possible math operators
    operators = {
        ast.Add: [ast.Sub, ast.Mult, ast.Div],
        ast.Sub: [ast.Add, ast.Mult, ast.Div],
        ast.Mult: [ast.Add, ast.Sub, ast.Div],
        ast.Div: [ast.Add, ast.Sub, ast.Mult]
    }
    
    # Parse code snippet into AST
    tree = ast.parse(code_snippet)
    change_made = False  # Flag to ensure at least one change is made
    
    class ChangeMathOperators(ast.NodeTransformer):
        def visit_BinOp(self, node):
            nonlocal change_made
            # Check if the operation is a math operation
            if type(node.op) in operators:
                # Randomly decide whether to change this operator
                if random.choice([True, False]) or not change_made:
                    # Choose a different operator
                    new_op = random.choice(operators[type(node.op)])
                    node.op = new_op()
                    change_made = True  # Mark that a change has been made
            return self.generic_visit(node)
    
    transformer = ChangeMathOperators()
    transformed_tree = transformer.visit(tree)
    
    # If no change was made, forcefully change one operator
    if not change_made:
        class ForceChangeMathOperators(ast.NodeTransformer):
            def visit_BinOp(self, node):
                # Only change the first math operation encountered
                if type(node.op) in operators and not change_made:
                    new_op = random.choice(operators[type(node.op)])
                    node.op = new_op()
                    return node
                return self.generic_visit(node)
        
        force_transformer = ForceChangeMathOperators()
        transformed_tree = force_transformer.visit(transformed_tree)
    
    # Convert AST back to source code
    new_code_snippet = astor.to_source(transformed_tree).strip()
    
    return new_code_snippet
