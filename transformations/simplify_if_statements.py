import ast
import astor
import sympy as sp
import random

from transformations.variables_vocab import get_new_variable_name

class RandomizeIfSimplification(ast.NodeTransformer):
    def __init__(self):
        self.declared_vars = []  # List to keep track of declared variables

    def visit_If(self, node):
        # Randomly decide the action to take
        action = random.choice(['simplify',  'add_junk'])

        if action == 'simplify':
            # Simplify the test expression if possible
            simplified_test = self.simplify_condition(node.test)
            
            if simplified_test is not None:
                if isinstance(simplified_test, ast.Constant):
                    # If the condition is always True or False, adjust the if structure accordingly
                    if simplified_test.value:
                        return node.body  # Always True, remove the elif and else
                    else:
                        # Always False, replace body with the else part if it exists
                        return node.orelse if node.orelse else []
                else:
                    # Replace the original test condition with the simplified one
                    node.test = simplified_test
        
        elif action == 'add_junk':
            # Add a junk condition with random operations and variables
            num_vars = random.randint(2, 5)
            self.declared_vars = [get_new_variable_name() for _ in range(num_vars)]
            junk_values = [random.randint(-10000, 10000) for _ in range(num_vars)]
            
            # Define the junk variables and their values
            junk_assignments = [
                ast.Assign(
                    targets=[ast.Name(id=var, ctx=ast.Store())],
                    value=ast.Constant(value=value)
                )
                for var, value in zip(self.declared_vars, junk_values)
            ]
            
            # Define a random junk operation using declared variables
            if len(self.declared_vars) > 1:
                op1 = ast.Name(id=random.choice(self.declared_vars), ctx=ast.Load())
                op2 = ast.Name(id=random.choice(self.declared_vars), ctx=ast.Load())
            else:
                op1 = ast.Name(id=self.declared_vars[0], ctx=ast.Load())
                op2 = ast.Constant(value=random.choice(junk_values))

            op = random.choice([ast.Add(), ast.Sub(), ast.Mult(), ast.Div()])
            op_expr = ast.BinOp(left=op1, op=op, right=op2)
            
            junk_body = junk_assignments + [ast.Expr(
                value=ast.Call(
                    func=ast.Name(id='print', ctx=ast.Load()),
                    args=[op_expr],
                    keywords=[]
                )
            )]

            # Junk condition is always false
            junk_condition = ast.If(
                test=ast.Compare(
                    left=ast.Constant(value=random.randint(-10000, 10000)),
                    ops=[ast.Eq()],
                    comparators=[ast.Constant(value=random.randint(-10000, 10000))]
                ),
                body=junk_body,
                orelse=[]
            )
            # Add the junk condition before the original if statement
            return [junk_condition, node]

        # If no simplification or junk condition is applied, continue as usual
        return self.generic_visit(node)

    def simplify_condition(self, node):
        # Convert the condition to a sympy expression and evaluate it
        expr = self.eval_expr(node)
        
        if expr is not None:
            # Simplify the sympy expression
            simplified_expr = sp.simplify(expr)
            
            # Evaluate the simplified expression
            if simplified_expr == True:
                return ast.Constant(value=True)
            elif simplified_expr == False:
                return ast.Constant(value=False)
        
        return node

    def eval_expr(self, node):
        # Convert AST node to sympy expression
        if isinstance(node, ast.Constant):
            return sp.sympify(node.value)
        elif isinstance(node, ast.Name):
            return sp.Symbol(node.id)
        elif isinstance(node, ast.BinOp):
            return self.eval_binop(node)
        elif isinstance(node, ast.Compare):
            left = self.eval_expr(node.left)
            right = self.eval_expr(node.comparators[0])
            op = self.eval_compare_op(node.ops[0])
            
            if left is not None and right is not None and op is not None:
                return op(left, right)
        return None

    def eval_binop(self, node):
        left = self.eval_expr(node.left)
        right = self.eval_expr(node.right)
        
        if left is not None and right is not None:
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
        return None

    def eval_compare_op(self, op):
        # Convert AST comparison operators to sympy functions
        if isinstance(op, ast.Eq):
            return sp.Eq
        elif isinstance(op, ast.NotEq):
            return sp.Ne
        elif isinstance(op, ast.Lt):
            return sp.Lt
        elif isinstance(op, ast.LtE):
            return sp.Le
        elif isinstance(op, ast.Gt):
            return sp.Gt
        elif isinstance(op, ast.GtE):
            return sp.Ge
        return None

def apply_randomized_if_simplification(code_snippet):
    # Parse the code snippet into an AST
    tree = ast.parse(code_snippet)
    
    # Apply the transformation
    transformer = RandomizeIfSimplification()
    transformed_tree = transformer.visit(tree)
    
    # Convert the AST back to source code
    new_code_snippet = astor.to_source(transformed_tree).strip()
    
    return new_code_snippet