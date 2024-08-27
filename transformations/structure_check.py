import re
def contains_control_structures_or_math_operations(code: str) -> bool:
    # Define patterns to check for
    patterns = [
        r'\bif\b',
        r'\bwhile\b',
        r'\bfor\b',
        r'\+',
        r'-',
        r'\*',
        r'/',
        r'%',
        r'\*\*',
        r'//'
    ]
    
    # Check if any pattern matches
    for pattern in patterns:
        if re.search(pattern, code):
            return True
    
    return False
