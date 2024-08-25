import random

VARIABLES = ["a", "b", "c", "d", "e"]
DIGITS = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
VARIABLE_SET = VARIABLES + DIGITS + ["_"]

def get_new_variable_name():
    # Ensure the first character is a letter or underscore
    first_char = random.choice(VARIABLES + ["_"])
    
    # Choose the rest of the characters from the allowed set
    length = random.randint(1, 4)  # Remaining length is 1 to 4
    remaining_chars = ''.join(random.choices(VARIABLE_SET, k=length))
    
    # Combine and return the variable name
    return first_char + remaining_chars

