import ast
import astor

from transformations.variables_vocab import get_new_variable_name

class ForToWhileTransformer(ast.NodeTransformer):
    def __init__(self):
        self.var_map = {}
        super().__init__()

    def get_variable(self, original):
        if original not in self.var_map:
            new_var = get_new_variable_name()
            while new_var in self.var_map.values():
                new_var = get_new_variable_name()
            self.var_map[original] = new_var
        return self.var_map[original]

    def visit_For(self, node):
        # Ensure that the loop is a for loop with range
        if isinstance(node.iter, ast.Call) and node.iter.func.id == 'range':
            # Extract range parameters
            range_args = node.iter.args
            start = astor.to_source(range_args[0]).strip().replace('(', '').replace(')', '')
            stop = astor.to_source(range_args[1]).strip().replace('(', '').replace(')', '')
            step = astor.to_source(range_args[2]).strip() if len(range_args) > 2 else '1'
            
            step = step.replace('(', '').replace(')', '')
            step = int(step) if step != '1' else 1  # Convert step to integer for use

            # Generate random variable names
            start_var = get_new_variable_name()
            stop_var = get_new_variable_name()
            step_var = get_new_variable_name()

            # Update the variable names in the loop body
            body = []
            for stmt in node.body:
                updated_stmt = self.visit(stmt)
                body.append(updated_stmt)

            # Replace loop variable with start_var in the loop body
            body = [ast.fix_missing_locations(
                        ast.NodeTransformer().visit(
                            ast.parse(astor.to_source(stmt).replace(node.target.id, start_var))
                        ).body[0]
                    ) for stmt in body]

            # Create a while loop equivalent with variable declarations
            while_loop = ast.While(
                test=ast.Compare(left=ast.Name(id=start_var, ctx=ast.Load()), ops=[ast.Lt()], comparators=[ast.Name(id=stop_var, ctx=ast.Load())]),
                body=body + [
                    ast.Assign(targets=[ast.Name(id=start_var, ctx=ast.Store())], value=ast.BinOp(left=ast.Name(id=start_var, ctx=ast.Load()), op=ast.Add(), right=ast.Constant(value=step)))
                ],
                orelse=[]
            )
            
            # Replace the for loop with the while loop
            return [ast.Assign(targets=[ast.Name(id=start_var, ctx=ast.Store())], value=ast.Constant(value=int(start))),
                    ast.Assign(targets=[ast.Name(id=stop_var, ctx=ast.Store())], value=ast.Constant(value=int(stop))),
                    ast.Assign(targets=[ast.Name(id=step_var, ctx=ast.Store())], value=ast.Constant(value=step)),
                    while_loop]
        return node

def for_to_while_loop(code):
    tree = ast.parse(code)
    transformer = ForToWhileTransformer()
    transformed_tree = transformer.visit(tree)
    return astor.to_source(transformed_tree)