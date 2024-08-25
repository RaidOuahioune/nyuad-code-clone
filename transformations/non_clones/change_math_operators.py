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
    
    class ChangeMathOperators(ast.NodeTransformer):
        def visit_BinOp(self, node):
            # Check if the operation is a math operation
            if type(node.op) in operators:
                # Randomly decide whether to change this operator
                if random.choice([True, False]):
                    # Choose a different operator
                    new_op = random.choice(operators[type(node.op)])
                    node.op = new_op()
            return self.generic_visit(node)
    
    transformer = ChangeMathOperators()
    transformed_tree = transformer.visit(tree)
    
    # Convert AST back to source code
    new_code_snippet = astor.to_source(transformed_tree).strip()
    
    return new_code_snippet
