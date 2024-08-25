import ast
import astor
import random
from tinypy_generator import CodeGenerator

LEVELS = ["1.1", "1.2", "2.1", "2.2", "3.1", "3.2"]

class LoopTransformer(ast.NodeTransformer):
    def __init__(self):
        self.code_generator = CodeGenerator()

    def visit_For(self, node):
        # Decide randomly whether to use a for loop or convert it to a while loop
        if random.choice([True, False]):
            # Modify the for loop range and code inside
            node.iter = self._modify_range(node.iter)
            if random.choice([True, False]):
                node.body = self._generate_code_block()
            else:
                node.body = self._modify_loop_body(node.body)
        else:
            # Convert to a while loop
            while_loop = self._convert_to_while(node)
            if random.choice([True, False]):
                while_loop.body = self._generate_code_block()
            else:
                while_loop.body = self._modify_loop_body(while_loop.body)
            return while_loop
        
        return node

    def _modify_range(self, iter_node):
        # Modify the range of the for loop
        if isinstance(iter_node, ast.Call) and isinstance(iter_node.func, ast.Name) and iter_node.func.id == 'range':
            if len(iter_node.args) > 0:
                start = random.randint(0, 10)
                stop = random.randint(11, 20)
                step = random.randint(1, 3)
                iter_node.args = [ast.Constant(value=start), ast.Constant(value=stop), ast.Constant(value=step)]
        return iter_node

    def _convert_to_while(self, for_node):
        # Convert the for loop to a while loop
        start = ast.Constant(value=0)
        stop = ast.Constant(value=10)
        step = ast.Constant(value=1)
        index_var = for_node.target.id

        init_stmt = ast.Assign(targets=[ast.Name(id=index_var, ctx=ast.Store())], value=start)
        condition = ast.Compare(left=ast.Name(id=index_var, ctx=ast.Load()), ops=[ast.Lt()], comparators=[stop])
        increment_stmt = ast.Assign(targets=[ast.Name(id=index_var, ctx=ast.Store())], value=ast.BinOp(left=ast.Name(id=index_var, ctx=ast.Load()), op=ast.Add(), right=step))

        while_loop = ast.While(test=condition, body=for_node.body + [increment_stmt], orelse=[])

        return ast.Module(body=[init_stmt, while_loop])

    def _generate_code_block(self):
        # Generate a new code block to replace the existing loop body
        level = random.choice(LEVELS)
        root, random_code = self.code_generator.generate_program(level)
        return ast.parse(random_code).body

    def _modify_loop_body(self, body):
        # Modify the existing code block inside the loop
        if body:
            for stmt in body:
                if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
                    # Modify existing print statements
                    if isinstance(stmt.value.func, ast.Name) and stmt.value.func.id == 'print':
                        stmt.value = ast.Call(func=ast.Name(id='print', ctx=ast.Load()), args=[ast.Constant(value=random.randint(-10000,10000))], keywords=[])
                elif isinstance(stmt, ast.Expr):
                    # Add a random arithmetic operation
                    stmt.value = ast.BinOp(left=stmt.value, op=ast.Add(), right=ast.Constant(value=1))
        return body

def alter_loop_code(code):
    # Parse the code into an AST
    tree = ast.parse(code)
    # Apply the transformation
    transformer = LoopTransformer()
    transformed_tree = transformer.visit(tree)
    # Convert the AST back to code
    return astor.to_source(transformed_tree)