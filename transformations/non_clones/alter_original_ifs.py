import ast
import astor
import random
from tinypy_generator import CodeGenerator

LEVELS = ["1.1", "1.2", "2.1", "2.2", "3.1", "3.2"]

class IfTransformer(ast.NodeTransformer):
    def __init__(self):
        pass
    
    def visit_If(self, node):
        # Randomly decide to keep or remove the if/elif/else statement
        if random.choice([True, False]):
            # Replace the code block with a random code snippet
            if node.body:
                root, random_code = CodeGenerator().generate_program(random.choice(LEVELS))
                node.body = ast.parse(random_code).body
            if node.orelse:
                root, random_code = CodeGenerator().generate_program(random.choice(LEVELS))
                node.orelse = ast.parse(random_code).body
        else:
            # Remove the entire if statement
            root, random_code = CodeGenerator().generate_program(random.choice(LEVELS))
            node.body = ast.parse(random_code).body
            
        return node

def alter_original_if_block_code(code):
    # Parse the code into an AST
    tree = ast.parse(code)
    # Apply the transformation
    transformer = IfTransformer()
    transformed_tree = transformer.visit(tree)
    # Convert the AST back to code
    return astor.to_source(transformed_tree)
