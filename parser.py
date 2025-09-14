# utils/parser.py
import re

def parse_numbers_safely(numbers_str):
    if not isinstance(numbers_str, str):
        return []
    return [int(num) for num in re.findall(r'\d+', numbers_str)]