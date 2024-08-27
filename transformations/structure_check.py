import re

def contains_loops(code: str) -> bool:
    # Patterns to check for loops (for, while)
    loop_patterns = [
        r'\bfor\b',
        r'\bwhile\b'
    ]
    
    # Check if any loop pattern matches
    for pattern in loop_patterns:
        if re.search(pattern, code):
            return True
    
    return False

def contains_if_statements(code: str) -> bool:
    # Pattern to check for if statements
    if_pattern = r'\bif\b'
    
    # Check if the if pattern matches
    return bool(re.search(if_pattern, code))

def contains_math_operations(code: str) -> bool:
    # Patterns to check for math operations
    math_patterns = [
        r'\+',
        r'-',
        r'\*',
        r'/',
        r'%',
        r'\*\*',
        r'//'
    ]
    
    # Check if any math operation pattern matches
    for pattern in math_patterns:
        if re.search(pattern, code):
            return True
    
    return False