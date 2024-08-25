import ast
import astor
import sympy as sp
import random

class SimplifyExpression(ast.NodeTransformer):
    def visit_Assign(self, node):
        # Handle assignments with binary operations
        if isinstance(node.value, ast.BinOp):
            # Randomly decide whether to simplify the expression or keep it as is
            if random.choice([True, False]):
                simplified_expr = self.simplify_binop(node.value)
                node.value = ast.parse(str(simplified_expr)).body[0].value
            else:
                # Keep the expression as is
                node.value = node.value
        
        return self.generic_visit(node)

    def simplify_binop(self, node):
        # Convert AST BinOp to a sympy expression
        expr = self.ast_to_sympy(node)
        # Simplify the sympy expression
        simplified_expr = sp.simplify(expr)
        return simplified_expr

    def ast_to_sympy(self, node):
        # Recursively convert AST BinOp to sympy expression
        if isinstance(node, ast.BinOp):
            left = self.ast_to_sympy(node.left)
            right = self.ast_to_sympy(node.right)
            
            if isinstance(node.op, ast.Add):
                return left + right
            elif isinstance(node.op, ast.Sub):
                return left - right
            elif isinstance(node.op, ast.Mult):
                return left * right
            elif isinstance(node.op, ast.Div):
                return left / right
            elif isinstance(node.op, ast.Pow):
                return left ** right

        elif isinstance(node, ast.Name):
            return sp.Symbol(node.id)
        
        elif isinstance(node, ast.Constant):
            return sp.sympify(node.value)
        
        else:
            return node

def apply_simplify_expression(code_snippet):
    # Parse the code snippet into an AST
    tree = ast.parse(code_snippet)
    
    # Apply the transformation
    transformer = SimplifyExpression()
    transformed_tree = transformer.visit(tree)
    
    # Convert the AST back to source code
    new_code_snippet = astor.to_source(transformed_tree).strip()
    
    return new_code_snippet
