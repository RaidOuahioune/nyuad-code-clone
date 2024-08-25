import ast
import astor
import random
import string

# Function to generate random values
def generate_random_value(value_type):
    if value_type == 'int':
        return random.randint(0, 100)  # Adjust range as needed
    elif value_type == 'float':
        return round(random.uniform(0.0, 100.0), 2)  # Adjust precision as needed
    elif value_type == 'bool':
        return random.choice([True, False])
    return None

# AST Node Transformer to replace constants
class ConstantTransformer(ast.NodeTransformer):
    def visit_Num(self, node):
        # Handle integer and float numbers
        if isinstance(node.n, int):
            return ast.copy_location(ast.Constant(value=generate_random_value('int')), node)
        elif isinstance(node.n, float):
            return ast.copy_location(ast.Constant(value=generate_random_value('float')), node)
        return node
    
    def visit_Constant(self, node):
        if isinstance(node.value, bool):
            return ast.copy_location(ast.Constant(value=generate_random_value('bool')), node)
        elif isinstance(node.value, int):
            return ast.copy_location(ast.Constant(value=generate_random_value('int')), node)
        elif isinstance(node.value, float):
            return ast.copy_location(ast.Constant(value=generate_random_value('float')), node)
        # If it's a string or other type, don't replace
        return node

# Function to transform code
def blind_constant_changer(code):
    tree = ast.parse(code)
    transformer = ConstantTransformer()
    transformed_tree = transformer.visit(tree)
    return astor.to_source(transformed_tree)