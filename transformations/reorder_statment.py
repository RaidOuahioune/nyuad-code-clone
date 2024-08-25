import ast
import astor
import random
from collections import defaultdict

class ReorderStatements(ast.NodeTransformer):
    def __init__(self):
        self.variable_assignments = defaultdict(list)
        self.variable_usages = defaultdict(list)

    def visit_Assign(self, node):
        if isinstance(node.targets[0], ast.Name):
            var_name = node.targets[0].id
            self.variable_assignments[var_name].append(node)
        return self.generic_visit(node)

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load):
            self.variable_usages[node.id].append(node)
        return self.generic_visit(node)

    def reorder(self, code_snippet):
        # Parse code snippet into AST
        tree = ast.parse(code_snippet)
        
        # Collect all statements
        statements = [node for node in tree.body if isinstance(node, ast.stmt)]
        
        # Determine a safe ordering
        ordered_statements = self.safe_reorder_statements(statements)
        
        # Reconstruct the tree with reordered statements
        new_tree = ast.Module(body=ordered_statements)
        
        # Convert AST back to source code
        new_code_snippet = astor.to_source(new_tree).strip()
        
        return new_code_snippet

    def safe_reorder_statements(self, statements):
        # Map from statement to its dependencies
        dependencies = defaultdict(set)
        for stmt in statements:
            if isinstance(stmt, ast.Assign):
                for target in stmt.targets:
                    if isinstance(target, ast.Name):
                        var_name = target.id
                        if var_name in self.variable_usages:
                            for usage in self.variable_usages[var_name]:
                                dependencies[usage].add(stmt)
        
        # Perform a topological sort to maintain dependency order
        ordered_statements = []
        visited = set()
        
        def topological_sort(statement):
            if statement in visited:
                return
            visited.add(statement)
            for pred in dependencies[statement]:
                topological_sort(pred)
            ordered_statements.append(statement)
        
        for stmt in statements:
            topological_sort(stmt)
        
        return ordered_statements

# Example usage
def reorder_statements(code_snippet):
    reordering_transformer = ReorderStatements()
    return reordering_transformer.reorder(code_snippet)
