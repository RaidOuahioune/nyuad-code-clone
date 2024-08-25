import random
import re
import ast
import astor
import traceback
import csv
from transformations.add_operations import add_operations
from transformations.remove_unused_variables import remove_unused_vars
from transformations.reorder_statment import reorder_statements
from transformations.remove_useless_operations import remove_useless_operations
from transformations.modfy_direction_assignments import apply_simplify_expression
from transformations.simplify_obvious_operations import simplify_obvious_operations
from transformations.simplify_if_statements import apply_randomized_if_simplification
from transformations.simplify_complex_if_statements import simplify_conditions
from transformations.for_to_while_loops import for_to_while_loop
# utils
from transformations.variables_vocab import get_new_variable_name
# non clones transformations
from transformations.non_clones.add_affecting_constants import add_non_equivalent_operations
from transformations.non_clones.alter_original_ifs import alter_original_if_block_code
from transformations.non_clones.blind_constants_changer import blind_constant_changer
from transformations.non_clones.change_loops import alter_loop_code
from transformations.non_clones.change_math_operators import change_math_operators

transformations = [
    remove_useless_operations,
    remove_unused_vars,
    apply_simplify_expression,
    add_operations,
    reorder_statements,
    simplify_obvious_operations,
    apply_randomized_if_simplification,
    simplify_conditions,
    for_to_while_loop
]

non_clone_transformations = [
    add_non_equivalent_operations,
    alter_original_if_block_code,
    blind_constant_changer,
    alter_loop_code,
    change_math_operators
]

transformation_names = [
    "Remove Useless Operations",
    "Remove Unused Variables",
    "Simplify Assignments",
    "Add Junk Operations",
    "Reorder Statements",
    "Simplify Obvious Operations",
    "Randomize If-Statement",
    "Simplify Complex Conditions",
    "Convert For to While Loop"
]

non_clone_transformation_names = [
    "Add Affecting Constants",
    "Alter Original If Block Code",
    "Blind Constant Changer",
    "Alter Loop Code",
    "Change Math Operators"
]

class CodeTransformer(ast.NodeTransformer):
    def __init__(self):
        super().__init__()
        self.variable_map = {}
        self.constant_map = {}
        self.in_simple_assignment = False  # To track if we're inside a simple assignment

    def visit_Assign(self, node):
        if isinstance(node.value, ast.Constant):
            self.in_simple_assignment = True
            for target in node.targets:
                if isinstance(target, ast.Name):
                    old_name = target.id
                    new_name = get_new_variable_name()
                    self.variable_map[old_name] = new_name
                    target.id = new_name

            old_value = node.value.value
            new_value = self.get_new_constant_value()
            self.constant_map[old_value] = new_value
            node.value.value = new_value
            self.in_simple_assignment = False

        return node

    def visit_Name(self, node):
        if node.id in self.variable_map:
            node.id = self.variable_map[node.id]
        return node

    def visit_Constant(self, node):
        if self.in_simple_assignment and node.value in self.constant_map:
            node.value = self.constant_map[node.value]
        return node

    def apply_self_transformations(self, source_code):
        tree = ast.parse(source_code)
        transformed_tree = self.visit(tree)
        transformed_code = astor.to_source(transformed_tree)

        # Ensure all variable occurrences are replaced consistently
        transformed_code = self.replace_all_variable_occurrences(transformed_code)
        return transformed_code

    def replace_all_variable_occurrences(self, code):
        for old_name, new_name in self.variable_map.items():
            pattern = rf'\b{re.escape(old_name)}\b'
            code = re.sub(pattern, new_name, code)
        return code

    def get_new_constant_value(self):
        return random.randint(0, 100)

    def apply_transformations(self, code_snippet, csv_file_path, log_file_path='failed_transformations.txt',is_clone=True):
        code = code_snippet

        # Apply self-transformations first
        code = self.apply_self_transformations(code)

        # Choose between clone and non-clone transformations
        if is_clone:
            selected_transformations = transformations
       
        else:
            selected_transformations = non_clone_transformations


        # Initialize a list to keep track of which transformations were applied
        transformation_record = [0] * len(selected_transformations)

        # Prepare to log failed transformations
        with open(log_file_path, 'a') as log_file:
            for i, transformation in enumerate(selected_transformations):
                random_uniform = random.uniform(0, 1)  # Use uniform distribution for probability
                if random_uniform >= 0.5:
                    try:
                        code = transformation(code)
                        transformation_record[i] = 1  # Mark the transformation as applied
                    except Exception as e:
                        # Write the failed code snippet and error message to the log file
                        stack_trace = traceback.format_exc()
                        log_file.write(f"Error in transformation:\n{code}\nException: {str(e)}\nStack Trace:\n{stack_trace}\n\n")

        # Write the transformation record to the CSV file
        with open(csv_file_path, 'a', newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(transformation_record)

        return code
