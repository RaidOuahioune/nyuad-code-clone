import ast
import sympy as sp
from sympy import simplify_logic, And, Or, Not, Eq, Ne
from sympy.parsing.sympy_parser import parse_expr
import astor

# Dictionary to map variable names to SymPy symbols
var_map = {}

def ast_to_sympy(node):
    if isinstance(node, ast.Compare):
        left = ast_to_sympy(node.left)
        ops = node.ops
        comparators = [ast_to_sympy(cmp) for cmp in node.comparators]
        if len(ops) == 1 and left is not None and all(c is not None for c in comparators):
            op = ops[0]
            if isinstance(op, ast.Eq):
                return Eq(left, comparators[0])
            elif isinstance(op, ast.NotEq):
                return Ne(left, comparators[0])
            elif isinstance(op, ast.Lt):
                return left < comparators[0]
            elif isinstance(op, ast.LtE):
                return left <= comparators[0]
            elif isinstance(op, ast.Gt):
                return left > comparators[0]
            elif isinstance(op, ast.GtE):
                return left >= comparators[0]
      

    if isinstance(node, ast.BoolOp):
        op = node.op
        if isinstance(op, ast.And):
            return And(*[ast_to_sympy(value) for value in node.values])
        elif isinstance(op, ast.Or):
            return Or(*[ast_to_sympy(value) for value in node.values])


    if isinstance(node, ast.UnaryOp):
        op = node.op
        if isinstance(op, ast.Not):
            return Not(ast_to_sympy(node.operand))
    
           

    if isinstance(node, ast.Name):
        if node.id not in var_map:
            var_map[node.id] = sp.Symbol(node.id)
        return var_map[node.id]

    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return sp.Float(node.value) if isinstance(node.value, float) else sp.Integer(node.value)
        elif isinstance(node.value, str):
            return sp.Symbol(node.value)
        
           

    if isinstance(node, ast.BinOp):
        left = ast_to_sympy(node.left)
        right = ast_to_sympy(node.right)
        if isinstance(node.op, ast.Add):
            return left + right
        elif isinstance(node.op, ast.Sub):
            return left - right
        elif isinstance(node.op, ast.Mult):
            return left * right
        elif isinstance(node.op, ast.Div):
            return left / right
        elif isinstance(node.op, ast.Mod):
            return left % right
        
           

  

def sympy_to_python(expr):
    if isinstance(expr, And):
        return ' and '.join(f'({sympy_to_python(arg)})' for arg in expr.args)
    elif isinstance(expr, Or):
        return ' or '.join(f'({sympy_to_python(arg)})' for arg in expr.args)
    elif isinstance(expr, Not):
        return f'not {sympy_to_python(expr.args[0])}'
    elif isinstance(expr, Eq):
        return f'{sympy_to_python(expr.args[0])} == {sympy_to_python(expr.args[1])}'
    elif isinstance(expr, Ne):
        return f'{sympy_to_python(expr.args[0])} != {sympy_to_python(expr.args[1])}'
    elif isinstance(expr, (sp.Lt, sp.Le, sp.Ge, sp.Gt)):
        op_map = {
            sp.Lt: '<',
            sp.Le: '<=',
            sp.Ge: '>=',
            sp.Gt: '>',
        }
        op = op_map[type(expr)]
        return f'{sympy_to_python(expr.args[0])} {op} {sympy_to_python(expr.args[1])}'
    elif isinstance(expr, sp.Symbol):
        return expr.name
    elif isinstance(expr, (bool, int, float)):
        return str(expr)
    elif expr is None:
        return 'None'
    else:
        return str(expr)

def replace_condition(node, simplified_condition):
    simplified_condition_code = sympy_to_python(simplified_condition)
    try:
        node.test = ast.parse(f'({simplified_condition_code})').body[0].value
    except Exception as e:
        #print(f"Error replacing condition: {e}")
        #print(f"Simplified condition code: {simplified_condition_code}")
        pass


def simplify_conditions(code):
    global var_map
    var_map = {}  # Reset variable mapping
    tree = ast.parse(code)
    for node in ast.walk(tree):
        if isinstance(node, ast.If):
            condition = ast_to_sympy(node.test)
            if condition is not None:
                simplified_condition = simplify_logic(condition)
                replace_condition(node, simplified_condition)
            else:
                pass
         
    # Convert the modified AST back to code
    simplified_code = astor.to_source(tree)
    return simplified_code
